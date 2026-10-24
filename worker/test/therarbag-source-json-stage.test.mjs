import test from "node:test";
import assert from "node:assert/strict";
import {diagnoseOriginalTheRarBgJson} from "../src/therarbag-source-json-stage.mjs";

const DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/?format=json";
const HASH="a".repeat(40);
const json=(obj,headers={})=>new Response(JSON.stringify(obj),{
 status:200,headers:{"content-type":"application/json",...headers}
});
test("one original source request and only a finite safe stage",async()=>{
 let calls=0;
 const stage=await diagnoseOriginalTheRarBgJson(async(url,opts)=>{
  calls++;
  assert.equal(url,DETAIL);
  assert.equal(opts.method,"GET");
  assert.equal(opts.redirect,"manual");
  assert.equal(opts.headers.accept,"application/json");
  return json({data:{info_hash:HASH}});
 });
 assert.equal(calls,1);
 assert.equal(stage,"JSON_WRAPPED_BTIH_VALID");
 assert.doesNotMatch(stage,/magnet|https|a{40}|secret/i);
});
test("classify actual HTTP blocks and HTML challenge without leaking response data",async()=>{
 for(const [response,expected] of [
  [new Response("upstream HTML",{status:403}),"SOURCE_HTTP_403"],
  [new Response("upstream HTML",{status:429}),"SOURCE_HTTP_429"],
  [new Response("go elsewhere",{status:302,headers:{"location":"https://evil.invalid"}}),"HTTP_REDIRECT"],
  [new Response("<html>challenge</html>",{status:200,headers:{"content-type":"text/html"}}),"HTML_NOT_JSON"],
  [json({data:{info_hash:HASH}},{"cf-mitigated":"challenge"}),"SOURCE_CHALLENGE"],
  [json({data:{info_hash:"x"}}),"JSON_WRAPPED_BTIH_INVALID"],
  [json({payload:{info_hash:HASH}}),"MISSING_DATA_OBJECT"],
  [new Response("{not-json",{status:200,headers:{"content-type":"application/json"}}),"INVALID_JSON"],
 ]){
   const stage=await diagnoseOriginalTheRarBgJson(async()=>response);
   assert.equal(stage,expected);
   assert.match(stage,/^[A-Z0-9_]{3,45}$/);
 }
});
test("unwrapped Axios JSON response is explicitly recognized",async()=>{
  const h="a".repeat(40);
  const stage=await diagnoseOriginalTheRarBgJson(async()=>json({info_hash:h}));
  assert.equal(stage,"JSON_ROOT_BTIH_VALID");
  assert.equal(await diagnoseOriginalTheRarBgJson(async()=>json([{"info_hash":h}])),"JSON_ROOT_ARRAY");
  assert.equal(await diagnoseOriginalTheRarBgJson(async()=>json({error:"blocked"})),"JSON_ERROR_ENVELOPE");
  assert.equal(await diagnoseOriginalTheRarBgJson(async()=>json({results:[]})),"JSON_RESULTS_RESPONSE");
  assert.equal(await diagnoseOriginalTheRarBgJson(async()=>json({info_hash:h,data:{info_hash:"b".repeat(40)}})),"JSON_HASH_CONFLICT");
});
test("network errors are classified without request body or source URI",async()=>{
 const stage=await diagnoseOriginalTheRarBgJson(async()=>{
   throw Error("secret-magnet https://therarbg.com sensitive text");
 });
 assert.equal(stage,"FETCH_NETWORK");
});
