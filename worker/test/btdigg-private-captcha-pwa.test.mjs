import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const headers=readFileSync(new URL("../../web/_headers",import.meta.url),"utf8");
const i18n=readFileSync(new URL("../../web/i18n.js",import.meta.url),"utf8");

function fixture(){
 const store=new Map();
 const elements=new Map();
 const element=id=>{
  if(!elements.has(id))elements.set(id,{
    value:"",textContent:"",hidden:true,href:"",src:"",children:[],
    showModal(){this.open=true},close(){this.open=false},
    addEventListener(){},replaceChildren(...xs){this.children=xs},
    append(...xs){this.children.push(...xs)}
   });
  return elements.get(id);
 };
 const sandbox={
  document:{getElementById:element,createElement:()=>element("new"),addEventListener(){}},
  location:{origin:"https://index.alexlab.media",search:"",hash:""},
  localStorage:{
   getItem:k=>store.get(k)??null,
   setItem:(k,v)=>store.set(k,String(v)),
   removeItem:k=>store.delete(k),
  },
  URL,URLSearchParams,Set,Map,Date,Promise,AbortController,Response,
  setTimeout,clearTimeout
 };
 runInNewContext(app+`
 globalThis.test={
   validatedBTDiggViewerOrigin,btdiggPrivateViewerUrl,
   activateBTDiggViewer,disconnectBTDiggViewer,
   openBTDiggVerification,openBTDiggViewerFromAction,finishBTDiggVerification,
   btdiggVerificationModeForCode,btdiggVisibleRefusalOnly,
   fetchBTDiggWithOneGuardedNewTab,
 };
 `,sandbox,{filename:"web/app.js"});
 return {ui:sandbox.test,element,store,document:sandbox.document};
}

test("private BTDigg verification iframe only accepts user-entered HTTPS tailnet :8444",()=>{
 const {ui}=fixture();
 const good="https://rock64.example.ts.net:8444/vnc.html";
 assert.equal(ui.validatedBTDiggViewerOrigin(good),
              "https://rock64.example.ts.net:8444");
 assert.equal(ui.btdiggPrivateViewerUrl(good),
              good+"?autoconnect=1&resize=scale");
 const rejected=[
  "http://rock64.example.ts.net:8444/vnc.html",
  "https://rock64.example.ts.net:6088/vnc.html",
  "https://rock64.example.ts.net/vnc.html",
  "https://evil.example:8444/vnc.html",
  "https://rock64.example.ts.net.attacker.test:8444/vnc.html",
  "https://u:p@rock64.example.ts.net:8444/vnc.html",
  "https://rock64.example.ts.net:8444/admin",
  "https://rock64.example.ts.net:8444/vnc.html?password=secret",
  "https://rock64.example.ts.net:8444/vnc.html#token",
  "javascript:alert(1)",
  "https://rock64.example.ts.net:8444/vnc.html"+"a".repeat(300)
 ];
 for(const value of rejected){
  assert.equal(ui.validatedBTDiggViewerOrigin(value),null,value);
  assert.equal(ui.btdiggPrivateViewerUrl(value),null,value);
 }
});

test("user click opens only HTTPS iframe and close tears down remote desktop",()=>{
 const {ui,element,store}=fixture();
 const input=element("btdiggNovncOrigin");
 const frame=element("btdiggViewerFrame");
 const host=element("btdiggViewerContainer");
 ui.openBTDiggVerification();
 assert.equal(frame.src,"","never load noVNC automatically");
 input.value="https://rock64.example.ts.net:8444/vnc.html";
 assert.equal(ui.activateBTDiggViewer(),true);
 assert.equal(host.hidden,false);
 assert.ok(frame.src.startsWith("https://rock64.example.ts.net:8444/vnc.html?"));
 assert.equal(element("btdiggViewerFallback").href,frame.src);
 assert.equal(store.get("magnetra.btdigg-private-viewer.v1"),
              JSON.stringify("https://rock64.example.ts.net:8444"));
 assert.equal(store.size,1,"store only URL origin, no password, CAPTCHA or query");
 ui.finishBTDiggVerification(false);
 assert.equal(frame.src,"about:blank");
 assert.equal(host.hidden,true);
 ui.openBTDiggVerification();
 assert.equal(input.value,"https://rock64.example.ts.net:8444");
 assert.equal(frame.src,"about:blank","no automatic remote reconnect");
});

