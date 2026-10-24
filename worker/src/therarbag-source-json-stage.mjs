// Diagnostic-only candidate. One exact original TheRarBg JSON fetch.
// Output is a finite error enum, never raw HTML, headers, URI, title or hash.
// Intentionally NOT a source workaround or runtime resolver change.
import {SOURCE_HEADERS} from "./request-headers.mjs";

const ORIGINAL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
const URL=ORIGINAL+"?format=json";
export const ORIGINAL_JSON_EGRESS_MARKER="THERARBAG_SOURCE_JSON_STAGE_V2";
export async function diagnoseOriginalTheRarBgJson(fetcher=fetch){
 let response;
 try{
   response=await fetcher(URL,{
    method:"GET",redirect:"manual",
    signal:AbortSignal.timeout(11000),
    headers:{...SOURCE_HEADERS,accept:"application/json"}
   });
 }catch(e){
   return e?.name==="TimeoutError"||e?.name==="AbortError"?"FETCH_TIMEOUT":"FETCH_NETWORK";
 }
 const status=response.status;
 if(status>=300&&status<400)return "HTTP_REDIRECT";
 if(status!==200){
   if([401,403,404,429,500,502,503,504].includes(status))return "SOURCE_HTTP_"+status;
   return "SOURCE_HTTP_OTHER";
 }
 if(response.headers.get("cf-mitigated")==="challenge")return "SOURCE_CHALLENGE";
 const ctype=(response.headers.get("content-type")||"").split(";")[0].trim().toLowerCase();
 if(ctype==="text/html"||ctype==="application/xhtml+xml")return "HTML_NOT_JSON";
 if(ctype!=="application/json")return "UNEXPECTED_CONTENT_TYPE";
 const length=Number(response.headers.get("content-length")||"0");
 if(!Number.isFinite(length)||length>3_000_000)return "OVERSIZE";
 let raw;
 try{raw=await response.text();}catch{return "BODY_READ_FAILED";}
 if(raw.length>3_000_000)return "OVERSIZE";
 let parsed;
 try{parsed=JSON.parse(raw);}catch{return "INVALID_JSON";}
 const entity=parsed?.data;
 if(!entity||typeof entity!=="object"||Array.isArray(entity))return "MISSING_DATA_OBJECT";
 if(typeof entity.info_hash!=="string"||!/^[a-f0-9]{40}$/i.test(entity.info_hash))
   return "MISSING_OR_INVALID_INFO_HASH";
 return "SOURCE_JSON_VALID";
}
