import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import vm from "node:vm";

const root=resolve(dirname(fileURLToPath(import.meta.url)),"../..");
const source=readFileSync(resolve(root,"web/app.js"),"utf8");
const html=readFileSync(resolve(root,"web/index.html"),"utf8");

function harness(){
 const storage=new Map();
 const dom=new Map();
 function element(){
  return {textContent:"",value:"",disabled:false,className:"",
   classList:{add(){},remove(){},toggle(){}},style:{},
   replaceChildren(){},append(){},addEventListener(){},setAttribute(){},title:""};
 }
 const document={
  getElementById(id){
   if(!dom.has(id))dom.set(id,element());
   return dom.get(id);
  },
  createElement(){return element()},
  addEventListener(){},
  querySelectorAll(){return []}
 };
 const localStorage={
  setItem(k,v){storage.set(k,String(v))},
  getItem(k){return storage.has(k)?storage.get(k):null},
  removeItem(k){storage.delete(k)}
 };
 const sandbox={document,localStorage,URL,URLSearchParams,console,Set,Map,Date};
 vm.runInNewContext(source+
   "\nglobalThis.__policy={state,pausedFromFailures,pauseFailedSources,chooseProviders,unpauseSources};",
   sandbox,{filename:"web/app.js",timeout:1000});
 return {...sandbox.__policy,storage,dom};
}

test("screenshot failure mix: only actual API errors are paused; healthy zero results retained",()=>{
 const h=harness();
 const ids=["knaben","torrentscsv","torrent9","oxtorrent","ytsmx","btdigg"];
 const selected=new Set(ids);
 const actual=[{provider:"torrent9",code:"TIMEOUT"},
  {provider:"oxtorrent",code:"TIMEOUT"},
  {provider:"btdigg",code:"RATE_LIMIT"}];
 const paused=h.pausedFromFailures(ids,actual,selected);
 assert.deepEqual([...paused].sort(),["btdigg","oxtorrent","torrent9"]);
 assert.equal(selected.has("ytsmx"),true,"do not mutate input");
});

test("completed search pauses failures persistently without touching bookmarks or Flud pairing",()=>{
 const h=harness();
 const providers=["knaben","torrentscsv","torrent9","internetarchive"];
 h.state.providers=providers.map(id=>({id,name:id,ported:true}));
 h.state.selected=new Set(providers);
 h.storage.set("magnetra.bookmarks.v1",JSON.stringify({sample:"bookmark"}));
 h.storage.set("magnetra.companion.v1",JSON.stringify({deviceId:"unchanged"}));
 const n=h.pauseFailedSources(providers,[{provider:"torrent9",code:"TIMEOUT"}]);
 assert.equal(n,1);
 assert.deepEqual([...h.state.selected].sort(),["internetarchive","knaben","torrentscsv"]);
 assert.equal(h.storage.get("magnetra.providers.v1"),JSON.stringify(["knaben","torrentscsv","internetarchive"]));
 assert.equal(h.storage.get("magnetra.paused-indexers.v1"),JSON.stringify(["torrent9"]));
 assert.match(h.dom.get("sourceHealthSummary").textContent,/1 failed indexer\(s\) paused/);
 assert.equal(h.storage.get("magnetra.bookmarks.v1"),JSON.stringify({sample:"bookmark"}));
 assert.equal(h.storage.get("magnetra.companion.v1"),JSON.stringify({deviceId:"unchanged"}));
});

test("never zero all selected sources on broad outage",()=>{
 const h=harness();
 const selected=new Set(["knaben","torrentscsv"]);
 assert.deepEqual([...h.pausedFromFailures(["knaben","torrentscsv"],
  [{provider:"knaben"},{provider:"torrentscsv"}],selected)],[]);
});

test("failures unrelated to the completed set cannot pause unsearched sources",()=>{
 const h=harness();
 const selected=new Set(["knaben","torrent9","ytsmx"]);
 assert.deepEqual([...h.pausedFromFailures(["knaben","ytsmx"],[
  {provider:"torrent9",code:"TIMEOUT"},
  {provider:"unknown",code:"TIMEOUT"}
 ],selected)],[]);
});

test("user can restore a paused source without re-running a blocked upstream test",()=>{
 const h=harness();
 h.state.providers=["knaben","torrent9"].map(id=>({id,name:id,ported:true}));
 h.state.selected=new Set(["knaben","torrent9"]);
 assert.equal(h.pauseFailedSources(["knaben","torrent9"],[{provider:"torrent9"}]),1);
 h.state.selected.add("torrent9");
 h.unpauseSources(["torrent9"]);
 assert.deepEqual([...h.state.pausedIds],[]);
 assert.equal(h.storage.get("magnetra.paused-indexers.v1"),"[]");
});

test("paused provider metadata survives browser restart, while manual selection takes precedence",()=>{
 const h=harness();
 h.state.providers=["knaben","torrentscsv","torrent9","ytsmx","btdigg"]
  .map(id=>({id,name:id,ported:true}));
 h.storage.set("magnetra.providers.v1",JSON.stringify(["knaben","ytsmx"]));
 h.storage.set("magnetra.paused-indexers.v1",JSON.stringify(["torrent9","ytsmx"]));
 h.chooseProviders();
 assert.deepEqual([...h.state.selected].sort(),["knaben"]);
 assert.deepEqual([...h.state.pausedIds],["torrent9"]);
 assert.match(h.dom.get("sourceHealthSummary").textContent,/1 failed indexer\(s\)/);
});

test("no automatic remote probing, query changes or source deletions",()=>{
 assert.match(source,/const paused=pauseFailedSources\(ids,failures\);/);
 assert.match(source,/if\(!controller\.signal\.aborted\)\{\s*const paused=pauseFailedSources/);
 assert.match(source,/save\(STORAGE\.selected,\[\.\.\.state\.selected\]\)/);
 assert.match(source,/pauseFailedSources\(ids,failures\)/);
 assert.match(source,/unpauseSources\(ids\)/);
 assert.match(source,/state\.selected=new Set\(ids\)/);
 assert.match(html,/id="sourceHealthSummary"/);
 assert.match(source,/FRESH_ASSETS|btdiggPacing|BTDIGG_MIN_GAP_MS/);
});
