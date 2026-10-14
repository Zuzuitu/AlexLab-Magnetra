// EZTV-only optional residential egress. Does not reuse or modify BTDigg.
// If secret is absent, the established direct Cloudflare EZTV adapter remains.
// Fixed HTTPS origins only, no browser-controlled proxy target or credentials.
export const EZTV_GATEWAY_ORIGIN="https://eztv-rock64.alexlab.media";
const EZTV_API="https://eztvx.to/api/get-torrents";
const TVMAZE_ORIGIN="https://api.tvmaze.com";

export function rock64EZTVFetcher(env,transport=fetch){
 const secret=env?.EZTV_GATEWAY_TOKEN;
 if(secret==null||secret==="")return null;
 if(typeof secret!=="string"||!(/^[A-Za-z0-9_-]{48,256}$/).test(secret))
  throw Error("EZTV Rock64 gateway is misconfigured.");
 return async function getEZTVSource(sourceUrl,options={}){
  const source=new URL(sourceUrl);
  // Leave TVmaze name-to-IMDb lookups alone. Never route through residential
  // gateway, and preserve their existing timeout/headers/redirect guards.
  if(source.origin===TVMAZE_ORIGIN&&source.pathname==="/search/shows" &&
     source.searchParams.getAll("q").length===1&&
     [...source.searchParams.keys()].every(k=>k==="q")&&
     !source.username&&!source.password&&!source.hash&&!source.port)
   return transport(sourceUrl,options);
  if(source.origin!==new URL(EZTV_API).origin||
     source.pathname!==new URL(EZTV_API).pathname||
     source.username||source.password||source.hash||source.port||
     [...source.searchParams.keys()].some(x=>!["imdb_id","limit","page"].includes(x))||
     source.searchParams.getAll("imdb_id").length!==1||
     source.searchParams.getAll("limit").length!==1||
     source.searchParams.getAll("page").length!==1||
     source.searchParams.get("limit")!=="100"||
     source.searchParams.get("page")!=="1"||
     !/^[0-9]{5,12}$/.test(source.searchParams.get("imdb_id")||""))
   throw Error("EZTV gateway rejects non-canonical source URL.");
  const gateway=new URL("/v1/torrents",EZTV_GATEWAY_ORIGIN);
  gateway.searchParams.set("imdb_id",source.searchParams.get("imdb_id"));
  let response;
  try{
   response=await transport(gateway.href,{
    method:"GET",redirect:"manual",signal:AbortSignal.timeout(14000),
    headers:{"authorization":"Bearer "+secret,"accept":"application/json"}
   });
  }catch(err){
   const message=String(err?.message||"");
   if(err?.name==="TimeoutError"||err?.name==="AbortError"||/timed? ?out|abort/i.test(message))
    throw Error("EZTV Rock64 tunnel timed out.");
   throw Error("EZTV Rock64 tunnel transport failed.");
  }
  if(response.status>=300&&response.status<400)
   throw Error("EZTV Rock64 tunnel redirect refused.");
  if(response.status===401)throw Error("EZTV Rock64 gateway authorization failed.");
  if(response.status===429)throw Error("EZTV source/gateway HTTP 429.");
  if(response.status===504)throw Error("EZTV Rock64 upstream timed out.");
  if(response.status===403)throw Error("EZTV upstream HTTP 403 via Rock64.");
  if(!response.ok)throw Error("EZTV Rock64 gateway HTTP "+response.status);
  if(!/application\/json/i.test(response.headers.get("content-type")||""))
   throw Error("EZTV gateway returned non-JSON data.");
  if(Number(response.headers.get("content-length")||0)>1000000)
   throw Error("EZTV gateway response too large.");
  return response;
 };
}
