import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

const js=readFileSync(new URL("../../web/i18n.js",import.meta.url),"utf8");
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const sw=readFileSync(new URL("../../web/sw.js",import.meta.url),"utf8");

function runtime(stored=""){
 const store=new Map(stored?[["magnetra.language.v1",stored]]:[]);
 const listeners={};
 const nodes=[
  {textContent:"Search results"},
  {textContent:"  Find what you need.  "},
  {textContent:"Check Shield connection"}
 ];
 let index=0;
 const sel={value:"",attrs:{},setAttribute(k,v){this.attrs[k]=v}};
 const input={getAttribute(a){return a==="placeholder"?"Search torrents...":null},
  setAttribute(a,v){this.value=v}};
 const document={
  body:{},
  documentElement:{lang:""},
  getElementById(id){return id==="languageSelect"?sel:null},
  addEventListener(type,callback){listeners[type]=callback},
  createTreeWalker(){index=0;return {nextNode(){return nodes[index++]||null}}},
  querySelectorAll(){return [input]}
 };
 const storage={
  getItem(key){return store.get(key)||null},
  setItem(key,value){store.set(key,value)}
 };
 const sandbox={document,localStorage:storage,NodeFilter:{SHOW_TEXT:4}};
 sandbox.window=sandbox;
 vm.runInNewContext(js,sandbox,{filename:"web/i18n.js",timeout:1500});
 listeners.DOMContentLoaded();
 return {lang:sandbox.MagnetraI18n,nodes,document,sel,input,store};
}
test("Romanian is default and all public HTML is tagged Romanian",()=>{
 const r=runtime();
 assert.equal(r.lang.language,"ro");
 assert.equal(r.document.documentElement.lang,"ro");
 assert.equal(r.nodes[0].textContent,"Rezultatele căutării");
 assert.equal(r.nodes[1].textContent,"  Găsește ce cauți.  ");
 assert.equal(r.input.value,"Caută torrente...");
 assert.equal(r.sel.value,"ro");
 assert.match(html,/<html lang="ro">/);
 assert.match(html,/src="\/i18n\.js"/);
});
test("Italian persists, Romanian restores; unsupported third language rejected",()=>{
 const r=runtime("it");
 assert.equal(r.lang.language,"it");
 assert.equal(r.nodes[0].textContent,"Risultati della ricerca");
 assert.equal(r.input.value,"Cerca torrent...");
 assert.equal(r.lang.t("Searching {n} indexers…",{n:5}),"Ricerca in 5 fonti…");
 assert.equal(r.lang.set("en"),false);
 assert.equal(r.lang.language,"it");
 assert.equal(r.lang.set("ro"),true);
 assert.equal(r.nodes[0].textContent,"Rezultatele căutării");
 assert.equal(r.store.get("magnetra.language.v1"),"ro");
});
test("every translation maps only Romanian and Italian and updates interpolations",()=>{
 const r=runtime();
 const dict=r.lang.dictionary;
 assert.ok(Object.keys(dict).length>=145);
 for(const [key,val] of Object.entries(dict)){
  assert.ok(val.ro?.trim(),key+": RO missing");
  assert.ok(val.it?.trim(),key+": IT missing");
  assert.deepEqual(Object.keys(val).sort(),["it","ro"]);
 }
 assert.equal(r.lang.t("{n} sources available",{n:12}),"12 surse disponibile");
 assert.equal(r.lang.set("it"),true);
 assert.equal(r.lang.t("{n} sources available",{n:12}),"12 fonti disponibili");
});
test("public UI removes source session/test diagnostics without removing operational safety",()=>{
 assert.doesNotMatch(html,/RESULTS THIS SESSION|19 repeatedly failing|historical, not live uptime|Test Shield connection/);
 assert.doesNotMatch(app,/RESULTS THIS SESSION|0 THIS SESSION|NOT AUDITED|RESULTS IN AUDIT|Diagnostic: /);
 assert.match(app,/const hiddenIndexerIds=new Set/);
 assert.match(app,/const valid=new Set\(selectableProviders\(\)\.map\(p=>p\.id\)\)/);
 assert.match(app,/const visibleFailures=failures\.filter\(f=>!hiddenIndexerIds\.has\(f\.provider\)\)/);
 assert.match(sw,/\/i18n\.js/);
 assert.match(html,/id="languageSelect"/);
 assert.equal((html.match(/<option value="(?:ro|it)">/g)||[]).length,2);
});
