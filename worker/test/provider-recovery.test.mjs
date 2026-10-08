import {readFileSync} from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import {directSearchUrl,classifyProviderError} from "../src/provider-recovery.mjs";
import worker from "../src/index.mjs";

test("BTDigg browser search link is exact-source HTTPS and preserves query",()=>{
 const url=directSearchUrl("btdigg","linux & ubuntu");
 assert.equal(url,"https://btdig.com/search?q=linux%20%26%20ubuntu");
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
});
test("BTDigg HTTP 429 is reported honestly with a direct first-party search recovery link",async()=>{
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
  assert.equal(data.errors[0].openUrl,"https://btdig.com/search?q=ubuntu");
  assert.deepEqual(data.results,[],"Never impersonate another source's results as BTDigg");
 }finally{globalThis.fetch=original;}
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
  assert.equal(data.errors[0].openUrl,"https://btdig.com/search?q=ubuntu");
 }finally{globalThis.fetch=original;}
});

test("manual browser fallback has an explicit user-gesture clipboard action and paste form",()=>{
 const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
 const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
 for(const id of ["pasteMagnetButton","manualMagnetDialog","manualMagnetForm","manualMagnetInput"])
   assert.ok(html.includes('id="'+id+'"'),id+" missing from PWA");
 assert.ok(app.includes('$("pasteMagnetButton").addEventListener("click"'));
 assert.ok(app.includes("navigator.clipboard.readText()"));
 assert.ok(app.includes('openDialog("manualMagnetDialog")'));
 assert.ok(app.includes('sendMagnet({magnet}'),"Manual magnets must reuse existing Companion dispatch");
});
