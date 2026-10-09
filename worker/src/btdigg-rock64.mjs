// Optional, fixed-origin Rock64 residential egress for BTDigg ONLY.
// When the secret is absent, the existing Cloudflare direct adapter is unchanged.
// No browser-supplied URL, open proxy, external redirects, or secret in public assets.
export const BTDIGG_GATEWAY_ORIGIN = "https://btdigg-rock64.alexlab.media";

export function rock64BTDiggFetcher(env, transport=fetch) {
 const secret=env?.BTDIGG_GATEWAY_TOKEN;
 if(secret==null||secret==="")return null;
 if(typeof secret!=="string"||!(/^[A-Za-z0-9_-]{48,256}$/).test(secret))
  throw Error("BTDigg Rock64 gateway is misconfigured.");
 return async function fetchActualBTDigg(sourceUrl,_options={}){
  const source=new URL(sourceUrl);
  if(source.origin!=="https://btdig.com"||source.pathname!=="/search"||
     source.username||source.password||source.hash||source.port||
     [...source.searchParams.keys()].some(x=>x!=="q")||
     source.searchParams.getAll("q").length!==1)
    throw Error("BTDigg Rock64 only accepts the canonical BTDigg search URL.");
  const q=source.searchParams.get("q");
  if(!q||q.trim().length<2||q.length>180)throw Error("Invalid BTDigg search query.");
  const gateway=new URL("/v1/search",BTDIGG_GATEWAY_ORIGIN);
  gateway.searchParams.set("q",q);
  let response;
  try{
   response=await transport(gateway.toString(),{
    method:"GET",redirect:"manual",signal:AbortSignal.timeout(10000),
    headers:{"authorization":"Bearer "+secret,"accept":"text/html"}
   });
  }catch{throw Error("BTDigg Rock64 gateway is unreachable.");}
  if(response.status>=300&&response.status<400)
   throw Error("BTDigg gateway redirect refused.");
  if(response.status===401||response.status===403)
   throw Error("BTDigg Rock64 gateway authorization failed.");
  if(response.status===429)throw Error("BTDigg gateway/provider HTTP 429 (rate limited).");
  if(!response.ok)throw Error("BTDigg Rock64 gateway HTTP "+response.status);
  if(!/text\/html/i.test(response.headers.get("content-type")||""))
   throw Error("BTDigg gateway returned non-HTML data.");
  if(Number(response.headers.get("content-length")||0)>3_000_000)
   throw Error("BTDigg gateway page too large.");
  // The existing Android-parity HTMLRewriter adapter will validate source
  // selectors, challenge markup, magnets, details URLs and row count.
  return response;
 };
}
