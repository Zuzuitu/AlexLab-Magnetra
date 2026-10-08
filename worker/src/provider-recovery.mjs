import {PROVIDER_MAP} from "./catalog.mjs";
import {HTML_PROVIDER_SPECS} from "./html-adapters.mjs";
import {LEGACY_SPECS,legacySearchUrl} from "./legacy-specs.mjs";

/** Fixed-provider URLs only. Never reflect arbitrary remote Location headers. */
export function directSearchUrl(id,query){
 const p=PROVIDER_MAP.get(id);
 if(!p||typeof query!=="string"||query.trim().length<2||query.length>180)return null;
 let candidate=null,origin=null;
 if(Object.hasOwn(HTML_PROVIDER_SPECS,id)){
  const spec=HTML_PROVIDER_SPECS[id];
  candidate=spec.search(query.trim());origin=spec.host;
 }else if(Object.hasOwn(LEGACY_SPECS,id)){
  const spec=LEGACY_SPECS[id];
  if(spec.method==="POST_FORM"||spec.method==="POST_JSON_HTML")return null;
  candidate=legacySearchUrl(spec,query.trim());origin=spec.host;
 }else if(id==="nyaasi"||id==="sukebeinyaa"){
  origin=id==="nyaasi"?"https://nyaa.si":"https://sukebei.nyaa.si";
  candidate=origin+"/?f=0&c=0_0&q="+encodeURIComponent(query.trim());
 }else{
  // Not every API-backed source has an equivalent public browser search UI.
  // A source homepage is intentionally not presented as a query URL.
  return null;
 }
 try{
  const target=new URL(candidate),expected=new URL(origin);
  if(target.origin!==expected.origin||target.protocol!=="https:"||target.username||
    target.password||target.hash||target.href.length>1500)return null;
  return target.toString();
 }catch{return null;}
}
export function classifyProviderError(err){
 const raw=String(err?.message||err||"").slice(0,180);
 if(/abort|timed? ?out|timeout/i.test(raw))return {code:"TIMEOUT",message:"The provider did not respond in time.",retryable:false};
 if(/HTTP 429|too many requests/i.test(raw))return {code:"RATE_LIMIT",message:"Provider rate-limited this connection.",retryable:false};
 if(/cf-mitigated|cloudflare challenge|challenge requires|anti-bot challenge/i.test(raw))
  return {code:"CHALLENGE",message:"Provider requires browser verification.",retryable:false};
 if(/HTTP 403|HTTP 401/i.test(raw))return {code:"ACCESS_DENIED",message:"Provider rejected requests from this server.",retryable:false};
 if(/redirect/i.test(raw))return {code:"REDIRECT_BLOCKED",message:"Provider redirected outside its approved domain.",retryable:false};
 if(/HTTP (520|521|522|523|524|530|502|503)/i.test(raw))return {code:"UPSTREAM_ERROR",message:"Provider server is unavailable or returned an upstream error.",retryable:false};
 return {code:"PROVIDER_ERROR",message:"This provider could not complete the search.",retryable:false};
}
