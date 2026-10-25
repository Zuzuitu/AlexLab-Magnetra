import test from "node:test";
import assert from "node:assert/strict";
import {createVerifiedSourceCache,FRESH_MS,STALE_MAX_MS} from "../src/verified-source-cache.mjs";

test("same original source and exact query only; no cross-provider substitution",async()=>{
 let now=0,n=0;const cache=createVerifiedSourceCache(()=>now);
 const source=async()=>{n++;return [{name:"Ubuntu",id:"thepiratebay:1",provider:"thepiratebay",magnet:"magnet:?xt=urn:btih:"+("a".repeat(40))}];};
 const first=await cache.search("thepiratebay","ubuntu","all",source);
 first.items[0].name="mutated caller";
 now=1_000;const warm=await cache.search("thepiratebay","ubuntu","all",source);
 assert.equal(n,1);assert.equal(warm.items[0].name,"Ubuntu");assert.equal(warm.cache.mode,"fresh");
 await cache.search("thepiratebay","ubuntu","movies",source);
 await cache.search("btdigg","ubuntu","all",source);
 assert.equal(n,3);
});
test("only positive verified records survive one failure with explicit stale flag",async()=>{
 let now=0,requests=0;const c=createVerifiedSourceCache(()=>now);
 const src=async()=>{requests++;if(requests>1)throw Error("upstream HTTP 504");return [{id:"btdigg:1",name:"genuine",provider:"btdigg"}];};
 await c.search("btdigg","ubuntu","all",src);
 now=FRESH_MS+1;
 const result=await c.search("btdigg","ubuntu","all",src);
 assert.equal(result.cache.mode,"stale");
 assert.equal(requests,2,"never automatically retries");
 now=STALE_MAX_MS+1;
 await assert.rejects(()=>c.search("btdigg","ubuntu","all",src),/504/);
});
test("empty, never-seen, different-source queries never use synthetic cache",async()=>{
 let now=0;const c=createVerifiedSourceCache(()=>now);
 await c.search("thepiratebay","notfound","all",async()=>[]);
 now=FRESH_MS+1;
 await assert.rejects(()=>c.search("thepiratebay","notfound","all",async()=>{throw Error("429");}),/429/);
 await assert.rejects(()=>c.search("btdigg","notfound","all",async()=>{throw Error("504");}),/504/);
});
test("single flight deduplicates identical inflight requests within one isolate",async()=>{
 let calls=0,finish;const c=createVerifiedSourceCache(()=>0);
 const src=()=>{calls++;return new Promise(r=>finish=r);};
 const one=c.search("thepiratebay","ubuntu","all",src);
 const two=c.search("thepiratebay","ubuntu","all",src);
 finish([{id:"t",name:"original"}]);
 assert.equal((await Promise.all([one,two])).length,2);
 assert.equal(calls,1);
});
test("unrelated provider traffic is unaffected by cache",async()=>{
 const c=createVerifiedSourceCache(()=>0);let calls=0;
 const f=async()=>{calls++;return [{id:"knaben:1",name:"original"}];};
 await c.search("knaben","ubuntu","all",f);
 await c.search("knaben","ubuntu","all",f);
 assert.equal(calls,2);
});

test("a confirmed source-empty response retires its former positive cache",async()=>{
 let now=0;const c=createVerifiedSourceCache(()=>now);
 await c.search("thepiratebay","ubuntu","all",async()=>[{id:"tpb:1",name:"original"}]);
 now=FRESH_MS+2;
 const empty=await c.search("thepiratebay","ubuntu","all",async()=>[]);
 assert.equal(empty.items.length,0);
 now+=1;
 await assert.rejects(()=>c.search("thepiratebay","ubuntu","all",async()=>{throw Error("provider HTTP 504")}),/504/);
});
