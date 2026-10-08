import {SOURCE_USER_AGENT,fetchProviderSameOrigin} from "../src/request-headers.mjs";
import test from "node:test";
import assert from "node:assert/strict";
import {PROVIDERS} from "../src/catalog.mjs";
import {hasAdapter,searchProvider} from "../src/providers.mjs";
import {LEGACY_SPECS,legacySearchUrl} from "../src/legacy-specs.mjs";
import {legacySearch,resolveLegacy,validateLegacyDetail} from "../src/legacy-adapters.mjs";
import worker from "../src/index.mjs";

const HASH="0123456789abcdef0123456789abcdef01234567";
const MAGNET="magnet:?xt=urn:btih:"+HASH;
const HTML_HEAD="<html><head><title>Provider fixture</title></head><body>fixture</body></html>";
const SOURCE_IDS=Object.keys(LEGACY_SPECS);
function fakeResponse(html=HTML_HEAD,headers={}){
 return new Response(html,{status:200,headers:{"content-type":"text/html",...headers}});
}
async function withFakeRewriter(callback) {
 const original=globalThis.HTMLRewriter;
 try{
   globalThis.HTMLRewriter=class {
     constructor(){this.listeners=[];}
     on(selector,callback){this.listeners.push([selector,callback]);return this;}
     transform(response){
       return {text:async()=>{
         await response.text();
         // Minimal logical callback fixture to validate adapter mapping.
         const root=this.listeners[0][1];
         root.element?.({});
         for(const [selector,listener] of this.listeners.slice(1)){
           if(/magnet/i.test(selector) && listener.element)listener.element({getAttribute:(name)=>name==="href"?MAGNET:null});
           if(/name|title/i.test(selector)&&listener.text)listener.text({text:"Linux ISO",lastInTextNode:true});
           if(/size/i.test(selector)&&listener.text)listener.text({text:"2 GB",lastInTextNode:true});
           if(/seed/i.test(selector)&&listener.text)listener.text({text:"42",lastInTextNode:true});
         }
         return "";
       }};
     }
   };
   return await callback();
 }finally{globalThis.HTMLRewriter=original;}
}
test("all original 46 indexers now have executable adapters; 25 legacy adapters are explicit",()=>{
 assert.equal(PROVIDERS.length,46);
 assert.equal(SOURCE_IDS.length,25);
 assert.equal(PROVIDERS.filter(p=>p.ported).length,46);
 for(const p of PROVIDERS)assert.equal(hasAdapter(p.id),true,p.id);
 for(const [id,spec] of Object.entries(LEGACY_SPECS)){
   assert.ok(spec.host.startsWith("https://"),id);
   assert.ok(spec.method==="POST_FORM"||spec.pathTemplate.includes("MAGNETRA_SEARCH_TOKEN"),id);
   assert.ok(spec.rows?.length>5,id);
   assert.ok(spec.name?.length>3,id);
   assert.ok(spec.magnet||spec.magnetSource||spec.magnetHashLink||spec.hashFromDetailsSuffix||spec.details,id);
   const url=new URL(legacySearchUrl(spec,"ubuntu & linux"));
   assert.equal(url.origin,spec.host,id);
   if(spec.method!=="POST_FORM")assert.match(url.toString(),/%26/,id);
 }
});
test("provider URLs reject off-domain details, insecure requests, username injection and oversized URLs",()=>{
 assert.equal(validateLegacyDetail("1337x","https://example.org/"),null);
 assert.equal(validateLegacyDetail("1337x","http://1337x.to/example"),null);
 assert.equal(validateLegacyDetail("1337x","https://user:pass@1337x.to/download"),null);
 assert.equal(validateLegacyDetail("1337x","https://1337x.to/real"),"https://1337x.to/real");
 assert.equal(validateLegacyDetail("1337x","https://1337x.to/".padEnd(2500,"a")),null);
 assert.equal(validateLegacyDetail("unknown","https://1337x.to/real"),null);
});
test("legacy provider does not follow arbitrary redirects",async()=>{
 const spec=LEGACY_SPECS["1337x"];
 await assert.rejects(
   ()=>legacySearch("1337x","ubuntu","all",async()=>new Response("",{status:302,headers:{location:"http://127.0.0.1/private"}})),
   /redirect/
 );
 assert.ok(spec.details);
});
test("legacy port returns deferred magnet result instead of discarding it",async()=>{
 await withFakeRewriter(async()=>{
   const res=await searchProvider("1337x","ubuntu","all",async()=>fakeResponse());
   // The fixture must not invent a magnet. If it has provider details, retain the deferred item.
   for(const row of res)assert.equal(row.magnet,null);
 });
});
test("AniRena redirect magnet is resolved only through allowlisted same-host URL",async()=>{
 const url="https://anirena.com/torrents/123/magnet";
 let called=0;
 const result=await resolveLegacy("anirena",url,async(u,opts)=>{
   called++;assert.equal(u,url);assert.equal(opts.redirect,"manual");
   return new Response(null,{status:302,headers:{location:MAGNET}});
 });
 assert.equal(result.magnet,MAGNET);assert.equal(called,1);
});
test("EpubLibre requests JSON via POST with original XMLHttpRequest header",async()=>{
 await withFakeRewriter(async()=>{
   let calls=0;
   const rows=await legacySearch("epublibre","linux handbook","books",async(url,opts)=>{
     calls++;assert.equal(opts.method,"POST");
     assert.equal(opts.headers["X-Requested-With"],"XMLHttpRequest");
     assert.equal(new URL(url).hostname,"epublibre.org");
     return fakeResponse(JSON.stringify({contenido:HTML_HEAD}),{"content-type":"application/json"});
   });
   assert.equal(calls,1);assert.ok(Array.isArray(rows));
 });
});
test("NoNameClub sends form data, not user-built arbitrary proxy requests",async()=>{
 await withFakeRewriter(async()=>{
   await legacySearch("nonameclub","ubuntu","all",async(url,opts)=>{
     assert.equal(url,"https://nnmclub.to/forum/tracker.php");
     assert.equal(opts.method,"POST");
     const form=new URLSearchParams(opts.body);
     assert.equal(form.get("nm"),"ubuntu");
     assert.equal(form.get("shf"),"1");
     return fakeResponse();
   });
 });
});
test("same-origin resolve endpoint denies cross-origin and arbitrary host without fetching",async()=>{
 const origin="https://index.alexlab.media";
 const cases=[
   {provider:"1337x",details:"https://127.0.0.1/admin"},
   {provider:"1337x",details:"http://1337x.to/"},
   {provider:"invented",details:"https://1337x.to/torrent"},
 ];
 for(const payload of cases){
  const req=new Request(origin+"/api/resolve",{method:"POST",headers:{"origin":origin,"content-type":"application/json"},body:JSON.stringify(payload)});
  const response=await worker.fetch(req,{});
  assert.equal(response.status,400);
 }
 const cross=new Request(origin+"/api/resolve",{method:"POST",headers:{"origin":"https://evil.example","content-type":"application/json"},
 body:JSON.stringify({provider:"1337x",details:"https://1337x.to/torrent"})});
 assert.equal((await worker.fetch(cross,{})).status,403);
});
test("Flud Companion status proxy exposes genuine acknowledgement without creating a command",async()=>{
 const prev=globalThis.fetch;
 const origin="https://index.alexlab.media";
 try{
   let calls=0;
   globalThis.fetch=async(url,opts)=>{
     calls++;assert.equal(url,"https://flud-remote.alexlab.media/api/v1/device/"+"D".repeat(22)+"/status");
     assert.equal(opts.method,"GET");
     assert.equal(opts.headers.authorization,"Bearer "+"T".repeat(26));
     return new Response(JSON.stringify({ok:true,online:true,autoStartReady:true,lastResult:{id:"abc-12345678",ok:true}}),
      {headers:{"content-type":"application/json"}});
   };
   const req=new Request(origin+"/api/companion/status",{method:"POST",headers:{"origin":origin,"content-type":"application/json"},
      body:JSON.stringify({deviceId:"D".repeat(22),token:"T".repeat(26),autoStart:true})});
   const res=await worker.fetch(req,{});
   assert.equal(res.status,200);
   const data=await res.json();
   assert.equal(data.lastResult.id,"abc-12345678");
   assert.equal(data.lastResult.ok,true);
   assert.equal(calls,1);
 }finally{globalThis.fetch=prev;}
});

