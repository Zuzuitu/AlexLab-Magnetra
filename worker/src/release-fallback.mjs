import {queryTerms,relevantTitle,filterRelevance} from "./query-relevance.mjs";

// A group suffix (e.g. -PSA) is optional only AFTER all selected sources
// lack a complete exact source-title match. The user-supplied resolution,
// codec and bit depth remain hard constraints. This is not a guessed release,
// automatic source retry, or query expansion across providers.
const RESOLUTION=/^(?:360p|480p|576p|720p|1080p|1440p|2160p|4320p|4k|8k)$/i;
const CODEC=/^(?:x265|h265|hevc|x264|h264|av1|xvid)$/i;
const DEPTH=/^(?:8bit|10bit|12bit)$/i;
const TECHNICAL=/^(?:360p|480p|576p|720p|1080p|1440p|2160p|4320p|4k|8k|x265|h265|hevc|x264|h264|av1|xvid|8bit|10bit|12bit|webrip|webdl|web|bluray|brrip|bdrip|hdr|dv|6ch|2ch|8ch|aac|ddp|ac3|dts|remux)$/i;

export function releaseFallbackIntent(original,plan){
 const full=String(original||"").trim();
 if(!plan?.broadened)return null;
 const parts=full.match(/[\p{L}\p{N}]+/gu)||[];
 const firstTechnical=parts.findIndex((part,index)=>index>=2&&TECHNICAL.test(part));
 if(firstTechnical<0)return null;
 const tail=parts.slice(firstTechnical);
 const last=tail.at(-1);
 if(!last||TECHNICAL.test(last)||!/^[a-z][a-z0-9]{1,19}$/i.test(last))return null;
 // Keep only technical terms supplied by the user; never infer x265 or 10bit.
 const resolutions=tail.filter(x=>RESOLUTION.test(x));
 const codecs=tail.filter(x=>CODEC.test(x));
 const depths=tail.filter(x=>DEPTH.test(x));
 // Prefer an explicit encoder x265 over the redundant umbrella codec HEVC.
 // WEBRip and 6CH are not requirements for fallback alternatives.
 const codec=codecs.find(x=>/^x(?:264|265)$/i.test(x))||codecs[0];
 const requirements=[resolutions[0],codec,depths[0]].filter(Boolean).map(x=>x.toLowerCase());
 if(!requirements.length)return null;
 return {
  titleQuery:plan.searchedAs,
  technicalTerms:requirements,
  requestedGroup:last,
 };
}

export function matchesQualityFallback(item,original,plan){
 const intent=releaseFallbackIntent(original,plan);
 if(!intent)return false;
 const name=item?.name;
 if(!name||!relevantTitle(intent.titleQuery,name))return false;
 const terms=new Set(queryTerms(name));
 return intent.technicalTerms.every(term=>terms.has(term));
}

export function partitionReleases(found,original,plan){
 const {matches:exact}=filterRelevance(found,original);
 const exactRows=new Set(exact);
 const intent=releaseFallbackIntent(original,plan);
 const alternatives=intent?found.filter(row=>!exactRows.has(row)&&
  matchesQualityFallback(row,original,plan)):[];
 return {
  exact,alternatives,
  excluded:found.length-exact.length-alternatives.length,
  criteria:intent?.technicalTerms||[],
  requestedGroup:intent?.requestedGroup||null
 };
}
