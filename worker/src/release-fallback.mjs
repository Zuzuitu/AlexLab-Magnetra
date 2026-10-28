import {queryTerms,relevantTitle,filterRelevance} from "./query-relevance.mjs";

// Rank only genuine source-owned records already received from an indexer.
// Never generate searches, substitute magnets, invent quality or silently
// upgrade a file. Movie title and year remain mandatory on every tier.
const RESOLUTIONS=Object.freeze([4320,2160,1440,1080,720,576,480,360]);
const DEPTH=/^(?:8bit|10bit|12bit)$/i;
const CODEC=/^(?:x265|h265|hevc|x264|h264|av1|xvid)$/i;
const RESOLUTION=/^(?:360p|480p|576p|720p|1080p|1440p|2160p|4320p|4k|8k)$/i;
const TECHNICAL=/^(?:360p|480p|576p|720p|1080p|1440p|2160p|4320p|4k|8k|x265|h265|hevc|x264|h264|av1|xvid|8bit|10bit|12bit|webrip|webdl|web|bluray|brrip|bdrip|hdr|dv|6ch|2ch|8ch|aac|ddp|ac3|dts|remux)$/i;
function words(s){return String(s??"").match(/[\p{L}\p{N}]+/gu)||[];}
function resolutionValue(t){
 if(!t)return null;
 if(/^4k$/i.test(t))return 2160;
 if(/^8k$/i.test(t))return 4320;
 const m=/^(360|480|576|720|1080|1440|2160|4320)p$/i.exec(t);
 return m?Number(m[1]):null;
}
function codecValue(t){
 if(!t)return null;
 const x=t.toLowerCase();
 if(x==="x265")return "x265";
 if(x==="h265"||x==="hevc")return "h265";
 if(x==="x264")return "x264";
 if(x==="h264")return "h264";
 return CODEC.test(x)?x:null;
}
function technicalFromName(s){
 // H.265/H-265 and H.264 are codec aliases in source-owned filenames.
 const normalized=String(s??"").replace(/\b([hx])[.\s-](264|265)\b/gi,"$1$2");
 const arr=words(normalized).map(x=>x.toLowerCase());
 const res=[...new Set(arr.map(resolutionValue).filter(Boolean))];
 const enc=[...new Set(arr.map(codecValue).filter(Boolean))];
 const bits=[...new Set(arr.filter(x=>DEPTH.test(x)))];
 const resolution=res.length===1?res[0]:null;
 let codec=null;
 // H.265/HEVC is compatible with x265; x265 is a particular encoder
 // and cannot be inferred just from an HEVC label.
 if(enc.includes("x265")&&!enc.some(x=>["x264","h264","av1","xvid"].includes(x)))codec="x265";
 else if(enc.includes("x264")&&!enc.some(x=>["x265","h265","av1","xvid"].includes(x)))codec="x264";
 else if(enc.length&&enc.every(x=>["h265","x265"].includes(x)))codec="h265";
 else if(enc.length&&enc.every(x=>["h264","x264"].includes(x)))codec="h264";
 else if(enc.length===1)codec=enc[0];
 return {resolution,codec,bitDepth:bits.length===1?bits[0]:null};
}
export function releaseFallbackIntent(original,plan){
 const full=String(original||"").trim();
 if(!plan?.broadened)return null;
 const parts=words(full);
 const first=parts.findIndex((p,i)=>i>=2&&TECHNICAL.test(p));
 if(first<0)return null;
 const tail=parts.slice(first);
 const meta=technicalFromName(tail.join(" "));
 const final=tail.at(-1);
 const last=/^(?:mkv|mp4|avi|mov|torrent)$/i.test(final||"")?tail.at(-2):final;
 const requestedGroup=last&&!TECHNICAL.test(last)&&/^[a-z][a-z0-9]{1,19}$/i.test(last)?last:null;
 if(!meta.resolution&&!meta.codec&&!meta.bitDepth)return null;
 return {
  titleQuery:plan.searchedAs,
  technicalTerms:[meta.resolution?meta.resolution+"p":null,meta.codec,meta.bitDepth].filter(Boolean),
  requestedGroup,requestedResolution:meta.resolution,
  requestedCodec:meta.codec,requestedBitDepth:meta.bitDepth
 };
}
function resolutionRank(requested,actual){
 if(!requested)return actual===null?1:0;
 if(actual===requested)return 0;
 if(actual===null)return 90;
 // User prefers the next lower resolution before an unnecessarily larger
 // file, e.g. 1080p -> 720p -> 480p -> 2160p.
 const lower=RESOLUTIONS.filter(n=>n<requested).sort((a,b)=>b-a);
 const higher=RESOLUTIONS.filter(n=>n>requested).sort((a,b)=>a-b);
 const li=lower.indexOf(actual),hi=higher.indexOf(actual);
 if(li>=0)return li+1;
 if(hi>=0)return lower.length+hi+1;
 return 89;
}
function codecRank(requested,actual){
 if(!requested)return actual?0:4;
 if(actual===requested)return 0;
 if(requested==="x265"&&actual==="h265")return 1;
 if(requested==="x264"&&actual==="h264")return 1;
 if(["x265","h265"].includes(requested)&&["x264","h264"].includes(actual))return 2;
 if(["x264","h264"].includes(requested)&&["x265","h265"].includes(actual))return 2;
 return actual?3:4;
}
function depthRank(requested,actual){
 if(!requested)return actual?0:2;
 if(actual===requested)return 0;
 return actual?1:2;
}
// Curated full-release searches require the complete original source filename,
// not just the unordered presence of every token. Container extensions are
// transport details and do not change the named release.
function releaseNameTokens(value){
 const withoutExtension=String(value??"").trim().replace(/\.(?:mkv|mp4|avi|mov|torrent)$/i,"");
 return words(withoutExtension.normalize("NFKD").replace(/[\u0300-\u036f]/g,""))
  .map(token=>token.toLowerCase());
}
export function isLiteralReleaseMatch(actual,requested){
 const a=releaseNameTokens(actual),b=releaseNameTokens(requested);
 return a.length>0&&a.length===b.length&&a.every((term,index)=>term===b[index]);
}
function groupRank(group,name){
 if(!group)return 0;
 const literal=String(name||"").trim();
 if(new RegExp("(?:-|[\\s._])"+group+"(?:\\.[a-z0-9]+)?$","i").test(literal))return 0;
 return 1;
}
function describeDifferences(intent,meta,name,original){
 const changes=[];
 if(intent.requestedResolution&&meta.resolution!==intent.requestedResolution)
  changes.push("resolution");
 if(intent.requestedCodec&&meta.codec!==intent.requestedCodec)
  changes.push("codec");
 if(intent.requestedBitDepth&&meta.bitDepth!==intent.requestedBitDepth)
  changes.push("bitDepth");
 if(intent.requestedGroup&&groupRank(intent.requestedGroup,name)!==0)
  changes.push("group");
 // Technical equivalence alone does not prove identical release naming.
 if(!changes.length&&!isLiteralReleaseMatch(name,original))changes.push("release");
 return changes;
}
export function rankReleaseAlternative(item,original,plan){
 const intent=releaseFallbackIntent(original,plan);
 if(!intent||!relevantTitle(intent.titleQuery,item?.name))return null;
 const meta=technicalFromName(item.name);
 // Never label an entirely unclassified title as a technical replacement.
 if(!meta.resolution&&!meta.codec)return null;
 const resolution=resolutionRank(intent.requestedResolution,meta.resolution);
 const codec=codecRank(intent.requestedCodec,meta.codec);
 const bitDepth=depthRank(intent.requestedBitDepth,meta.bitDepth);
 const group=groupRank(intent.requestedGroup,item.name);
 // The category order is intentional: SAME RESOLUTION with x264 always
 // outranks 720p x265 when the request was 1080p x265.
 const fallbackRank=resolution*1000+codec*100+bitDepth*10+group;
 return {fallbackRank,fallbackDifferences:describeDifferences(intent,meta,item.name,original),
   fallbackActual:{resolution:meta.resolution?meta.resolution+"p":null,
    codec:meta.codec,bitDepth:meta.bitDepth},
   fallbackGroupMatches:group===0};
}
export function matchesQualityFallback(item,original,plan){
 return rankReleaseAlternative(item,original,plan)!==null;
}
export function partitionReleases(found,original,plan){
 const {matches:strictRelevant}=filterRelevance(found,original);
 const intent=releaseFallbackIntent(original,plan);
 // For real full-release searches, strict token presence alone is not exact:
 // a REPACK, an extra suffix or reordered release terms is an alternative.
 // A .mkv extension only in the query does not disqualify the same source
 // name without extension. Non-release and hidden-provider logic stay intact.
 const exact=intent?found.filter(row=>isLiteralReleaseMatch(row?.name,original)):strictRelevant;
 const ids=new Set(exact);
 const alternatives=[];
 if(intent)for(const row of found){
  if(ids.has(row))continue;
  const rank=rankReleaseAlternative(row,original,plan);
  if(rank)alternatives.push({...row,...rank});
 }
 alternatives.sort((a,b)=>a.fallbackRank-b.fallbackRank);
 return {exact,alternatives,
  excluded:found.length-exact.length-alternatives.length,
  criteria:intent?.technicalTerms||[],requestedGroup:intent?.requestedGroup||null
 };
}
