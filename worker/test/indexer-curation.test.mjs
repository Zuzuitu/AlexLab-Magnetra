import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";
import {PROVIDERS} from "../src/catalog.mjs";

// Exercise the actual PWA script, not a parallel implementation of its picker.
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const excluded=[
 "anirena","bt4g","bitsearch","extdotto","eztvx","filemood",
 "limetorrents","nyaasi","1337x","tokyotoshokan","torrentdatabase",
 "torrentdownloadinfo","torrentdownloads","torrentkitty","uindex",
 "xxxclub","torrentz","animetosho","mikanproject"
];
function runPicker(saved){
 const storage=new Map(Object.entries(saved||{}).map(([key,value])=>[key,JSON.stringify(value)]));
 const elements=new Map();
 function node(tag="div"){
  return {tag,children:[],listeners:{},textContent:"",value:"",
   append(...children){this.children.push(...children);},
   replaceChildren(...children){this.children=children;},
   addEventListener(name,cb){this.listeners[name]=cb;},
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
test("catalog keeps all 46 real adapter IDs; exactly 19 owner-named indexers hidden",()=>{
 assert.equal(PROVIDERS.length,46);
 const {ui,elements}=runPicker();
 assert.deepEqual([...ui.hiddenIndexerIds].sort(),excluded.slice().sort());
 assert.equal(ui.selectableProviders().length,27);
 ui.renderProviders();
 const rows=elements.get("providerGrid").children;
 const ids=rows.map(row=>row.children[0].children[0].value);
 assert.equal(ids.length,27);
 for(const id of excluded)assert.ok(!ids.includes(id),id+" must not be selectable");
 assert.deepEqual(ids.slice(0,3),["btdigg","torrent9","oxtorrent"]);
 assert.ok(!ui.priorityIndexerIds.includes("eztvx"));
 assert.match(elements.get("catalogSummary").textContent,/27 selectable indexers/);
 assert.equal(elements.get("providerCount").textContent,"5/27");
});
test("hidden IDs in iPhone localStorage are scrubbed, visible custom choices retained",()=>{
 const before=["btdigg","torrent9","anirena","eztvx","torrentz","torrentdownloadinfo","animetosho","mikanproject"];
 const {ui,storage,elements}=runPicker({
  "magnetra.providers.v1":before,
  "magnetra.paused-indexers.v1":["bt4g","nyaasi","knaben","mikanproject"]
 });
 assert.deepEqual([...ui.state.selected],["btdigg","torrent9"]);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),["btdigg","torrent9"]);
 assert.deepEqual([...ui.state.pausedIds],["knaben"]);
 assert.equal(elements.get("providerCount").textContent,"2/27");
 assert.doesNotMatch(elements.get("sourceHealthSummary").textContent,/3 failed/);
});
test("old all-hidden saved selection falls back to BTDigg plus usable defaults",()=>{
 const {ui,storage}=runPicker({"magnetra.providers.v1":excluded});
 assert.deepEqual([...ui.state.selected],["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"]);
 assert.deepEqual(JSON.parse(storage.get("magnetra.providers.v1")),[...ui.state.selected]);
});
test("bulk actions, fallback and UI copy only reference selectable indexers",()=>{
 assert.match(app,/\$\("selectAllProviders"\)\.addEventListener\("click",\(\)=>\{\s*const ids=selectableProviders\(\)\.map\(p=>p\.id\)/);
 assert.match(app,/\$\("selectWorking"\)\.addEventListener\("click",\(\)=>\{\s*const ids=orderedProviders\(selectableProviders\(\)\)/);
 assert.match(app,/const live=orderedProviders\(selectableProviders\(\)\)/);
 assert.match(html,/id="selectAllProviders">Select all available/);
 assert.doesNotMatch(html,/Select all 46/);
 assert.match(html,/19 repeatedly failing sources are hidden/);
});

test("unavailable panel excludes AnimeTosho and Mikan and disappears if only they failed",()=>{
 const {ui,elements}=runPicker();
 ui.renderProviderErrors([
  {provider:"animetosho",message:"Upstream unavailable"},
  {provider:"mikanproject",message:"Provider could not complete search"}
 ]);
 assert.equal(elements.get("providerErrors").children.length,0,
  "no warning or alternatives panel if only hidden indexers failed");
 ui.renderProviderErrors([
  {provider:"animetosho",message:"Upstream unavailable"},
  {provider:"mikanproject",message:"Provider could not complete search"},
  {provider:"btdigg",message:"Temporary BTDigg timeout"}
 ]);
 const parent=elements.get("providerErrors");
 assert.equal(parent.children.length,1);
 const details=parent.children[0];
 assert.match(details.children[0].textContent,/1 indexer unavailable/);
 const text=JSON.stringify(details);
 assert.doesNotMatch(text,/AnimeTosho|Mikan|animetosho|mikanproject/);
 assert.match(text,/BTDigg/);
});
