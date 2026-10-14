#!/usr/bin/env node
// One-shot metadata-only EZTV upstream / production probe.
// No magnet URLs, torrent names, hashes, service credentials or response bodies logged.
const urls = [
  ["eztv-imdb", "https://eztvx.to/api/get-torrents?imdb_id=460681&limit=2&page=1"],
  ["eztv-recent", "https://eztvx.to/api/get-torrents?limit=2&page=1"],
  ["production-imdb", "https://index.alexlab.media/api/search?q=tt0460681&providers=eztvx"],
  ["production-title", "https://index.alexlab.media/api/search?q=Supernatural&providers=eztvx"]
];
const rootType=x=>x===null?"null":Array.isArray(x)?"array":typeof x;
const has=(x,k)=>x&&typeof x==="object"&&Object.hasOwn(x,k);
const compact=object=>{
 if(!object||typeof object!=="object")return {root:rootType(object)};
 if(has(object,"stats")&&has(object,"errors")){
   const stats=Array.isArray(object.stats)?object.stats:[];
   const errors=Array.isArray(object.errors)?object.errors:[];
   return {root:rootType(object),resultsCount:Array.isArray(object.results)?object.results.length:null,
     stats:stats.map(x=>({provider:String(x?.provider||"").slice(0,24),ok:x?.ok,count:x?.count})),
     errorCodes:errors.map(x=>String(x?.code||"").slice(0,36)),
     errorCategories:errors.map(x=>String(x?.error||"").slice(0,80))};
 }
 const known=["imdb_id","torrents","torrents_count","limit","page","error","errors","message","status","success","data"];
 const rows=Array.isArray(object.torrents)?object.torrents:null;
 const first=rows?.[0];
 return {root:rootType(object),recognizedKeys:known.filter(k=>has(object,k)),
   unrecognizedKeyCount:Object.keys(object).filter(k=>!known.includes(k)).length,
   torrentsType:has(object,"torrents")?rootType(object.torrents):"missing",
   torrentsCount:rows?.length??null,
   imdbEchoMatches:has(object,"imdb_id")?String(object.imdb_id).replace(/^tt/i,"")==="460681":null,
   sampleFields:first&&typeof first==="object"
     ?["title","filename","hash","magnet_url","imdb_id","seeds","peers","size_bytes"].filter(k=>has(first,k)):[],
   sampleImdbMatches:has(first,"imdb_id")?String(first.imdb_id).replace(/^tt/i,"")==="460681":null,
   apiErrorPresent:has(object,"error")||has(object,"errors")||has(object,"message")
 };
};
for(const [name,url] of urls){
 const out={probe:name};
 try{
  const res=await fetch(url,{headers:{"accept":"application/json"},
    redirect:"manual",signal:AbortSignal.timeout(9000)});
  out.httpStatus=res.status;
  out.contentType=(res.headers.get("content-type")||"").split(";")[0].slice(0,60);
  if(Number(res.headers.get("content-length")||0)>1000000){out.body="too-large";console.log(JSON.stringify(out));continue;}
  const body=await res.text();
  if(body.length>1000000){out.body="too-large";console.log(JSON.stringify(out));continue;}
  try{out.shape=compact(JSON.parse(body));}
  catch{out.body="not-json";}
 }catch(err){out.networkError=err?.name==="TimeoutError"?"timeout":"fetch-failed";}
 console.log(JSON.stringify(out));
}
