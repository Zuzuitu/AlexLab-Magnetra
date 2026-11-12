import test from "node:test";
import assert from "node:assert/strict";
import {rock64BTDiggFetcher,BTDIGG_GATEWAY_ORIGIN,boundedBTDiggRetryAfterMs} from "../src/btdigg-rock64.mjs";

const secret="x".repeat(64);
test("only configured server can use Rock64's fixed BTDigg endpoint",async()=>{
 assert.equal(rock64BTDiggFetcher({}),null);
 assert.throws(()=>rock64BTDiggFetcher({BTDIGG_GATEWAY_TOKEN:"short"}));
 let calls=0;
 const adapter=rock64BTDiggFetcher({BTDIGG_GATEWAY_TOKEN:secret},async(target,options)=>{
  calls++;
  assert.equal(new URL(target).origin,BTDIGG_GATEWAY_ORIGIN);
  assert.equal(options.redirect,"manual");
  return new Response("<html>OK</html>",{headers:{"content-type":"text/html"}});
 });
 const response=await adapter("https://btdig.com/search?q=ubuntu");
 assert.equal(response.status,200);
 assert.equal(calls,1);
 for(const invalid of [
  "https://other.example/search?q=ubuntu",
  "http://btdig.com/search?q=ubuntu",
  "https://btdig.com/other?q=ubuntu",
  "https://btdig.com/search?q=ubuntu&extra=1",
  "https://btdig.com/search?q=x"
 ])await assert.rejects(()=>adapter(invalid));
 assert.equal(calls,1);
});

test("gateway rejects redirects, unexpected HTML shape and rate limiting",async()=>{
 const wrap=response=>rock64BTDiggFetcher({BTDIGG_GATEWAY_TOKEN:secret},async()=>response);
 for(const res of [
  new Response("",{status:302,headers:{location:"https://other.example"}}),
  new Response("",{status:401}),
  new Response("",{status:429}),
  new Response("wrong",{status:200,headers:{"content-type":"application/json"}})
 ]){
  await assert.rejects(()=>wrap(res)("https://btdig.com/search?q=ubuntu"));
 }
});

test("intermittent gateway failures expose safe, BTDigg-only cause and never auto-retry",async()=>{
 const original="https://btdig.com/search?q=ubuntu";
 const make=fn=>rock64BTDiggFetcher({BTDIGG_GATEWAY_TOKEN:secret},fn);
 const cases=[
  [()=>{throw new DOMException("The operation was aborted due to timeout","TimeoutError");},/tunnel timed out/],
  [()=>{throw Error("Cloudflare subrequest error 1042");},/tunnel Cloudflare 1042/],
  [()=>{throw TypeError("fetch failed: private connection URL");},/gateway transport failed/],
  [()=>new Response('{"error":"timeout"}',{status:504,headers:{"content-type":"application/json"}}),/source timed out/]
 ];
 for(const [run,pattern] of cases){
  let calls=0;
  const fetcher=make(async()=>{calls++;return run();});
  await assert.rejects(()=>fetcher(original),pattern);
  assert.equal(calls,1,"a failed BTDigg search must never retry automatically");
 }
});

test("gateway source refusal carries bounded Retry-After to the Worker cache",async()=>{
 const url="https://btdig.com/search?q=release-PSA";
 const adapter=rock64BTDiggFetcher(
  {BTDIGG_GATEWAY_TOKEN:secret},
  async()=>new Response("",{status:429,headers:{
   "retry-after":"601","x-magnetra-btdigg-429-scope":"source"
  }}));
 await assert.rejects(()=>adapter(url),e=>{
  assert.match(e.message,/HTTP 429/);
  assert.equal(e.retryAfterMs,601_000);
  assert.doesNotMatch(String(e),/Bearer|magnet:|token/i);
  return true;
 });
 for(const [value,expected] of [
  ["5",5000],["1800",1800_000],["1801",1800_000],
  ["999999",1800_000],["0",null],["-1",null],
  ["1.2",null],[" 30 ",null],["Wed, 12 Nov",null],["",null],
  [null,null],["1234567",null]
 ])assert.equal(boundedBTDiggRetryAfterMs(value),expected,String(value));
});

test("local 5-second gateway pacing is not mislabeled as upstream refusal",async()=>{
 let calls=0;
 const adapter=rock64BTDiggFetcher(
  {BTDIGG_GATEWAY_TOKEN:secret},
  async()=>{calls++;return new Response("",{status:429,headers:{
   "retry-after":"5","x-magnetra-btdigg-429-scope":"local-pacing"
  }});});
 await assert.rejects(()=>adapter("https://btdig.com/search?q=first"),e=>{
  assert.equal(e.message,"BTDigg Rock64 local pacing.");
  assert.doesNotMatch(e.message,/HTTP 429/);
  assert.equal(e.retryAfterMs,undefined);
  return true;
 });
 assert.equal(calls,1,"one bounded local response, no source retry");
});

test("older gateway without a scope header fails closed on 429",async()=>{
 const adapter=rock64BTDiggFetcher(
  {BTDIGG_GATEWAY_TOKEN:secret},
  async()=>new Response("",{status:429,headers:{"retry-after":"9"}}));
 await assert.rejects(()=>adapter("https://btdig.com/search?q=original"),e=>{
  assert.match(e.message,/HTTP 429/);
  assert.equal(e.retryAfterMs,9000);
  return true;
 });
});
