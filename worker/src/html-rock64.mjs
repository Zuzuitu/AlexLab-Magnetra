// Opt-in hardcoded fixed-origin HTML transport through the existing 8798 hub.
// No arbitrary-URL proxy, open redirects, client-provided destinations or
// generic credentials. Without the private Worker secret, legacy direct
// transports remain selected (fail-closed).
import {LEGACY_SPECS} from "./legacy-specs.mjs";

export const HTML_GATEWAY_ORIGIN="https://magnetra-rock64.alexlab.media";
const SOURCES=Object.freeze({
 oxtorrent:Object.freeze({host:"https://www.oxtorrent.co",searchPrefix:"/recherche/",searchSuffix:""}),
 torrent9:Object.freeze({host:"https://www7.torrent9.to",searchPrefix:"/search_torrent/",searchSuffix:".html"})
});
const DETAIL=/^\/torrent\/[0-9]{1,12}\/[a-zA-Z0-9][a-zA-Z0-9._-]{0,180}$/;
const SECRET=/^[A-Za-z0-9_-]{48,256}$/;

export function routeHtmlRequest(provider,sourceUrl){
 const spec=SOURCES[provider];
 if(!spec||LEGACY_SPECS[provider]?.host!==spec.host)throw Error("Unsupported source HTML gateway.");
 let source;
 try{source=new URL(sourceUrl);}catch{throw Error("Malformed source HTML URL.");}
 if(source.origin!==spec.host||source.username||source.password||source.hash||
    source.port||source.href.length>750||source.protocol!=="https:")
  throw Error("HTML source outside provider allowlist.");
 const endpoint=new URL("/v1/"+provider+"/html",HTML_GATEWAY_ORIGIN);
 if(!source.search){
  const path=source.pathname;
  if(DETAIL.test(path)){
   endpoint.searchParams.set("mode","detail");
   endpoint.searchParams.set("path",path);
   return endpoint.href;
  }
  if(path.startsWith(spec.searchPrefix)&&path.endsWith(spec.searchSuffix)){
   const encoded=path.slice(spec.searchPrefix.length,
    spec.searchSuffix ? -spec.searchSuffix.length : undefined);
   let decoded;
   try{decoded=decodeURIComponent(encoded);}catch{throw Error("Invalid HTML query encoding.");}
   if(decoded.length>=2&&decoded.length<=100&&decoded.trim()===decoded&&
      !/[/\\?#\x00-\x1f\x7f]/.test(decoded)&&
      encodeURIComponent(decoded)===encoded){
    endpoint.searchParams.set("mode","search");
    endpoint.searchParams.set("q",decoded);
    return endpoint.href;
   }
  }
 }
 throw Error("Noncanonical source HTML route refused.");
}

/** Only activate on a valid protected server-side secret, never client state. */
export function rock64HtmlFetcher(provider,env,transport=fetch){
 if(!Object.hasOwn(SOURCES,provider))return null;
 const secret=env?.MAGNETRA_GATEWAY_TOKEN;
 if(secret==null||secret==="")return null;
 if(typeof secret!=="string"||!SECRET.test(secret))
  throw Error("Magnetra shared gateway is misconfigured.");
 return async function authenticatedHtml(sourceUrl,options={}){
  if(options.method&&options.method!=="GET")throw Error("Source HTML gateway allows GET only.");
  if(options.body!=null)throw Error("Source HTML gateway rejects request bodies.");
  const gateway=routeHtmlRequest(provider,sourceUrl);
  let response;
  try{
   response=await transport(gateway,{
    method:"GET",redirect:"manual",
    headers:{"authorization":"Bearer "+secret,"accept":"text/html"},
    signal:options.signal||AbortSignal.timeout(12000)
   });
  }catch(err){
   if(err?.name==="AbortError"||err?.name==="TimeoutError")
    throw Error("Source HTML gateway timed out.");
   throw Error("Source HTML gateway transport failed.");
  }
  if(response.status>=300&&response.status<400)
   throw Error("Source HTML gateway redirect refused.");
  if(response.status===401)throw Error("Source HTML gateway authorization failed.");
  if(response.status===429)throw Error("Source HTTP 429.");
  if(response.status===403)throw Error("Source HTTP 403.");
  if(response.status===504)throw Error("Source HTML gateway timeout (HTTP 504).");
  if(!response.ok)throw Error("Source HTML gateway HTTP "+response.status);
  if(!/text\/html/i.test(response.headers.get("content-type")||""))
   throw Error("Source HTML gateway returned non-HTML data.");
  if(Number(response.headers.get("content-length")||0)>256000)
   throw Error("Source HTML gateway response too large.");
  return response;
 };
}
