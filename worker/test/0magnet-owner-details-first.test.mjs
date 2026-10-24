import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

// Exercise the REAL production PWA ensureMagnet() via VM, not an imitation.
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const ownerDetails="https://9mag.net/!lxbV";
const auxiliary="https://9mag.net/!different-listing-aux";
const validMagnet="magnet:?xt=urn:btih:"+"a".repeat(40);

function harness() {
 const requests=[];
 const sandbox={
  document:{addEventListener(){}},
  location:{search:"",hash:"",pathname:"/"},
  URLSearchParams,
  fetch:async(path,options={})=>{
   const data=options.body?JSON.parse(options.body):null;
   requests.push({path,options,data});
   // A deliberately noncanonical source MUST fail the API to surface
   // the same class of issue as the real iPhone; original details passes.
   if(data?.details!==ownerDetails && data?.provider==="0magnet")
     return {ok:false,status:502,json:async()=>({error:"Provider could not resolve magnet: provider details page contains no supported magnet link"})};
   return {ok:true,status:200,json:async()=>({provider:data?.provider,magnet:validMagnet})};
  }
 };
 vm.createContext(sandbox);
 vm.runInContext(app,sandbox,{timeout:1500});
 return {
  requests,
  resolve:async item=>{
   sandbox.__ownerItem={...item};
   return vm.runInContext("ensureMagnet(__ownerItem)",sandbox,{timeout:1500});
  }
 };
}

test("0Magnet exact owner URL chooses original details despite auxiliary magnetSource",async()=>{
 const h=harness();
 const returned=await h.resolve({id:"0magnet:owner",name:"Owner matched release",provider:"0magnet",
   details:ownerDetails,magnetSource:auxiliary,magnet:null});
 assert.equal(returned,validMagnet);
 assert.equal(h.requests.length,1);
 assert.equal(h.requests[0].path,"/api/resolve");
 assert.deepEqual(h.requests[0].data,{provider:"0magnet",details:ownerDetails});
 assert.notEqual(h.requests[0].data.details,auxiliary);
});

test("0Magnet refuses to fall back to ambiguous auxiliary when original details missing",async()=>{
 const h=harness();
 await assert.rejects(h.resolve({id:"0magnet:missing",provider:"0magnet",details:null,
    magnetSource:auxiliary,magnet:null}),/Provider has no supported magnet/);
 assert.equal(h.requests.length,0);
});

test("0Magnet cached real magnet bypasses any unnecessary network resolution",async()=>{
 const h=harness();
 assert.equal(await h.resolve({id:"0magnet:ready",provider:"0magnet",details:ownerDetails,
    magnetSource:auxiliary,magnet:validMagnet}),validMagnet);
 assert.equal(h.requests.length,0);
});

test("TheRarBg, OxTorrent, Torrent9 retain their proven details-first logic",async()=>{
 for(const provider of ["therarbag","oxtorrent","torrent9"]){
  const h=harness();
  await h.resolve({id:provider+":owner",provider,details:ownerDetails,magnetSource:auxiliary,magnet:null});
  assert.deepEqual(h.requests[0].data,{provider,details:ownerDetails},provider);
 }
});

test("other original indexers keep their existing magnetSource-first precedence",async()=>{
 for(const provider of ["1337x","torrentz","torrent9x"]){
  const h=harness();
  await h.resolve({id:provider+":owner",provider,details:ownerDetails,magnetSource:auxiliary,magnet:null});
  assert.deepEqual(h.requests[0].data,{provider,details:auxiliary},provider);
 }
});
