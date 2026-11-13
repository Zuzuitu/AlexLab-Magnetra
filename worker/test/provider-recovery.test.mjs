import {readFileSync} from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import {directSearchUrl,classifyProviderError} from "../src/provider-recovery.mjs";
import worker from "../src/index.mjs";

test("BTDigg has no retired manual browser recovery URL",()=>{
 assert.equal(directSearchUrl("btdigg","linux & ubuntu"),null);
 assert.equal(directSearchUrl("btdigg","x"),null);
 assert.equal(directSearchUrl("invented-provider","ubuntu"),null);
 assert.equal(directSearchUrl("btdigg","u".repeat(181)),null);
});
test("other provider direct links stay bound to provider-owned canonical HTTPS origins",()=>{
 for(const id of ["anirena","bitsearch","limetorrents","torrentdownloadinfo","nyaasi","sukebeinyaa"]){
   const link=directSearchUrl(id,"linux & ubuntu");
   assert.ok(link,id+" should have a direct source URL");
   assert.equal(new URL(link).protocol,"https:");
   assert.ok(link.includes("%26"),id);
 }
 assert.equal(directSearchUrl("torrentscsv","ubuntu"),null,"Do not invent a public search URL for API-backed sources");
 assert.equal(directSearchUrl("nonameclub","ubuntu"),null,"Form-only searches must not be misrepresented as bookmarkable GET URLs");
 assert.equal(directSearchUrl("epublibre","ubuntu"),null,"POST-JSON searches cannot be reproduced by a browser GET");

});
test("provider error categories distinguish timeouts, rate limits, access denial and blocked redirects",()=>{
 assert.equal(classifyProviderError("The operation was aborted due to timeout").code,"TIMEOUT");
 assert.equal(classifyProviderError("provider HTTP 429").code,"RATE_LIMIT");
 assert.equal(classifyProviderError("provider HTTP 403").code,"ACCESS_DENIED");
 assert.equal(classifyProviderError("provider anti-bot challenge").code,"CHALLENGE");
 assert.equal(classifyProviderError("Provider redirect left the approved origin").code,"REDIRECT_BLOCKED");
 assert.equal(classifyProviderError("provider HTTP 530").code,"UPSTREAM_ERROR");
 assert.equal(classifyProviderError("BTDigg Rock64 tunnel timed out (16-second request).").code,"BTDIGG_TUNNEL_TIMEOUT");
 assert.equal(classifyProviderError("BTDigg Rock64 source timed out (HTTP 504).").code,"BTDIGG_SOURCE_TIMEOUT");
 assert.equal(classifyProviderError("BTDigg Rock64 tunnel Cloudflare 1042.").code,"BTDIGG_TUNNEL_1042");
 assert.equal(classifyProviderError("BTDigg Rock64 gateway transport failed.").code,"BTDIGG_TUNNEL_ERROR");
 assert.equal(classifyProviderError("BTDigg Rock64 local pacing.").code,"BTDIGG_LOCAL_PACING");
 assert.match(classifyProviderError("BTDigg Rock64 local pacing.").message,/gateway is spacing requests/);
});
test("provider timeouts have explicit recovery metadata, not opaque failure text",async()=>{
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async()=>{throw new DOMException("The operation was aborted due to timeout","TimeoutError")};
  const res=await worker.fetch(new Request("https://index.alexlab.media/api/search?q=ubuntu&providers=btdigg"),{});
  const data=await res.json();
  assert.equal(data.errors.length,1);
  assert.equal(data.errors[0].code,"TIMEOUT");
  assert.ok(data.errors[0].message.includes("respond"));
  assert.equal(data.errors[0].openUrl,null);
 }finally{globalThis.fetch=original;}
});

test("generic manual magnet action for Flud remains (not BTDigg browser importing)",()=>{
 const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
 const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
 for(const id of ["pasteMagnetButton","manualMagnetDialog","manualMagnetForm","manualMagnetInput"])
   assert.ok(html.includes('id="'+id+'"'),id+" missing from PWA");
 assert.ok(app.includes('$("pasteMagnetButton").addEventListener("click"'));
 assert.ok(app.includes("navigator.clipboard.readText()"));
 assert.ok(app.includes('openDialog("manualMagnetDialog")'));
 assert.ok(app.includes('sendMagnet({magnet}'),"Manual magnets must reuse existing Companion dispatch");
});

test("PWA online assets are refreshed network-first but authenticated APIs never cached",()=>{
 const sw=readFileSync(new URL("../../web/sw.js",import.meta.url),"utf8");
 assert.ok(sw.includes('CACHE="alexlab-magnetra-v15"'));
 assert.ok(sw.includes('new Set(["/app.js","/i18n.js","/styles.css","/manifest.webmanifest"])'));
 assert.ok(sw.includes('fetch(event.request,{cache:"no-store"})'));
 assert.ok(sw.includes('url.pathname.startsWith("/api/")'));
 assert.ok(sw.includes('event.request.method!=="GET"'));
});

