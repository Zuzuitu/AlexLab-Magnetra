import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

// Real client function evaluated unmodified; no simulated source selector.
const app = readFileSync(new URL("../../web/app.js", import.meta.url),"utf8");
const details="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
const mismatchingSource="https://therarbg.com/not-a-detail-view?src=listing";
const VALID_MAGNET="magnet:?xt=urn:btih:"+"a".repeat(40);

function harness(optin=false) {
 const requests=[];
 const sandbox={
  document:{addEventListener(){}},
  location:{search:optin?"?magnetra_diag=1":"",hash:"",pathname:"/"},
  URLSearchParams,
  fetch:async(path,options={})=>{
   requests.push({path,options,body:options.body?JSON.parse(options.body):null});
   return {ok:true,status:200,json:async()=>({provider:"therarbag",magnet:VALID_MAGNET})};
  }
 };
 vm.createContext(sandbox);
 vm.runInContext(app,sandbox,{timeout:1500});
 async function resolve(item){
  sandbox.__selectedItem={...item};
  return await vm.runInContext("ensureMagnet(__selectedItem)",sandbox,{timeout:1500});
 }
 return {requests,resolve};
}

test("iPhone evidence: TheRarBg chooses original details ahead of different magnetSource",async()=>{
 const h=harness(true);
 const magnet=await h.resolve({
  id:"therarbag:352mb",provider:"therarbag",name:"Original source result",
  details,magnetSource:mismatchingSource,magnet:null
 });
 assert.equal(magnet,VALID_MAGNET);
 assert.equal(h.requests.length,1);
 assert.equal(h.requests[0].path,"/api/resolve");
 assert.deepEqual(h.requests[0].body,{provider:"therarbag",details});
 assert.equal(h.requests[0].options.headers["x-magnetra-resolve-diagnostic"],
              "owner-opt-in-20261024-v1");
 assert.notEqual(h.requests[0].body.details,mismatchingSource);
});

test("TheRarBg default mode uses same correct details but sends no diagnostic header",async()=>{
 const h=harness();
 await h.resolve({id:"x",provider:"therarbag",details,magnetSource:mismatchingSource});
 assert.deepEqual(h.requests[0].body,{provider:"therarbag",details});
 assert.equal(h.requests[0].options.headers["x-magnetra-resolve-diagnostic"],undefined);
});

test("OxTorrent and Torrent9 keep their previously fixed details-first behavior",async()=>{
 for(const provider of ["oxtorrent","torrent9"]){
  const h=harness();
  await h.resolve({id:"x",provider,details,magnetSource:mismatchingSource});
  assert.deepEqual(h.requests[0].body,{provider,details},provider);
 }
});

test("other indexers still prefer magnetSource exactly as previously",async()=>{
 for(const provider of ["1337x","torrent9x","torrentz"]){
  const h=harness();
  await h.resolve({id:"x",provider,details,magnetSource:mismatchingSource});
  assert.deepEqual(h.requests[0].body,{provider,details:mismatchingSource},provider);
 }
});

test("TheRarBg refuses magnetSource-only result; does not request noncanonical URL",async()=>{
 const h=harness(true);
 await assert.rejects(h.resolve({id:"x",provider:"therarbag",details:null,magnetSource:mismatchingSource}));
 assert.equal(h.requests.length,0);
});

test("already resolved magnet remains usable without another source fetch",async()=>{
 const h=harness(true);
 const result=await h.resolve({id:"x",provider:"therarbag",details,magnetSource:mismatchingSource,magnet:VALID_MAGNET});
 assert.equal(result,VALID_MAGNET);
 assert.equal(h.requests.length,0);
});
