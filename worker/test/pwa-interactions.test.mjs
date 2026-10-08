import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";
import {webcrypto} from "node:crypto";

const source=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const magnet="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567";
const json=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{"content-type":"application/json"}});
function harness(fetcher){
 const elements=new Map();
 const element=id=>{
  if(!elements.has(id))elements.set(id,{
   textContent:"",value:"",disabled:false,
   replaceChildren(){},scrollIntoView(){},showModal(){},close(){},
   classList:{add(){},remove(){},toggle(){}}
  });
  return elements.get(id);
 };
 const sandbox={
  document:{getElementById:element,addEventListener(){}},
  location:{origin:"https://index.alexlab.media"},
  fetch:fetcher,crypto:webcrypto,URL,URLSearchParams,AbortController,
  Response,DOMException,Date,Promise,Set,Map,
  setTimeout:(cb)=>setTimeout(cb,0),clearTimeout,
 };
 runInNewContext(source+`
 renderResults=()=>{};
 renderProviderErrors=()=>{};
 toast=()=>{};
 globalThis.testing={state,search,sendMagnet,magnetIdentity};
 `,sandbox,{filename:"web/app.js"});
 return {api:sandbox.testing,element};
}
const tick=()=>new Promise(resolve=>setTimeout(resolve,10));

test("sliding search pool starts the next provider without waiting for an unrelated timeout",async()=>{
 let releaseSlow;
 const slow=new Promise(resolve=>{releaseSlow=resolve;});
 const started=[];
 const {api,element}=harness(async(path)=>{
  const id=new URL(path,"https://index.alexlab.media").searchParams.get("providers");
  started.push(id);
  if(id==="slow")await slow;
  return json({results:[{provider:id,name:id}],errors:[]});
 });
 element("query").value="ubuntu";element("category").value="all";
 api.state.selected=new Set(["slow","one","two","three","four"]);
 const pending=api.search();
 await tick();
 assert.deepEqual(started,["slow","one","two","three","four"]);
 assert.equal(api.state.items.length,4,"fast results stream while slow provider is still pending");
 releaseSlow();
 await pending;
 assert.equal(api.state.items.length,5);
 assert.equal(api.state.searching,false);
});

test("cancel search preserves completed results but ignores late and stale responses",async()=>{
 let releaseSlow;
 const slow=new Promise(resolve=>{releaseSlow=resolve;});
 const {api,element}=harness(async(path)=>{
  const id=new URL(path,"https://index.alexlab.media").searchParams.get("providers");
  if(id==="slow")await slow; // hostile transport ignores AbortSignal
  return json({results:[{provider:id,name:id}],errors:[]});
 });
 element("query").value="ubuntu";element("category").value="all";
 api.state.selected=new Set(["fast","slow"]);
 const pending=api.search();
 await tick();
 assert.equal(api.state.items.length,1);
 await api.search(); // pressing Search again while busy means Cancel
 releaseSlow();
 await pending;
 assert.deepEqual(api.state.items.map(x=>x.provider),["fast"]);
 assert.equal(api.state.searching,false);
 assert.match(element("notice").textContent,/cancelled/i);
});

test("Companion dispatch blocks concurrent repeat taps and reuses idempotency ID",async()=>{
 let release;
 const gate=new Promise(resolve=>{release=resolve;});
 const submissions=[];
 const {api}=harness(async(path,options)=>{
  if(path==="/api/companion/magnet"){
   const body=JSON.parse(options.body);
   submissions.push(body);
   if(submissions.length===1)await gate;
   return json({ok:true,queued:true,duplicate:submissions.length>1,id:"receipt-test-1"},202);
  }
  if(path==="/api/companion/status")return json({ok:true,lastResult:{id:"receipt-test-1",ok:true}});
  throw Error("unexpected fetch "+path);
 });
 api.state.pairing={deviceId:"D".repeat(20),token:"T".repeat(26),autoStart:false};
 const button=()=>({textContent:"Send to Flud",disabled:false,title:""});
 const a=api.sendMagnet({id:"provider:a",magnet},button());
 await tick();
 const b=api.sendMagnet({id:"provider:b",magnet},button());
 await b;
 assert.equal(submissions.length,1,"equivalent magnets cannot be queued concurrently");
 release();
 await a;
 await api.sendMagnet({id:"provider:c",magnet},button());
 assert.equal(submissions.length,2);
 assert.equal(submissions[0].requestId,submissions[1].requestId,"relay request ID must remain stable for 110 seconds");
 assert.equal(api.magnetIdentity(magnet,"device"),api.magnetIdentity(magnet.toUpperCase().replace("MAGNET:?","magnet:?"),"device"));
});
