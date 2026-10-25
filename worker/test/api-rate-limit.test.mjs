import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import worker from "../src/index.mjs";

const ROOT="https://index.alexlab.media";
const sensitive=[
 ["GET","/api/search?q=sample&providers=knaben"],
 ["POST","/api/resolve"],
 ["POST","/api/companion/magnet"],
 ["POST","/api/companion/status"]
];
function request(method,path,body){
 return new Request(ROOT+path,{
  method,
  headers:{"origin":ROOT,"cf-connecting-ip":"synthetic-client","content-type":"application/json"},
  ...(method==="POST"?{body:JSON.stringify(body??{})}:{})
 });
}

test("Wrangler binds a scoped rate limiter with a bounded one-minute window",()=>{
 const cfg=JSON.parse(readFileSync(new URL("../wrangler.jsonc",import.meta.url),"utf8"));
 assert.equal(cfg.name,"alexlab-magnetra");
 assert.equal(cfg.ratelimits.length,1);
 const cfgLimit=cfg.ratelimits[0];
 assert.equal(cfgLimit.name,"MAGNETRA_API_RATE");
 assert.match(cfgLimit.namespace_id,/^[1-9][0-9]*$/);
 assert.deepEqual(cfgLimit.simple,{limit:90,period:60});
 assert.equal(cfg.services.find(s=>s.binding==="FLUD_RELAY")?.service,"flud-remote-relay");
});

test("Only exact sensitive API methods and paths receive 429; values never leak",async()=>{
 for(const [method,path] of sensitive){
  let calls=0,key="";
  const env={MAGNETRA_API_RATE:{async limit(input){
    calls++;key=input.key;return {success:false};
  }},FLUD_RELAY:{async fetch(){throw Error("Should not call private relay");}}};
  const response=await worker.fetch(request(method,path,{
   deviceId:"SYNTHETIC_DEVICE",token:"SYNTHETIC_TOKEN",magnet:"synthetic-magnet"
  }),env);
  assert.equal(response.status,429,method+" "+path);
  assert.equal(response.headers.get("cache-control"),"no-store");
  assert.equal(response.headers.get("retry-after"),"60");
  assert.equal(calls,1);
  assert.match(key,/synthetic-client/);
  assert.ok(!key.includes("sample"));
  assert.ok(!key.includes("TOKEN"));
  assert.ok(!key.includes("magnet"));
  const body=JSON.stringify(await response.json());
  assert.ok(!body.includes("SYNTHETIC_DEVICE"));
  assert.ok(!body.includes("SYNTHETIC_TOKEN"));
 }
});

test("Public endpoints, assets, and other HTTP methods are not rate-limited",async()=>{
 let calls=0;
 const env={MAGNETRA_API_RATE:{async limit(){calls++;return {success:false};}},
  ASSETS:{async fetch(){return new Response("shell",{status:200});}}};
 for(const path of ["/api/health","/api/providers","/api/recovery-plan"]){
  const response=await worker.fetch(request("GET",path),env);
  assert.equal(response.status,200);
 }
 assert.equal((await worker.fetch(request("GET","/"),env)).status,200);
 assert.equal((await worker.fetch(request("GET","/api/resolve"),env)).status,404);
 assert.equal(calls,0);
});

test("Normal allowed requests retain previous validation and origin controls",async()=>{
 let calls=0;
 const env={MAGNETRA_API_RATE:{async limit(){calls++;return {success:true};}}};
 const response=await worker.fetch(request("GET","/api/search?q=x"),env);
 assert.equal(response.status,400); // Invalid query length; not a limiter error.
 assert.equal(calls,1);
});

test("The missing binding keeps pre-existing local/CI contract fixtures functional",async()=>{
 const response=await worker.fetch(request("GET","/api/search?q=x"),{});
 assert.equal(response.status,400);
});

test("Unexpected binding failures are sanitized with no raw exception details",async()=>{
 const env={MAGNETRA_API_RATE:{async limit(){
  throw new Error("PRIVATE_DIAGNOSTIC_PAYLOAD_SHOULD_NOT_APPEAR");
 }}};
 const response=await worker.fetch(request("GET","/api/search?q=abc"),env);
 assert.equal(response.status,503);
 assert.equal(response.headers.get("cache-control"),"no-store");
 assert.ok(!JSON.stringify(await response.json()).includes("PRIVATE_DIAGNOSTIC"));
});