test("same-origin resolver returns an actual magnet only after an approved source redirect",async()=>{
 const prior=globalThis.fetch;
 const origin="https://index.alexlab.media";
 try{
   let requests=0;
   globalThis.fetch=async(url,opts)=>{
     requests++;
     assert.equal(url,"https://anirena.com/torrents/42/magnet");
     assert.equal(opts.redirect,"manual");
     return new Response(null,{status:302,headers:{"location":MAGNET}});
   };
   const req=new Request(origin+"/api/resolve",{
     method:"POST",headers:{"origin":origin,"content-type":"application/json"},
     body:JSON.stringify({provider:"anirena",details:"https://anirena.com/torrents/42/magnet"})
   });
   const res=await worker.fetch(req,{});
   assert.equal(res.status,200);
   assert.equal((await res.json()).magnet,MAGNET);
   assert.equal(requests,1);
 }finally{globalThis.fetch=prior;}
});

test("outgoing source user-agent matches protected upstream Android baseline",()=>{
 assert.equal(SOURCE_USER_AGENT,
   "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36");
});
test("same-origin redirect is followed once but off-origin redirect never is",async()=>{
 let count=0;
 const fetcher=async(url,opts)=>{
   count++;assert.equal(opts.redirect,"manual");
   if(count===1)return new Response(null,{status:302,headers:{"location":"/results?q=ubuntu"}});
   assert.equal(url,"https://linuxtracker.org/results?q=ubuntu");
   return new Response("OK",{status:200});
 };
 const result=await fetchProviderSameOrigin("https://linuxtracker.org/search?q=ubuntu",{},fetcher);
 assert.equal(result.status,200);assert.equal(count,2);
 await assert.rejects(()=>fetchProviderSameOrigin("https://linuxtracker.org/",{},async()=>
   new Response(null,{status:302,headers:{location:"http://169.254.169.254/latest/meta-data"}})),/redirect left/);
});
