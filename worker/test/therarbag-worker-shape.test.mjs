import test from "node:test";
import assert from "node:assert/strict";
import Worker from "../src/index.mjs";
import {classifyTheRarBgWorkerHtmlShape,allowTheRarBgWorkerShapeDiagnostic,
  THERARBAG_SHAPE_STAGES} from "../src/therarbag-worker-shape.mjs";

const DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
const HASH="a".repeat(40);
const TOKEN="test-sensitive-string-DO-NOT-PRINT";
function request({headers={},detail=DETAIL,provider="therarbag"}={}){
 return new Request("https://index.alexlab.media/api/resolve",{
  method:"POST",headers:{"origin":"https://index.alexlab.media",
   "content-type":"application/json",...headers},
  body:JSON.stringify({provider,details:detail})
 });
}
const PROBE={"x-magnetra-shape-diagnostic":"20261024-readonly-exact"};
async function mockedSource(html,cb){
 const previousFetch=globalThis.fetch,priorRewriter=globalThis.HTMLRewriter;
 let calls=0;
 globalThis.fetch=async(url,opts)=>{
  calls++;
  assert.equal(url,DETAIL);
  assert.equal(opts.redirect,"manual");
  return new Response(html,{status:200,headers:{"content-type":"text/html"}});
 };
 class FakeHTMLRewriter{on(){return this}transform(res){return res}}
 globalThis.HTMLRewriter=FakeHTMLRewriter;
 try{await cb(()=>calls);}finally{
  globalThis.fetch=previousFetch;
  if(priorRewriter===undefined)delete globalThis.HTMLRewriter;
  else globalThis.HTMLRewriter=priorRewriter;
 }
}
test("finite stages distinguish Worker HTML from runner without exposing source",()=>{
 const samples=[
  ["<html><body><div>Advertisement only</div></body></html>",0,"SOURCE_DETAIL_MARKERS_ABSENT"],
  ["<html><body><button>Magnet Download</button></body></html>",0,"MAGNET_CONTROL_WITHOUT_MARKUP_LINK"],
  ["<html>Info Hash: unavailable</html>",0,"INFO_HASH_LABEL_VALUE_UNAVAILABLE"],
  ["<html>Info Hash: "+HASH+"</html>",0,"LABELED_BTIH_PRESENT_FALLBACK_REJECTED"],
  ["<html><a href='magnet:?xt=urn:btih:"+HASH+"'>Magnet</a></html>",0,"MAGNET_HTML_PRESENT_REWRITER_MISSED"],
  ["<html><a href='magnet:?xt=urn:btih:"+HASH+"'>Magnet</a></html>",1,"REWRITER_MATCHED_BUT_REJECTED"],
  ["<div>Other data</div>",0,"SOURCE_HTML_UNEXPECTED"],
  ["<html><script>magnet:?xt=urn:btih:"+HASH+"</script></html>",0,"SOURCE_DETAIL_MARKERS_ABSENT"]
 ];
 for(const [html,matches,expected] of samples){
  const result=classifyTheRarBgWorkerHtmlShape(html,matches);
  assert.equal(result,expected);
  assert.ok(THERARBAG_SHAPE_STAGES.has(result));
  assert.doesNotMatch(result,/a{40}|magnet:|https:|password|token/i);
 }
});
test("diagnostic is restricted to exact public page and header",()=>{
 const accept=request({headers:PROBE});
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(accept,"therarbag",DETAIL),true);
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(request(),"therarbag",DETAIL),false);
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(request({headers:{"x-magnetra-shape-diagnostic":"other"}}),"therarbag",DETAIL),false);
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(accept,"torrent9",DETAIL),false);
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(accept,"therarbag",DETAIL+"?query=evil"),false);
 assert.equal(allowTheRarBgWorkerShapeDiagnostic(accept,"therarbag","https://therarbg.com/post-detail/other/"),false);
});
test("only approved probe yields finite stage on missing source HTML",async()=>{
 const html="<html><main><p>upstream full HTML without hash</p></main></html>";
 await mockedSource(html,async calls=>{
  const probed=await Worker.fetch(request({headers:PROBE}),{});
  assert.equal(probed.status,502);
  const data=await probed.json();
  assert.deepEqual(data,{
    error:"TheRarBg magnet could not be resolved.",
    code:"DETAIL_NO_BTIH",
    shapeDiagnosticVersion:"THERARBAG_WORKER_SHAPE_V1",
    shapeStage:"SOURCE_DETAIL_MARKERS_ABSENT"
  });
  assert.equal(calls(),1);
  const normal=await Worker.fetch(request(),{});
  const ordinary=await normal.json();
  assert.equal(normal.status,502);
  assert.deepEqual(ordinary,{
    error:"TheRarBg magnet could not be resolved.",
    code:"DETAIL_NO_BTIH"
  });
  assert.equal(calls(),2);
 });
});
test("a valid original labelled infohash still resolves; diagnostic never changes magnet",async()=>{
 const html="<html><main><p>Info Hash: "+HASH+"</p></main></html>";
 await mockedSource(html,async calls=>{
  const ordinary=await Worker.fetch(request(),{});
  const withProbe=await Worker.fetch(request({headers:PROBE}),{});
  assert.equal(ordinary.status,200);
  assert.equal(withProbe.status,200);
  assert.equal((await ordinary.json()).magnet,"magnet:?xt=urn:btih:"+HASH);
  const data=await withProbe.json();
  assert.equal(data.magnet,"magnet:?xt=urn:btih:"+HASH);
  assert.equal(data.shapeDiagnosticVersion,"THERARBAG_WORKER_SHAPE_V1");
  assert.equal(calls(),2);
 });
});
test("malformed, scripted and unrelated source text cannot enter diagnostic output",async()=>{
 const html="<html><script>"+TOKEN+"</script><p>"+TOKEN+"</p><div>Info Hash: invalid</div></html>";
 await mockedSource(html,async()=>{
  const data=await (await Worker.fetch(request({headers:PROBE}),{})).json();
  assert.equal(data.shapeStage,"INFO_HASH_LABEL_VALUE_UNAVAILABLE");
  assert.doesNotMatch(JSON.stringify(data),/test-sensitive|invalid|<script>|therarbg\.com|post-detail/);
 });
});
test("no new external requests for invalid detail URL",async()=>{
 let calls=0;
 const old=globalThis.fetch;
 globalThis.fetch=async()=>{calls++;throw Error("unexpected network");};
 try{
  const resp=await Worker.fetch(request({detail:"https://evil.example/post-detail/95bf8b/"}),{});
  assert.equal(resp.status,400);
  assert.equal(calls,0);
 }finally{globalThis.fetch=old;}
});
