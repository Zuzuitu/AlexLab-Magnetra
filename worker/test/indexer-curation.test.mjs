import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";
import {PROVIDERS} from "../src/catalog.mjs";

const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
function runPicker(saved){
 const storage=new Map(Object.entries(saved||{}).map(([key,value])=>[key,JSON.stringify(value)]));
 const elements=new Map();
 function node(tag="div"){
  return {tag,children:[],listeners:{},textContent:"",value:"",
   append(...children){this.children.push(...children);},
   replaceChildren(...children){this.children=children;},
   addEventListener(name,cb){this.listeners[name]=cb;},
   setAttribute(){},
   classList:{add(){},remove(){},toggle(){}}
  };
 }
 const document={
  addEventListener(){},
  createElement:node,
  getElementById(id){if(!elements.has(id))elements.set(id,node());return elements.get(id);}
 };
 const localStorage={
  getItem:key=>storage.get(key)??null,
  setItem:(key,value)=>storage.set(key,value),
  removeItem:key=>storage.delete(key)
 };
 const context=vm.createContext({document,localStorage});
 vm.runInContext(app+"\nglobalThis.__picker={state,hiddenIndexerIds,preferred,priorityIndexerIds,chooseProviders,selectableProviders,orderedProviders,renderProviders,renderProviderErrors};",context,{filename:"web/app.js"});
 const ui=context.__picker;
 ui.state.providers=PROVIDERS;
 ui.chooseProviders();
 return {ui,elements,storage};
}

test("all 46 original provider IDs remain in backend, 45 are selectable and SubsPlease is excluded",()=>{
 assert.equal(PROVIDERS.length,46);
 const {ui,elements}=runPicker();
 assert.deepEqual([...ui.hiddenIndexerIds],["subsplease"]);
 assert.equal(ui.selectableProviders().length,45);
 ui.renderProviders();
 const rows=elements.get("providerGrid").children;
 const ids=rows.map(row=>row.children[0].children[0].value);
 assert.equal(ids.length,45);
 assert.ok(!ids.includes("subsplease"));
 for(const id of ["bt4g","eztvx","animetosho","mikanproject","fitgirlrepacks"]){
  assert.ok(ids.includes(id),id+" must now appear");
 }
 assert.deepEqual(ids.slice(0,3),["btdigg","torrent9","oxtorrent"]);
 assert.match(elements.get("catalogSummary").textContent,/45 sources available/);
 assert.equal(elements.get("providerCount").textContent,"5/45");
});

test("only SubsPlease is scrubbed from existing iPhone selections and paused sources",()=>{
 const {ui,storage,elements}=runPicker({
  "magnetra.providers.v1":["btdigg","bt4g","subsplease","animetosho"],
  "magnetra.paused-indexers.v1":["subsplease","nyaasi","knaben"]
 });
 assert.deepEqual([...ui.state.selected],["btdigg","bt4g","animetosho"]);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),["btdigg","bt4g","animetosho"]);
 assert.deepEqual([...ui.state.pausedIds],["nyaasi","knaben"]);
 assert.equal(elements.get("providerCount").textContent,"3/45");
});

test("previously selecting only SubsPlease safely falls back to preferred sources",()=>{
 const {ui,storage}=runPicker({"magnetra.providers.v1":["subsplease"]});
 const defaults=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"];
 assert.deepEqual([...ui.state.selected],defaults);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),defaults);
});

test("one Select All control includes all 45 eligible indexers, never SubsPlease",()=>{
 assert.match(app,/\$\("selectAllProviders"\)\.addEventListener\("click",\(\)=>\{\s*const ids=selectableProviders\(\)\.map\(p=>p\.id\)/);
 assert.doesNotMatch(app,/\$\("selectWorking"\)/);
 assert.match(html,/id="selectAllProviders">Selectează toate/);
 assert.doesNotMatch(html,/id="selectWorking"|Selectează sursele verificate/);
 assert.match(html,/Sursele cu erori se dezactivează automat/);
});

test("error panel hides SubsPlease but shows previously hidden indexers",()=>{
 const {ui,elements}=runPicker();
 ui.renderProviderErrors([{provider:"subsplease",message:"Unavailable"}]);
 assert.equal(elements.get("providerErrors").children.length,0);
 ui.renderProviderErrors([
  {provider:"subsplease",message:"Unavailable"},
  {provider:"animetosho",message:"Upstream unavailable"},
  {provider:"btdigg",message:"Temporary timeout"}
 ]);
 const parent=elements.get("providerErrors");
 assert.equal(parent.children.length,1);
 assert.match(parent.children[0].children[0].textContent,/2 source\(s\) unavailable/);
 const data=JSON.stringify(parent);
 assert.doesNotMatch(data,/SubsPlease|subsplease/);
 assert.match(data,/AnimeTosho|animetosho/);
});

test("manual selection persists as-is for reenabled indexers",()=>{
 const {ui,elements,storage}=runPicker({"magnetra.providers.v1":["btdigg","bangumimoe","ytsmx","torrent9"]});
 assert.deepEqual([...ui.state.selected],["btdigg","bangumimoe","ytsmx","torrent9"]);
 ui.renderProviders();
 const ids=elements.get("providerGrid").children.map(row=>row.children[0].children[0].value);
 assert.equal(ids.length,45);
 assert.ok(ids.includes("ytsmx"));
 assert.ok(ids.includes("bangumimoe"));
 assert.ok(!ids.includes("subsplease"));
 assert.equal(JSON.parse(storage.get("magnetra.providers.v1")).length,4);
});