test("one explicit verification action opens the saved private viewer, never a source search",()=>{
 const {ui,element,store}=fixture();
 const key="magnetra.btdigg-private-viewer.v1";
 const frame=element("btdiggViewerFrame");
 ui.openBTDiggViewerFromAction("BTDIGG_CAPTCHA_REQUIRED");
 assert.equal(frame.src,"","first use requires setup");
 assert.equal(element("btdiggViewerContainer").hidden,true);
 store.set(key,JSON.stringify("https://invalid.example:8444"));
 ui.openBTDiggViewerFromAction("BTDIGG_CAPTCHA_REQUIRED");
 assert.equal(frame.src,"","revalidate saved addresses before loading");
 const origin="https://rock64.example.ts.net:8444";
 store.set(key,JSON.stringify(origin));
 for(const code of ["BTDIGG_CAPTCHA_REQUIRED","BTDIGG_VISIBLE_REFUSAL"]){
  ui.openBTDiggViewerFromAction(code);
  assert.equal(frame.src,origin+"/vnc.html?autoconnect=1&resize=scale");
  assert.equal(element("btdiggViewerContainer").hidden,false);
  const refusal=code==="BTDIGG_VISIBLE_REFUSAL";
  assert.equal(element("btdiggVerificationRetry").hidden,refusal);
  ui.finishBTDiggVerification(refusal);
  assert.equal(frame.src,"about:blank");
 }
});

test("manual-only verification UI has no source polling or open web proxy",()=>{
 for(const id of [
  "btdiggVerificationDialog","btdiggNovncOrigin",
  "btdiggViewerFrame","btdiggVerificationRetry",
  "btdiggOpenPrivateViewer","btdiggViewerFallback"
 ])assert.ok(html.includes('id="'+id+'"'),id);
 assert.ok(app.includes('"BTDIGG_CAPTCHA_REQUIRED","BTDIGG_VISIBLE_REFUSAL"'));
 assert.ok(app.includes("disconnectBTDiggViewer"));
 assert.ok(app.includes('frame-src')===false);
 assert.ok(!/captcha\.solve|recaptcha\.solve|playwright-stealth|2captcha|anticaptcha/i.test(app+html));
 assert.match(headers,/frame-src https:\/\/\*\.ts\.net:8444;/);
 assert.match(headers,/script-src 'self'/);
 assert.match(headers,/connect-src 'self'/);
 assert.match(headers,/frame-ancestors 'none'/);
 assert.ok(i18n.includes('"Verify BTDigg inside Magnetra"'));
 assert.ok(i18n.includes('"it": "Verifica BTDigg in Magnetra"'));
 assert.ok(!html.includes('src="https://rock64.'));
});

test("source refusal offers inspection-only; CAPTCHA still offers manual verification",()=>{
 const {ui,element}=fixture();
 const retry=element("btdiggVerificationRetry");
 assert.equal(ui.btdiggVerificationModeForCode("BTDIGG_VISIBLE_REFUSAL"),"refusal");
 assert.equal(ui.btdiggVerificationModeForCode("BTDIGG_CAPTCHA_REQUIRED"),"captcha");
 ui.openBTDiggVerification("refusal");
 assert.equal(retry.hidden,true,"Too Many Requests is not a solved CAPTCHA");
 assert.match(element("btdiggVerificationIntro").textContent,/Too Many Requests/);
 ui.finishBTDiggVerification(true);
 assert.equal(retry.hidden,true,"refusal must not cause a search");
 ui.openBTDiggVerification("captcha");
 assert.equal(retry.hidden,false,"confirmed human challenge may request user retry");
});

