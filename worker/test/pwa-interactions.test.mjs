import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";
import {webcrypto} from "node:crypto";

const source=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const magnet="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567";
const json=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{"content-type":"application/json"}});
function harness(fetcher,initialStorage={},query=""){
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
  location:{origin:"https://index.alexlab.media",search:query},
  fetch:fetcher,crypto:webcrypto,URL,URLSearchParams,AbortController,
  Response,DOMException,Date,Promise,Set,Map,
  setTimeout:(cb)=>setTimeout(cb,0),clearTimeout,
 };
 runInNewContext(source+`
 renderResults=()=>{};
 renderProviderErrors=()=>{};
 toast=()=>{};
 globalThis.testing={state,search,sendMagnet,ensureMagnet,magnetIdentity,
  chooseProviders,orderedProviders,renderProviders,btdiggWaitMs,btdiggPacing,waitForBTDigg,
  magnetFailureText};
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

test("selecting every curated source issues exactly one request per provider including TPB",async()=>{
 const requested=[];let concurrent=0,maxConcurrent=0;
 const {api,element}=harness(async(path)=>{
  const url=new URL(path,"https://index.alexlab.media");
  const id=url.searchParams.get("providers");
  requested.push(id);concurrent++;maxConcurrent=Math.max(maxConcurrent,concurrent);
  await Promise.resolve();
  concurrent--;
  return json({results:[],stats:[{provider:id,ok:true,count:0}],errors:[]});
 });
 const all=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive",
  "oxtorrent","torrent9","therarbag","nonameclub","0magnet","animeworld"];
 element("query").value="lupin";element("category").value="all";
 api.state.selected=new Set(all);
 await api.search();
 assert.equal(requested.length,all.length,"no hidden extra search requests");
 assert.equal(new Set(requested).size,all.length,"no provider receives duplicate requests");
 assert.equal(requested.filter(id=>id==="thepiratebay").length,1);
 assert.ok(maxConcurrent<=3,"PWA bound to three parallel providers");
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


test("owner-pinned sources outrank audit, while unpinned latest results precede unknowns/errors",()=>{
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
  ["btdigg","knaben","torrentscsv","alpha","unknown","zeta"],
  "a successful in-session search improves unpinned ordering without outranking owner-pinned sources");
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

test("production 50 OxTorrent and 20 Torrent9 card Resolve requests choose canonical details, not advertising magnetSource",async()=>{
 const submissions=[];
 const {api}=harness(async(path,options)=>{
  assert.equal(path,"/api/resolve");
  const body=JSON.parse(options.body);
  submissions.push(body);
  return json({provider:body.provider,magnet});
 });
 const cases=[
  ...Array.from({length:50},(_,i)=>({
   id:"oxtorrent:sample"+i,provider:"oxtorrent",
   details:"https://www.oxtorrent.co/torrent/"+(133995+i)+"/toy-story-5-2026-multi-ca-1080p",
   magnetSource:"https://www.oxtorrent.co/telecharger/advertising-"+i,
   torrentFile:"https://www.oxtorrent.co/telecharger/advertising-"+i
  })),
  ...Array.from({length:20},(_,i)=>({
   id:"torrent9:sample"+i,provider:"torrent9",
   details:"https://www7.torrent9.to/torrent/"+(133873+i)+"/hope-2026-multi-ca",
   magnetSource:"https://www7.torrent9.to/download/advertising-"+i,
   torrentFile:"https://www7.torrent9.to/download/advertising-"+i
  }))
 ];
 for(const item of cases) {
  const received=await api.ensureMagnet(item);
  assert.equal(received,magnet);
  assert.equal(item.magnet,magnet);
 }
 assert.equal(submissions.length,70);
 for(let i=0;i<submissions.length;i++){
  assert.equal(submissions[i].provider,cases[i].provider);
  assert.equal(submissions[i].details,cases[i].details,"must use original canonical details route");
  assert.notEqual(submissions[i].details,cases[i].magnetSource,"must never click provider advertising/download route");
 }
 // Already resolved BTIH must be returned without another HTTP request.
 await api.ensureMagnet(cases[0]);
 assert.equal(submissions.length,70);
});

test("original deferred magnetSource precedence remains unchanged for all other providers",async()=>{
 const requests=[];
 const {api}=harness(async(path,options)=>{
  assert.equal(path,"/api/resolve");
  requests.push(JSON.parse(options.body));
  return json({magnet});
 });
 const oldProvider={
  provider:"nyaasi",
  details:"https://nyaa.si/view/123456",
  magnetSource:"https://nyaa.si/download/123456.torrent"
 };
 assert.equal(await api.ensureMagnet(oldProvider),magnet);
 assert.equal(requests.length,1);
 assert.equal(requests[0].provider,"nyaasi");
 assert.equal(requests[0].details,oldProvider.magnetSource);
});

test("OxTorrent/Torrent9 missing canonical details fail closed without contacting advertising source",async()=>{
 const requests=[];
 const {api}=harness(async(path,options)=>{
  requests.push({path,options});
  throw Error("Unexpected remote call");
 });
 for(const provider of ["oxtorrent","torrent9"]){
  await assert.rejects(api.ensureMagnet({
   provider,details:null,magnetSource:"https://external.invalid/download"
  }),/Provider has no supported magnet or details link/i);
 }
 assert.equal(requests.length,0,"do not send ad/redirect URLs even to the backend");
});

test("TheRarBg diagnostic mode is explicit and does not change source URL or normal UI",async()=>{
 const detail="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
 const seen=[];
 const diagnostic={build:"THERARBAG_IPHONE_DIAG_V1",detailFingerprint:"0123456789ab",
  htmlStage:"HTML_NO_BTIH",jsonStage:"JSON_HTTP_503",elapsedMs:31};
 const fail=async(path,options)=>{
  assert.equal(path,"/api/resolve");
  seen.push(options);
  return json({error:"TheRarBg magnet could not be resolved.",code:"DETAIL_NO_BTIH",
   diagnostic},502);
 };
 const diag=harness(fail,{},"?magnetra_diag=1");
 const item={provider:"therarbag",details:detail,magnet:null};
 await assert.rejects(diag.api.ensureMagnet(item),error=>{
  assert.equal(error.magnetraCode,"DETAIL_NO_BTIH");
  assert.equal(error.magnetraDiagnostic.detailFingerprint,"0123456789ab");
  const rendered=diag.api.magnetFailureText(item,error);
  assert.match(rendered,/HTML_NO_BTIH.*JSON_HTTP_503/);
  assert.doesNotMatch(rendered,/magnet:\\?|btih:|post-detail/);
  return true;
 });
 assert.equal(seen.length,1);
 assert.equal(JSON.parse(seen[0].body).details,detail);
 assert.equal(seen[0].headers["x-magnetra-resolve-diagnostic"],"owner-opt-in-20261024-v1");
 const plain=harness(fail);
 await assert.rejects(plain.api.ensureMagnet({provider:"therarbag",details:detail}),error=>{
  assert.ok(!error.magnetraDiagnostic);
  assert.doesNotMatch(plain.api.magnetFailureText(item,error),/Diagnostic:/);
  return true;
 });
 assert.equal(seen[1].headers["x-magnetra-resolve-diagnostic"],undefined);
});

test("alternative search never reselects the failing TPB source",()=>{
 assert.match(source,/new Set\(visibleFailures\.map\(f=>f\.provider\)\)/);
 assert.match(source,/safeLive=live\.filter\(id=>!failed\.has\(id\)\)/);
 assert.doesNotMatch(source,/\["knaben","torrentscsv","thepiratebay"\]/);
 const i18n=readFileSync(new URL("../../web/i18n.js",import.meta.url),"utf8");
 assert.match(i18n,/ThePirateBay limitează momentan solicitările/);
 assert.match(i18n,/ThePirateBay limita temporaneamente le richieste/);
});
