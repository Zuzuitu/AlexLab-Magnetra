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


test("TPB HTTP 429 pauses all TPB queries in one isolate until Retry-After expiry",async()=>{
 let now=0,calls=0;
 const c=createVerifiedSourceCache(()=>now);
 const limited=async()=>{calls++;const err=Error("provider HTTP 429");err.retryAfterMs=30_000;throw err;};
 await assert.rejects(()=>c.search("thepiratebay","first","all",limited),/429/);
 now=29_999;
 await assert.rejects(()=>c.search("thepiratebay","second","movies",limited),/429/);
 assert.equal(calls,1,"cooldown must not contact original upstream for a different term");
 now=30_001;
 await assert.rejects(()=>c.search("thepiratebay","second","movies",limited),/429/);
 assert.equal(calls,2,"upstream may be contacted once the real deadline expires");
});

test("TPB 429 with an exact cached positive is stale, not fresh or borrowed",async()=>{
 let now=0,calls=0;
 const c=createVerifiedSourceCache(()=>now);
 await c.search("thepiratebay","ubuntu","all",async()=>[{id:"thepiratebay:1",name:"real",provider:"thepiratebay"}]);
 now=FRESH_MS+1;
 const limited=async()=>{calls++;throw Error("provider HTTP 429");};
 const first=await c.search("thepiratebay","ubuntu","all",limited);
 assert.equal(first.cache.mode,"stale");
 assert.equal(calls,1);
 now+=10_000;
 const still=await c.search("thepiratebay","ubuntu","all",limited);
 assert.equal(still.cache.mode,"stale");
 assert.equal(calls,1,"do not recontact upstream within default cooldown");
 await assert.rejects(()=>c.search("thepiratebay","different","all",limited),/429/);
 assert.equal(calls,1,"different search must not receive another query's cached results");
 now+=60_001;
 await assert.rejects(()=>c.search("thepiratebay","different","all",limited),/429/);
 assert.equal(calls,2);
});

test("TPB 403, timeout and 5xx do not create a 429 cooldown; BTDigg remains separate",async()=>{
 let now=0,tpbCalls=0,btdiggCalls=0;
 const c=createVerifiedSourceCache(()=>now);
 for(const error of ["provider HTTP 403","provider HTTP 503","TimeoutError"]){
  await assert.rejects(()=>c.search("thepiratebay","a"+tpbCalls,"all",async()=>{
   tpbCalls++;throw Error(error);
  }));
 }
 assert.equal(tpbCalls,3);
 await assert.rejects(()=>c.search("thepiratebay","limited","all",async()=>{throw Error("provider HTTP 429")}),/429/);
 await c.search("btdigg","ubuntu","all",async()=>{btdiggCalls++;return [{id:"btdigg:1",name:"original"}];});
 assert.equal(btdiggCalls,1);
 now+=60_001;
 await c.search("thepiratebay","recovered","all",async()=>{tpbCalls++;return [];});
 assert.equal(tpbCalls,4);
});

test("TPB 429 cooldown is bounded and never becomes permanent",async()=>{
 let now=0,calls=0;
 const c=createVerifiedSourceCache(()=>now);
 await assert.rejects(()=>c.search("thepiratebay","ubuntu","all",async()=>{
  calls++;const e=Error("provider HTTP 429");e.retryAfterMs=8*60*60_000;throw e;
 }),/429/);
 now=5*60_000-1;
 await assert.rejects(()=>c.search("thepiratebay","new","all",async()=>{calls++;return [];}),/429/);
 assert.equal(calls,1);
 now=5*60_000+1;
 assert.deepEqual((await c.search("thepiratebay","new","all",async()=>{calls++;return [];})).items,[]);
 assert.equal(calls,2);
});