test("one explicit PWA search makes exactly one delayed new-tab opportunity after visible refusal",async()=>{
 const {ui,element}=fixture();
 const signal=new AbortController().signal;
 const original={errors:[{provider:"btdigg",code:"BTDIGG_VISIBLE_REFUSAL"}]};
 const after={results:[{provider:"btdigg",title:"fixture"}],errors:[]};
 const calls=[];
 let waiting=0;
 const request=async(path,opts)=>{
  calls.push([path,opts.signal]);
  return calls.length===1?original:after;
 };
 const pause=async(query,requestedSignal)=>{
  waiting++;
  assert.equal(query,"synthetic query");
  assert.equal(requestedSignal,signal);
 };
 const now=Date.now();
 const value=await ui.fetchBTDiggWithOneGuardedNewTab(
  "/api/search?providers=btdigg","synthetic query",signal,request,pause);
 assert.equal(value,after);
 assert.equal(waiting,1);
 assert.equal(calls.length,2,"strict maximum one additional request");
 assert.equal(calls[0][0],calls[1][0],"same owner query and provider");
 assert.equal(element("notice").textContent.includes("BTDigg"),true);
 assert.ok(Date.now()-now<1000,"offline test does not wait for real 30 seconds");
});

test("second visible refusal stops; no repeated retry loop",async()=>{
 const {ui}=fixture();
 const signal=new AbortController().signal;
 const refusal={errors:[{provider:"btdigg",code:"BTDIGG_VISIBLE_REFUSAL"}]};
 let calls=0,waits=0;
 const result=await ui.fetchBTDiggWithOneGuardedNewTab(
  "/api/search?providers=btdigg","some title",signal,
  async()=>{calls++;return refusal;},
  async()=>{waits++;});
 assert.equal(result,refusal);
 assert.equal(calls,2);
 assert.equal(waits,1);
});

test("genuine 429, CAPTCHA, transport failure, timeout and normal results NEVER auto retry",async()=>{
 const cases=[
  "RATE_LIMIT","RATE_LIMIT_COOLDOWN","BTDIGG_CAPTCHA_REQUIRED",
  "BTDIGG_TUNNEL_TIMEOUT","BTDIGG_SOURCE_TIMEOUT",
  "BTDIGG_LOCAL_PACING","BTDIGG_VISIBLE_REFUSAL_OTHER"
 ];
 for(const code of cases){
  const {ui}=fixture();
  const data={errors:[{provider:"btdigg",code}]};
  let calls=0;
  const actual=await ui.fetchBTDiggWithOneGuardedNewTab(
   "/api/search?providers=btdigg","title",new AbortController().signal,
   async()=>{calls++;return data;},
   async()=>{throw Error("not allowed");});
  assert.equal(actual,data,code);
  assert.equal(calls,1,code);
 }
 const {ui}=fixture();
 assert.equal(ui.btdiggVisibleRefusalOnly({
  errors:[{provider:"other",code:"BTDIGG_VISIBLE_REFUSAL"}]
 }),false,"never retry another provider");
});

test("cancelled or background iPhone cannot issue deferred source request",async()=>{
 for(const hidden of [true,false]){
  const {ui,document}=fixture();
  const controller=new AbortController();
  if(hidden)document.visibilityState="hidden";
  const refusal={errors:[{provider:"btdigg",code:"BTDIGG_VISIBLE_REFUSAL"}]};
  let calls=0,waits=0;
  const request=async()=>{calls++;return refusal;};
  const pause=async()=>{waits++;controller.abort();};
  const value=await ui.fetchBTDiggWithOneGuardedNewTab(
   "/api/search?providers=btdigg","title",controller.signal,request,pause);
  assert.equal(value,refusal);
  assert.equal(calls,1,"must not send after hidden/cancelled");
  assert.equal(waits,hidden?0:1);
 }
});

test("BTDigg visible source refusal recovery never changes HTTP429 Worker behavior",()=>{
 assert.match(app,/e\.code==="BTDIGG_VISIBLE_REFUSAL"/);
 assert.ok(app.includes("document.visibilityState"));
 assert.ok(app.includes("btdiggCooldownRemainingMs()>0"));
 assert.ok(app.includes("await pause(query,signal,true)"));
 assert.ok(app.includes("return await request(url,{signal});"));
 assert.ok(!/setInterval\([^)]*fetchBTDigg|setTimeout\([^)]*fetchBTDigg/.test(app));
});
