import test from "node:test";
import assert from "node:assert/strict";
import {rock64BTDiggFetcher,BTDIGG_GATEWAY_ORIGIN} from "../src/btdigg-rock64.mjs";

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
