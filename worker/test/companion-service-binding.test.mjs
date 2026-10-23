import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";

const endpoint="https://index.alexlab.media/api/companion";
const deviceId="D".repeat(20);
const token="T".repeat(32);
function incoming(action,extra={}){
 return new Request(endpoint+"/"+action,{
  method:"POST",
  headers:{"content-type":"application/json","origin":"https://index.alexlab.media"},
  body:JSON.stringify({deviceId,token,...extra})
 });
}
const json=(body,status=200)=>new Response(JSON.stringify(body),{
 status,headers:{"content-type":"application/json"}
});

test("status uses bound relay; preserves fixed hostname, GET and bearer credentials",async()=>{
 let calls=0;
 const env={FLUD_RELAY:{async fetch(request){
  calls++;
  assert.equal(request.url,"https://flud-remote.alexlab.media/api/v1/device/"+deviceId+"/status");
  assert.equal(request.method,"GET");
  assert.equal(request.headers.get("authorization"),"Bearer "+token);
  return json({ok:true,online:true,autoStartReady:true});
 }}};
 const response=await worker.fetch(incoming("status"),env);
 assert.equal(response.status,200);
 assert.equal((await response.json()).online,true);
 assert.equal(calls,1);
});

test("bound relay returns its 401 without converting an auth failure into 502",async()=>{
 const env={FLUD_RELAY:{async fetch(){
  return json({error:"Unauthorized"},401);
 }}};
 const response=await worker.fetch(incoming("status"),env);
 assert.equal(response.status,401);
 const data=await response.json();
 assert.equal(data.error,"Unauthorized");
 assert.ok(!JSON.stringify(data).includes(token));
});

test("magnet uses same binding and existing idempotent request contract",async()=>{
 let sent;
 const env={FLUD_RELAY:{async fetch(request){
  assert.equal(request.url,"https://flud-remote.alexlab.media/api/v1/device/"+deviceId+"/magnet");
  assert.equal(request.method,"POST");
  assert.equal(request.headers.get("authorization"),"Bearer "+token);
  sent=await request.json();
  return json({ok:true,queued:true,id:"command-test-1"},202);
 }}};
 const magnet="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567";
 const response=await worker.fetch(incoming("magnet",{magnet,autoStart:true,requestId:"request-12345678"}),env);
 assert.equal(response.status,202);
 assert.equal(sent.magnet,magnet);
 assert.equal(sent.autoStart,true);
 assert.equal(sent.requestId,"request-12345678");
});

test("internal transport failure is still sanitized as a 502, not claimed as offline",async()=>{
 const env={FLUD_RELAY:{async fetch(){throw new Error("private transport details");}}};
 const response=await worker.fetch(incoming("status"),env);
 assert.equal(response.status,502);
 const body=await response.json();
 assert.deepEqual(body,{error:"Companion remote relay is unavailable."});
 assert.ok(!JSON.stringify(body).includes("private transport"));
});
