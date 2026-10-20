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
