import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import {readFileSync} from "node:fs";
import {legacySearch,validateLegacyDetail} from "../src/legacy-adapters.mjs";

const original="https://nnmclub.to/forum/viewtopic.php?t=1896364";
const falseAux="https://nnmclub.to/forum/undefined";
const magnet="magnet:?xt=urn:btih:"+"a".repeat(40);

// Exercise the actual NoNameClub search adapter. This source defines
// details and torrentFile but no magnetSource selector at all.
test("NoNameClub missing optional source anchor never becomes /undefined",async()=>{
 const previous=globalThis.HTMLRewriter;
 try {
  globalThis.HTMLRewriter=class {
   constructor(){this.callbacks=[];}
   on(selector,callback){this.callbacks.push([selector,callback]);return this;}
   transform(response){return {text:async()=>{
    await response.text();
    this.callbacks[0][1].element({});
    for(const [selector,handler] of this.callbacks.slice(1)){
     if(selector.includes("viewtopic.php?t=")&&handler.element){
      handler.element({getAttribute(name){return name==="href"?"viewtopic.php?t=1896364":null;}});
     }else if(selector.includes("download.php?id=")&&handler.element){
      handler.element({getAttribute(){return null;}});
     }else if(selector.includes(" a[href^='viewtopic.php?t='] b")&&handler.text){
      handler.text({text:"Lupin fixture",lastInTextNode:true});
     }
    }
    return "";
   }};}
  };
  const records=await legacySearch("nonameclub","Lupin","all",async()=>new Response("<html></html>",{headers:{"content-type":"text/html"}}));
  assert.equal(records.length,1);
  assert.equal(records[0].details,original);
  assert.equal(records[0].magnetSource,null);
  assert.equal(records[0].torrentFile,null);
  assert.notEqual(records[0].magnetSource,falseAux);
 } finally{globalThis.HTMLRewriter=previous;}
});

test("NoNameClub missing or empty optional external URL cannot be a permitted detail",()=>{
 for(const value of [null,undefined,"","  "]){
  assert.equal(validateLegacyDetail("nonameclub",value),null);
 }
 assert.equal(validateLegacyDetail("nonameclub",original),original);
 assert.equal(validateLegacyDetail("nonameclub","https://evil.example/admin"),null);
});

// Exercise production ensureMagnet(), not a reimplementation. Distinguish
// an old cached false auxiliary source from the valid original detail URL.
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
function harness(){
 const calls=[];
 const box={
  document:{addEventListener(){}},location:{search:"",hash:"",pathname:"/"},URLSearchParams,
  fetch:async(path,opts={})=>{
   const body=JSON.parse(opts.body);
   calls.push({path,body});
   if(body.details!==original){
    return {ok:false,status:502,json:async()=>({error:"provider details page contains no supported magnet link"})};
   }
   return {ok:true,status:200,json:async()=>({magnet})};
  }
 };
 vm.createContext(box);
 vm.runInContext(app,box,{timeout:1500});
 return {calls,resolve:async item=>{
  box.item={...item};
  return vm.runInContext("ensureMagnet(item)",box,{timeout:1500});
 }};
}
test("NoNameClub owner exact card uses source-owned details despite cached fake auxiliary",async()=>{
 const h=harness();
 assert.equal(await h.resolve({provider:"nonameclub",details:original,magnetSource:falseAux,magnet:null}),magnet);
 assert.equal(h.calls.length,1);
 assert.equal(h.calls[0].path,"/api/resolve");
 assert.deepEqual(h.calls[0].body,{provider:"nonameclub",details:original});
});

test("NoNameClub without original details fails closed rather than request false auxiliary",async()=>{
 const h=harness();
 await assert.rejects(h.resolve({provider:"nonameclub",details:null,magnetSource:falseAux,magnet:null}),/no supported magnet/i);
 assert.equal(h.calls.length,0);
});
