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
 const context=vm.createContext({document,localStorage,setTimeout:()=>1,clearTimeout:()=>{}});
 vm.runInContext(app+"\nglobalThis.__picker={state,hiddenIndexerIds,preferred,priorityIndexerIds,chooseProviders,selectableProviders,orderedProviders,renderProviders,renderProviderErrors,toggleAllProviders,updateSelectAllButton};",context,{filename:"web/app.js"});
 const ui=context.__picker;
 ui.state.providers=PROVIDERS;
 ui.chooseProviders();
 return {ui,elements,storage};
}


test("curated 11 picker restores all 34 previous hidden IDs plus SubsPlease",()=>{
 assert.equal(PROVIDERS.length,46);
 const {ui,elements}=runPicker();
 assert.equal(ui.hiddenIndexerIds.size,35);
 for(const id of ["subsplease","bt4g","eztvx","animetosho","mikanproject","fitgirlrepacks"])assert.ok(ui.hiddenIndexerIds.has(id),id);
 assert.equal(ui.selectableProviders().length,11);
 ui.renderProviders();
 const ids=elements.get("providerGrid").children.map(row=>row.children[0].children[0].value);
 assert.equal(ids.length,11);
 assert.deepEqual(ids.slice(0,3),["btdigg","torrent9","oxtorrent"]);
 assert.ok(!ids.includes("subsplease"));
 assert.match(elements.get("catalogSummary").textContent,/11 sources available/);
 assert.equal(elements.get("providerCount").textContent,"5/11");
});

test("migrates iPhone selected and paused lists without reintroducing hidden sources",()=>{
 const {ui,storage,elements}=runPicker({
  "magnetra.providers.v1":["btdigg","bt4g","subsplease","animetosho","torrent9"],
  "magnetra.paused-indexers.v1":["subsplease","nyaasi","knaben"]
 });
 assert.deepEqual([...ui.state.selected],["btdigg","torrent9"]);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),["btdigg","torrent9"]);
 assert.deepEqual([...ui.state.pausedIds],["knaben"]);
 assert.equal(elements.get("providerCount").textContent,"2/11");
});

test("legacy hidden-only selection recovers defaults but explicit saved [] stays empty",()=>{
 const a=runPicker({"magnetra.providers.v1":["subsplease","bt4g"]});
 assert.deepEqual([...a.ui.state.selected],["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"]);
 const b=runPicker({"magnetra.providers.v1":[]});
 assert.equal(b.ui.state.selected.size,0);
 assert.equal(b.elements.get("providerCount").textContent,"0/11");
 assert.equal(b.elements.get("selectAllProviders").textContent,"Select all available");
});

test("select/deselect all toggle persists even across picker initialization",()=>{
 const {ui,storage,elements}=runPicker();
 assert.equal(elements.get("selectAllProviders").textContent,"Select all available");
 ui.toggleAllProviders();
 assert.equal(ui.state.selected.size,11);
 assert.equal(elements.get("selectAllProviders").textContent,"Deselect all available");
 assert.equal(elements.get("providerCount").textContent,"11/11");
 ui.toggleAllProviders();
 assert.equal(ui.state.selected.size,0);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),[]);
 assert.equal(elements.get("selectAllProviders").textContent,"Select all available");
 ui.chooseProviders();
 assert.equal(ui.state.selected.size,0);
 ui.toggleAllProviders();
 assert.equal(ui.state.selected.size,11);
 assert.doesNotMatch(app,/\$\("selectWorking"\)/);
 assert.match(html,/id="selectAllProviders">Selectează toate/);
});

test("per-indexer checkbox changes also update dynamic bulk label",()=>{
 const {ui,elements}=runPicker();
 ui.toggleAllProviders();ui.renderProviders();
 const input=elements.get("providerGrid").children[0].children[0].children[0];
 input.checked=false;input.listeners.change();
 assert.equal(ui.state.selected.size,10);
 assert.equal(elements.get("selectAllProviders").textContent,"Select all available");
 input.checked=true;input.listeners.change();
 assert.equal(ui.state.selected.size,11);
 assert.equal(elements.get("selectAllProviders").textContent,"Deselect all available");
});

test("error panels and saved preferences exclude previously hidden adapters",()=>{
 const {ui,elements,storage}=runPicker({"magnetra.providers.v1":["btdigg","bangumimoe","ytsmx","torrent9"]});
 assert.deepEqual([...ui.state.selected],["btdigg","torrent9"]);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),["btdigg","torrent9"]);
 ui.renderProviderErrors([
  {provider:"subsplease",message:"Unavailable"},
  {provider:"animetosho",message:"Unreachable"},
  {provider:"btdigg",message:"Temporary timeout"}
 ]);
 const visible=JSON.stringify(elements.get("providerErrors"));
 assert.doesNotMatch(visible,/SubsPlease|subsplease|AnimeTosho|animetosho/);
 assert.match(visible,/1 source\(s\) unavailable/);
});
