// Optional, fixed-origin Rock64 residential egress for BTDigg ONLY.
// When the secret is absent, the existing Cloudflare direct adapter is unchanged.
// No browser-supplied URL, open proxy, external redirects, or secret in public assets.
export const BTDIGG_GATEWAY_ORIGIN = "https://btdigg-rock64.alexlab.media";

// Rock64 emits decimal seconds on its authenticated 429 responses. Do not
// trust arbitrary Retry-After strings, follow redirects or create retry timers.
export function boundedBTDiggRetryAfterMs(value) {
 if(typeof value!=="string"||!(/^[1-9][0-9]{0,5}$/).test(value))return null;
 const seconds=Number(value);
 return Number.isSafeInteger(seconds)?Math.min(30*60_000,seconds*1000):null;
}

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
    method:"GET",redirect:"manual",signal:AbortSignal.timeout(16000),
    headers:{"authorization":"Bearer "+secret,"accept":"text/html"}
   });
  }catch(e){
   // Do not publish arbitrary transport exception text (it can contain URLs).
   // Distinguish the main failure modes without retries or weakening tunnel auth.
   const detail=String(e?.message||"");
   if(e?.name==="TimeoutError"||e?.name==="AbortError"||
      /timed? ?out|timeout|aborted/i.test(detail))
    throw Error("BTDigg Rock64 tunnel timed out (16-second request).");
   if(/(?:^|\D)1042(?:\D|$)/.test(detail))
    throw Error("BTDigg Rock64 tunnel Cloudflare 1042.");
   throw Error("BTDigg Rock64 gateway transport failed.");
  }
  if(response.status>=300&&response.status<400)
   throw Error("BTDigg gateway redirect refused.");
  if(response.status===401||response.status===403)
   throw Error("BTDigg Rock64 gateway authorization failed.");
  if(response.status===429){
   // The newer private gateway distinguishes an origin denial from a
   // five-second local pacing rejection. A legacy gateway has no scope:
   // fail closed and keep the existing conservative source-429 pause.
   const scope=response.headers.get("x-magnetra-btdigg-429-scope");
   if(scope==="local-pacing")
    throw Error("BTDigg Rock64 local pacing.");
   const err=Error("BTDigg gateway/provider HTTP 429 (rate limited).");
   err.retryAfterMs=boundedBTDiggRetryAfterMs(
    response.headers.get("retry-after"));
   throw err;
  }
  if(response.status===504)throw Error("BTDigg Rock64 source timed out (HTTP 504).");
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
