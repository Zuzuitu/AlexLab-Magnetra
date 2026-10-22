import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import Worker from "../src/index.mjs";
import {classifyTheRarBgResolveError} from "../src/therarbag-resolve-errors.mjs";

const HASH="c".repeat(40);
const detail="https://therarbg.com/post-detail/test-entry/public-domain-sample/";
const request=()=>new Request("https://index.alexlab.media/api/resolve",{
 method:"POST",headers:{"origin":"https://index.alexlab.media","content-type":"application/json"},
 body:JSON.stringify({provider:"therarbag",details:detail})
});
async function withSource(fetcher,callback){
 const originalFetch=globalThis.fetch,rewriter=globalThis.HTMLRewriter;
 class FakeHTMLRewriter{on(){return this}transform(response){return response}}
 globalThis.fetch=fetcher;
 globalThis.HTMLRewriter=FakeHTMLRewriter;
 try{return await callback();}
 finally{globalThis.fetch=originalFetch;if(rewriter===undefined)delete globalThis.HTMLRewriter;else globalThis.HTMLRewriter=rewriter;}
}

test("finite sanitized classifications do not include untrusted source text",()=>{
 for(const [message,code] of [
  ["provider HTTP 403","SOURCE_HTTP_403"],["provider HTTP 502","SOURCE_HTTP_502"],
  ["provider HTTP 418","SOURCE_HTTP_OTHER"],
  ["provider details page contains no supported magnet link","DETAIL_NO_BTIH"],
  ["provider challenge requires a browser session","SOURCE_CHALLENGE"],
  ["provider page too large","SOURCE_PAGE_TOO_LARGE"],
  ["Provider redirected repeatedly; browser challenge may be required","SOURCE_REDIRECT"],
  ["The operation was aborted","SOURCE_TIMEOUT"],
  ["fetch failed","SOURCE_NETWORK"],
  ["unexpected detail token password=sensitive","RESOLVE_UNKNOWN"]
 ]){
  const out=classifyTheRarBgResolveError(new Error(message));
  assert.equal(out,code,message);
  assert.match(out,/^[A-Za-z0-9_]{3,40}$/);
  assert.doesNotMatch(out,/password|https|magnet/i);
 }
});
test("real source HTTP 403 remains 502 transport wrapper with safe source code",async()=>{
 await withSource(async()=>new Response("private upstream body; must never echo",{status:403}),async()=>{
  const response=await Worker.fetch(request(),{});
  assert.equal(response.status,502);
  const payload=await response.json();
  assert.equal(payload.code,"SOURCE_HTTP_403");
  assert.equal(payload.error,"TheRarBg magnet could not be resolved.");
  assert.doesNotMatch(JSON.stringify(payload),/private upstream|post-detail/);
 });
});
test("source HTTP 200 missing original source hash gets distinct parser category",async()=>{
 await withSource(async()=>new Response("<html><main>No source-owned info hash</main></html>",{status:200}),async()=>{
  const response=await Worker.fetch(request(),{});
  assert.equal(response.status,502);
  assert.equal((await response.json()).code,"DETAIL_NO_BTIH");
 });
});
test("source HTML with unique own BTIH still works",async()=>{
 await withSource(async()=>new Response("<html><main>Info Hash: "+HASH+"</main></html>",{status:200}),async()=>{
  const response=await Worker.fetch(request(),{});
  assert.equal(response.status,200);
  const value=await response.json();
  assert.equal(value.magnet,"magnet:?xt=urn:btih:"+HASH);
 });
});
test("other provider endpoint behavior is not globally reclassified",async()=>{
 await withSource(async()=>new Response("Upstream", {status:502}),async()=>{
  const resp=await Worker.fetch(new Request("https://index.alexlab.media/api/resolve",{
   method:"POST",headers:{"origin":"https://index.alexlab.media","content-type":"application/json"},
   body:JSON.stringify({provider:"audiobookbay",details:"https://audiobookbay.lu/post/public-domain-test/"})
  }),{});
  const body=await resp.json();
  assert.equal(resp.status,502);
  assert.equal(body.code,undefined);
 });
});
test("RO/IT UI displays stage-specific information and does not leak raw errors",()=>{
 const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
 const i18n=readFileSync(new URL("../../web/i18n.js",import.meta.url),"utf8");
 assert.match(app,/failure\.magnetraCode=data\.code/);
 assert.match(app,/SOURCE_HTTP_403:"TheRarBg refused/);
 assert.match(app,/DETAIL_NO_BTIH:"TheRarBg details page/);
 assert.match(app,/function magnetFailureText\(item,error\)/);
 assert.match(i18n,/TheRarBg a refuzat accesul la detalii/);
 assert.match(i18n,/TheRarBg ha rifiutato la pagina dei dettagli/);
 assert.match(i18n,/Cererea Magnetra a fost blocată/);
 assert.match(i18n,/La richiesta Magnetra è stata bloccata/);
});
