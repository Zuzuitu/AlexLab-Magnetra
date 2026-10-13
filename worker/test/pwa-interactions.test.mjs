import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";
import {webcrypto} from "node:crypto";

const source=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const magnet="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567";
const json=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{"content-type":"application/json"}});
function harness(fetcher,initialStorage={}){
 const storage=new Map(Object.entries(initialStorage));
 const localStorage={
  getItem:key=>storage.get(key)??null,
  setItem:(key,value)=>storage.set(key,String(value)),
  removeItem:key=>storage.delete(key)
 };
 const makeElement=tag=>({
  tagName:tag,children:[],textContent:"",value:"",disabled:false,
  replaceChildren(...kids){this.children=[...kids]},append(...kids){this.children.push(...kids)},
  addEventListener(){},scrollIntoView(){},showModal(){},close(){},
  classList:{add(){},remove(){},toggle(){}}
 });
 const elements=new Map();
 const element=id=>{
  if(!elements.has(id))elements.set(id,makeElement("div"));
  return elements.get(id);
 };
 const sandbox={
  document:{getElementById:element,createElement:makeElement,addEventListener(){}},
  localStorage,
  location:{origin:"https://index.alexlab.media"},
  fetch:fetcher,crypto:webcrypto,URL,URLSearchParams,AbortController,
  Response,DOMException,Date,Promise,Set,Map,
  setTimeout:(cb)=>setTimeout(cb,0),clearTimeout,
 };
 runInNewContext(source+`
 renderResults=()=>{};
 renderProviderErrors=()=>{};
 toast=()=>{};
 globalThis.testing={state,search,sendMagnet,magnetIdentity,
  chooseProviders,orderedProviders,renderProviders,btdiggWaitMs,btdiggPacing,waitForBTDigg};
 `,sandbox,{filename:"web/app.js"});
 return {api:sandbox.testing,element,storage};
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
 assert.deepEqual(Array.from(api.state.items,x=>x.provider),["fast"]);
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

test("provider picker uses current browser-session outcomes without triggering additional probes",async()=>{
 let requests=0;
 const {api,element}=harness(async(path)=>{
  requests++;
  const id=new URL(path,"https://index.alexlab.media").searchParams.get("providers");
  if(id==="btdigg")return json({results:[{provider:id,name:"Ubuntu fixture"}],
   stats:[{provider:id,count:1,ok:true}],errors:[]});
  return json({results:[],stats:[{provider:id,count:0,ok:false}],
   errors:[{provider:id,code:"TIMEOUT",message:"Provider timed out."}]});
 });
 element("query").value="ubuntu";
 element("category").value="all";
 api.state.selected=new Set(["btdigg","other"]);
 await api.search();
 assert.equal(api.state.sessionAudit.btdigg.state,"results");
 assert.equal(api.state.sessionAudit.btdigg.count,1);
 assert.equal(api.state.sessionAudit.other.state,"error");
 assert.equal(requests,2,"rendering status badges must not ping providers");
});


test("BTDigg is pinned; actual latest audit positives precede unknowns then source errors",()=>{
 const {api,element}=harness(async()=>json({}));
 const p=(id,name,category)=>({id,name,ported:true,lastAudit:{state:category}});
 api.state.providers=[
  p("zeta","Zeta","error"),
  p("torrentscsv","TorrentsCSV","results"),
  p("unknown","Unknown","empty-unverified"),
  p("btdigg","BTDigg","results"),
  p("knaben","Knaben","results"),
  p("alpha","Alpha","error")
 ];
 assert.deepEqual(Array.from(api.orderedProviders(api.state.providers),p=>p.id),
  ["btdigg","knaben","torrentscsv","unknown","alpha","zeta"]);
 api.state.sessionAudit.alpha={state:"results",count:1,at:"now"};
 assert.deepEqual(Array.from(api.orderedProviders(api.state.providers),p=>p.id),
  ["btdigg","alpha","knaben","torrentscsv","unknown","zeta"],
  "a successful in-session search can improve a stale error label");
 api.renderProviders();
 assert.equal(element("providerGrid").children.length,6);
 assert.equal(element("providerGrid").children[0].children[0].children[1].textContent,"BTDigg");
});

test("fresh profiles include BTDigg, legacy defaults migrate, custom selection remains user-owned",()=>{
 const all=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive","custom"];
 const providers=all.map(id=>({id,ported:true}));
 const create=(stored)=>{
  const initial=stored===undefined?{}:{"magnetra.providers.v1":JSON.stringify(stored)};
  const h=harness(async()=>json({}),initial);
  h.api.state.providers=providers;
  h.api.chooseProviders();
  return {selected:Array.from(h.api.state.selected),stored:JSON.parse(h.storage.get("magnetra.providers.v1"))};
 };
 const defaults=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"];
 assert.deepEqual(create().selected,defaults);
 assert.deepEqual(create(["knaben","torrentscsv","thepiratebay","internetarchive"]).selected,defaults);
 assert.deepEqual(create(["custom","knaben"]).selected,["custom","knaben"]);
 assert.deepEqual(create(["btdigg"]).selected,["btdigg"]);
 assert.deepEqual(create(["custom","knaben"]).stored,["custom","knaben"]);
});

test("rapid BTDigg distinct searches wait locally and aborted waits never reach the API",async()=>{
 let calls=0;
 const {api}=harness(async()=>{calls++;return json({results:[],stats:[],errors:[]});});
 const now=Date.now();
 api.btdiggPacing.nextAllowedAt=now+5500;
 api.btdiggPacing.lastGoodQuery=null;
 assert.ok(api.btdiggWaitMs("new term",now)>=5400);
 api.btdiggPacing.lastGoodQuery="ubuntu";
 api.btdiggPacing.lastGoodUntil=now+60000;
 assert.equal(api.btdiggWaitMs("ubuntu",now),0,"reuse cached proven same-query results");
 assert.ok(api.btdiggWaitMs("different",now)>=5400);
 const controller=new AbortController();
 const pending=api.waitForBTDigg("different",controller.signal);
 controller.abort();
 await assert.rejects(pending,/cancelled/i);
 assert.equal(calls,0,"cancelled, not-yet-sent searches do not hit Rock64");
});
