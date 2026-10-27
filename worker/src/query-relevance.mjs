// Query/title relevance gate shared by ALL 46 original indexers.
// A remote source may ignore the query or return trending/loosely related rows.
// This gate never changes provenance, invents magnets, calls providers or hides errors.
const STOPWORDS=new Set(["the","a","an","of"]);
const LOOKUP_ID=/^(?:tt[0-9]{5,12}|[a-f0-9]{40}|[a-z2-7]{32})$/i;
function words(value){
 return (String(value??"").normalize("NFKD")
  .replace(/[\u0300-\u036f]/g,"").toLowerCase()
  .match(/[\p{L}\p{N}]+/gu)||[]);
}
export function queryTerms(query){
 const tokens=words(query);
 const significant=tokens.filter(t=>!STOPWORDS.has(t));
 return [...new Set(significant.length?significant:tokens)];
}
// A complete release filename is not a viable provider-wide literal query:
// different indexers tokenize quality/audio/group metadata differently. Issue
// ONE query per indexer for the title (+ year/episode), never a retry/broad
// internet search, and keep the original query for UI transparency.
// Only strip an unambiguous technical suffix after two meaningful title words.
const TECHNICAL_SUFFIX=/^(?:2160p|1440p|1080p|720p|480p|360p|4k|8bit|10bit|12bit|webrip|webdl|web|bluray|brrip|bdrip|dvdrip|hdtv|hdrip|remux|hdr|hdr10|hdr10p|dv|dolbyvision|hevc|av1|x265|h265|x264|h264|xvid|ddp|ddp51|ac3|dts|aac|6ch|2ch|8ch)$/i;
export function planSearchQuery(input){
 const original=String(input??"").trim();
 if(!original||LOOKUP_ID.test(original))return {searchedAs:original,broadened:false};
 const tokens=original.match(/[\p{L}\p{N}]+/gu)||[];
 const firstTech=tokens.findIndex((token,i)=>i>=2&&TECHNICAL_SUFFIX.test(token));
 if(firstTech<0)return {searchedAs:original,broadened:false};
 const core=tokens.slice(0,firstTech);
 if(core.filter(token=>!STOPWORDS.has(token.toLowerCase())).length<2)
  return {searchedAs:original,broadened:false};
 const searchedAs=core.join(" ");
 return {searchedAs,broadened:searchedAs!==original};
}
export function relevantTitle(query,title){
 const raw=String(query??"").trim();
 if(!raw||!String(title??"").trim())return false;
 // The genuine EZTV adapter searches an IMDb ID and the title carries the
 // episode name, not that ID; exact hash lookups also need this exception.
 if(LOOKUP_ID.test(raw))return true;
 const expected=queryTerms(raw);
 if(!expected.length)return false;
 const actual=new Set(words(title));
 return expected.every(term=>actual.has(term));
}
export function filterRelevance(results,query){
 const matches=[];
 for(const result of results){
  if(relevantTitle(query,result?.name))matches.push(result);
 }
 return {matches,excluded:results.length-matches.length};
}
