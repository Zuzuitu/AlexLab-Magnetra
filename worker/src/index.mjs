import {PROVIDERS, PROVIDER_MAP} from "./catalog.mjs";
import {hasAdapter,searchProvider} from "./providers.mjs";

const DEFAULT_IDS=["knaben","torrentscsv","nyaasi","internetarchive"];
// Exact endpoint allowlist: never forward to an arbitrary hostname or URL.
const COMPANION_RELAY_ORIGIN="https://flud-remote.alexlab.media";
const CATEGORIES=new Set(["all","movies","series","apps","games","books","music","anime","porn","other"]);
const JSON_HEADERS={"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"};
const json=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:JSON_HEADERS});
function error(message,status=400){return json({error:message},status);}
async function safeBody(request,max=15000){
  if(Number(request.headers.get("content-length")||0)>max)throw Error("request too large");
  const t=await request.text();
  if(t.length>max)throw Error("request too large");
  return JSON.parse(t);
}
async function getSearch(url) {
 const q=url.searchParams.get("q")||"";
 if(q.trim().length<2||q.length>180)return error("Query must contain 2–180 characters.");
 const category=url.searchParams.get("category")||"all";
 if(!CATEGORIES.has(category))return error("Invalid category.");
 const ids=(url.searchParams.get("providers")||DEFAULT_IDS.join(",")).split(",").filter(Boolean);
 if(ids.length>46||ids.length===0||new Set(ids).size!==ids.length)return error("Choose 1–46 distinct providers.");
 if(ids.some(id=>!PROVIDER_MAP.has(id)))return error("Unknown provider.");
 if(ids.some(id=>!hasAdapter(id)))return error("One or more selected providers are not ported yet.");
 const results=[],errors=[],stats=[];
 // Bounded concurrency reduces load on providers and keeps resource consumption predictable.
 for(let i=0;i<ids.length;i+=3){
   const batch=await Promise.all(ids.slice(i,i+3).map(async id=>{
     try {
       const found=await searchProvider(id,q,category);
       return {provider:id,results:found,count:found.length};
     } catch(e){
       return {provider:id,results:[],count:0,error:String(e?.message||e).slice(0,180)};
     }
   }));
   for(const item of batch){
     stats.push({provider:item.provider,count:item.count,ok:!item.error});
     if(item.error)errors.push({provider:item.provider,error:item.error});
     results.push(...item.results);
   }
 }
 // Preserve source identities and identical hashes across providers for traceability.
 return json({query:q,category,results,stats,errors,total:results.length});
}
function checkSameOrigin(request){
 const origin=request.headers.get("origin");
 return origin===null||origin===new URL(request.url).origin;
}
function validCompanion(body){
 const deviceId=typeof body.deviceId==="string"?body.deviceId.trim():"";
 const token=typeof body.token==="string"?body.token.trim():"";
 if(!/^[A-Za-z0-9_-]{16,128}$/.test(deviceId))return {error:"Invalid Companion device ID."};
 if(token.length<20||token.length>512||/[\r\n]/.test(token))return {error:"Invalid Companion Remote token."};
 return {deviceId,token};
}
async function companion(request,action){
 if(!checkSameOrigin(request))return error("Cross-origin submission not permitted.",403);
 let body;
 try {body=await safeBody(request);}catch{return error("Invalid JSON request.");}
 const v=validCompanion(body);
 if(v.error)return error(v.error);
 if(action==="magnet"){
   if(typeof body.magnet!=="string"||!body.magnet.toLowerCase().startsWith("magnet:?")||body.magnet.length>12000)return error("Invalid magnet.");
   if(body.autoStart!==true && body.autoStart!==false)return error("Invalid autoStart setting.");
 }
 const id=v.deviceId;
 const url=COMPANION_RELAY_ORIGIN+"/api/v1/device/"+encodeURIComponent(id)+"/"+action;
 const payload=action==="magnet"?JSON.stringify({
   magnet:body.magnet,autoStart:body.autoStart,
   requestId:typeof body.requestId==="string"&&/^[A-Za-z0-9._:-]{8,100}$/.test(body.requestId)?body.requestId:crypto.randomUUID()
 }):JSON.stringify({});
 let upstream;
 try{
   upstream=await fetch(url,{
     method:action==="status"?"GET":"POST",
     headers:{"authorization":"Bearer "+v.token,"content-type":"application/json","accept":"application/json"},
     ...(action==="status"?{}:{body:payload}),
     signal:AbortSignal.timeout(12000),
     redirect:"error"
   });
 }catch{return error("Companion remote relay is unavailable.",502);}
 let data;
 try {data=await upstream.json();}catch{return error("Companion relay returned an invalid response.",502);}
 // Never echo the bearer token to frontend or log it.
 return json(data,upstream.status);
}
export default {
 async fetch(request,env){
   const url=new URL(request.url);
   if(url.pathname==="/api/health" && request.method==="GET")return json({ok:true,product:"AlexLab Magnetra",ported:PROVIDERS.filter(x=>x.ported).length,total:PROVIDERS.length});
   if(url.pathname==="/api/providers" && request.method==="GET")return json({providers:PROVIDERS});
   if(url.pathname==="/api/search" && request.method==="GET")return getSearch(url);
   if(url.pathname==="/api/companion/magnet" && request.method==="POST")return companion(request,"magnet");
   if(url.pathname==="/api/companion/status" && request.method==="POST")return companion(request,"status");
   if(url.pathname.startsWith("/api/"))return error("Not found.",404);
   if(request.method==="GET" && env?.ASSETS) return env.ASSETS.fetch(request);
   return error("Not found.",404);
 }
};
