import test from "node:test";
import assert from "node:assert/strict";
import Worker from "../src/index.mjs";

const DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
const HASH="a".repeat(40);
const JSON_URL=DETAIL+"?format=json";
const PROBE={"x-magnetra-resolve-diagnostic":"owner-opt-in-20261024-v1"};
const html="<html><main><div>Magnet Download</div><p>Info Hash: unavailable</p></main></html>";
const request=({probe=false,provider="therarbag",details=DETAIL}={})=>new Request(
 "https://index.alexlab.media/api/resolve",{
  method:"POST",
  headers:{origin:"https://index.alexlab.media","content-type":"application/json",...(probe?PROBE:{})},
  body:JSON.stringify({provider,details})
 });
async function withSource(fetcher,callback){
 const oldFetch=globalThis.fetch,oldRewriter=globalThis.HTMLRewriter;
 // HTMLRewriter is mocked only here, never used as evidence of actual workerd behavior.
 class FakeHTMLRewriter{on(){return this}transform(response){return response}}
 globalThis.fetch=fetcher;
 globalThis.HTMLRewriter=FakeHTMLRewriter;
 try{return await callback()}
 finally{
  globalThis.fetch=oldFetch;
  if(oldRewriter===undefined)delete globalThis.HTMLRewriter;
  else globalThis.HTMLRewriter=oldRewriter;
 }
}
test("opt-in TheRarBg failure classifies HTML and rejected original JSON, without raw data",async()=>{
 const calls=[];
 await withSource(async(url,opts)=>{
  calls.push(url);
  assert.equal(opts.redirect,"manual");
  if(url===DETAIL)return new Response(html,{status:200});
  if(url===JSON_URL)return new Response("upstream secret 12345",{status:503});
  throw Error("unexpected source URL");
 },async()=>{
  const response=await Worker.fetch(request({probe:true}),{});
  assert.equal(response.status,502);
  const body=await response.json();
  assert.equal(body.code,"DETAIL_NO_BTIH");
  assert.equal(body.diagnostic.build,"THERARBAG_IPHONE_DIAG_V1");
  assert.equal(body.diagnostic.htmlStage,"HTML_NO_BTIH");
  assert.equal(body.diagnostic.jsonStage,"JSON_HTTP_503");
  assert.match(body.diagnostic.detailFingerprint,/^(?:[a-f0-9]{12}|unavailable)$/);
  assert.ok(body.diagnostic.elapsedMs>=0);
  assert.doesNotMatch(JSON.stringify(body.diagnostic),/magnet:|btih:|post-detail|therarbg\.com|upstream secret|password|token/i);
  assert.deepEqual(calls,[DETAIL,JSON_URL]);
 });
});
test("normal TheRarBg failure remains identical, without any diagnostic fields",async()=>{
 await withSource(async(url)=>{
  if(url===DETAIL)return new Response(html,{status:200});
  if(url===JSON_URL)return new Response("{}",{status:200,headers:{"content-type":"application/json"}});
  throw Error("unexpected source");
 },async()=>{
  const response=await Worker.fetch(request(),{});
  assert.equal(response.status,502);
  assert.deepEqual(await response.json(),{
   error:"TheRarBg magnet could not be resolved.",code:"DETAIL_NO_BTIH"
  });
 });
});
test("source JSON success has no extra requests or changed source infohash",async()=>{
 const calls=[];
 await withSource(async(url)=>{
  calls.push(url);
  if(url===DETAIL)return new Response(html,{status:200});
  if(url===JSON_URL)return new Response(JSON.stringify({info_hash:HASH}),{
   status:200,headers:{"content-type":"application/json"}
  });
  throw Error("unapproved origin");
 },async()=>{
  const response=await Worker.fetch(request({probe:true}),{});
  assert.equal(response.status,200);
  const body=await response.json();
  assert.equal(body.magnet,"magnet:?xt=urn:btih:"+HASH);
  assert.equal(body.diagnostic.jsonStage,"JSON_VALID");
  assert.deepEqual(calls,[DETAIL,JSON_URL]);
 });
});
test("source HTTP refusal yields finite no-fetch diagnostic stage",async()=>{
 await withSource(async()=>new Response("secret private response",{status:403}),async()=>{
  const body=await (await Worker.fetch(request({probe:true}),{})).json();
  assert.equal(body.code,"SOURCE_HTTP_403");
  assert.equal(body.diagnostic.htmlStage,"HTML_NOT_FETCHED");
  assert.equal(body.diagnostic.jsonStage,"JSON_NOT_STARTED");
  assert.doesNotMatch(JSON.stringify(body),/secret private response/);
 });
});
test("no source calls for invalid details even with opt-in header",async()=>{
 let calls=0;
 await withSource(async()=>{calls++;throw Error("unexpected network")},async()=>{
  const response=await Worker.fetch(request({probe:true,details:"https://evil.example/post-detail/95bf8b/item/"}),{});
  assert.equal(response.status,400);
  assert.equal(calls,0);
 });
});
