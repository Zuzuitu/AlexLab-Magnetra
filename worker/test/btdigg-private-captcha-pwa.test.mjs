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
   openBTDiggVerification,finishBTDiggVerification,
 };
 `,sandbox,{filename:"web/app.js"});
 return {ui:sandbox.test,element,store};
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
 assert.match(frame.src,/^https:\/\/rock64\.tailc14d25\.ts\.net:8444\/vnc\.html\?/);
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