test("public BTDigg API distinguishes upstream HTTP 504 from tunnel fetch timeout",async()=>{
 const original=globalThis.fetch;
 const endpoint=new Request("https://index.alexlab.media/api/search?q=supernatural&providers=btdigg");
 const cases=[
  {
   code:"BTDIGG_SOURCE_TIMEOUT",
   mocked:async()=>new Response('{"error":"BTDigg request timed out"}',{status:504,headers:{"content-type":"application/json"}})
  },
  {
   code:"BTDIGG_TUNNEL_TIMEOUT",
   mocked:async()=>{throw new DOMException("The operation was aborted due to timeout","TimeoutError");}
  }
 ];
 try{
  for(const {code,mocked} of cases){
   let calls=0;
   globalThis.fetch=async()=>{calls++;return mocked()};
   const res=await worker.fetch(endpoint,{BTDIGG_GATEWAY_TOKEN:"x".repeat(64)});
   assert.equal(res.status,200);
   const payload=await res.json();
   assert.equal(payload.total,0);
   assert.equal(payload.errors?.length,1);
   assert.equal(payload.errors[0].provider,"btdigg");
   assert.equal(payload.errors[0].code,code);
   assert.equal(payload.errors[0].retryable,false);
   assert.equal(payload.errors[0].openUrl,null);
   assert.equal(payload.stats[0].ok,false);
   assert.equal(calls,1,"must not retry BTDigg automatically");
   assert.ok(payload.errors[0].message);
  }
 }finally{globalThis.fetch=original;}
});


test("one local BTDigg pacing response never blocks independent TPB title-ranked alternatives",async()=>{
 const previous=globalThis.fetch;
 const exact="The Dog Stars 2026 1080p 10bit WEBRip 6CH x265 HEVC PSA";
 const calls=[];
 try{
  globalThis.fetch=async(url,options)=>{
   const target=new URL(String(url));calls.push(target.origin);
   if(target.origin==="https://btdigg-rock64.alexlab.media"){
    assert.equal(options.headers.authorization,"Bearer "+"p".repeat(64));
    assert.equal(target.pathname,"/v1/search");
    return new Response("",{status:429,headers:{
     "retry-after":"5","x-magnetra-btdigg-429-scope":"local-pacing"
    }});
   }
   assert.equal(target.origin,"https://apibay.org");
   assert.equal(target.searchParams.get("q"),"The Dog Stars 2026");
   return new Response(JSON.stringify([
    {id:"1",name:"The Dog Stars 2026 720p x265 PSA",info_hash:"b".repeat(40),size:"1234",seeders:"5",leechers:"2"},
    {id:"2",name:"The Dog Stars 2026 1080p x264 PSA",info_hash:"c".repeat(40),size:"2345",seeders:"3",leechers:"1"}
   ]),{headers:{"content-type":"application/json"}});
  };
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(exact)+
    "&category=movies&providers=btdigg,thepiratebay";
  const response=await worker.fetch(new Request(url),{BTDIGG_GATEWAY_TOKEN:"p".repeat(64)});
  assert.equal(response.status,200);
  const data=await response.json();
  assert.deepEqual(calls.sort(),["https://apibay.org","https://btdigg-rock64.alexlab.media"]);
  assert.equal(data.errors.length,1);
  assert.equal(data.errors[0].provider,"btdigg");
  assert.equal(data.errors[0].code,"BTDIGG_LOCAL_PACING");
  assert.equal(data.errors[0].retryable,false);
  assert.equal(data.errors[0].openUrl,null);
  assert.equal(data.stats.find(x=>x.provider==="btdigg").ok,false);
  assert.equal(data.stats.find(x=>x.provider==="thepiratebay").alternativeCount,2);
  assert.equal(data.total,0,"No synthetic exact release on local pacing");
  assert.equal(data.alternativeTotal,2);
  assert.deepEqual(data.alternatives.map(x=>x.provider),["thepiratebay","thepiratebay"]);
  assert.ok(data.alternatives.every(x=>x.releaseMatch==="quality-alternative"));
  assert.ok(data.alternatives[0].fallbackRank<data.alternatives[1].fallbackRank,
   "1080p x264 must outrank 720p x265 without another source request");
 }finally{globalThis.fetch=previous;}
});

// A provider 429 deliberately latches the shared Worker-isolate cache.
// Exercise 503/504 mocks before this terminal refusal scenario.
test("BTDigg HTTP 429 is reported without prompting the discarded manual browser workflow",async()=>{
 const original=globalThis.fetch;
 try{
  globalThis.fetch=async()=>new Response("Rate limited",{status:429});
  const res=await worker.fetch(new Request("https://index.alexlab.media/api/search?q=ubuntu&providers=btdigg"),{});
  assert.equal(res.status,200);
  const data=await res.json();
  assert.equal(data.total,0);
  assert.equal(data.errors.length,1);
  assert.equal(data.errors[0].provider,"btdigg");
  assert.equal(data.errors[0].code,"RATE_LIMIT");
  assert.equal(data.errors[0].retryable,false);
  assert.equal(data.errors[0].openUrl,null);
  assert.deepEqual(data.results,[],"Never impersonate another source's results as BTDigg");
 }finally{globalThis.fetch=original;}
});
test("PWA uses translated categorical BTDigg errors without exposing developer codes",()=>{
 const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
 assert.match(app,/const genericError=\(failure\)=>/);
 assert.match(app,/RATE_LIMIT|429/);
 assert.match(app,/Provider timed out/);
 assert.match(app,/failure\.provider==="btdigg"/);
 assert.doesNotMatch(app,/diagnostic-code|Diagnostic: /);
});
