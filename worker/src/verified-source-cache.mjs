// Best-effort same-isolate cache of source-authenticated POSITIVE search results.
// This is NOT a new crawler, alternate origin, generic proxy or persistent store.
// Never synthesize magnet hashes, substitute providers or retry upstream 429/403.
export const FRESH_MS=4*60_000;
export const STALE_MAX_MS=20*60_000;
const MAX_ENTRIES=12;
const MAX_SERIALIZED_BYTES=160_000;
const ALLOWED=new Set(["btdigg","thepiratebay"]);
const TPB_DEFAULT_COOLDOWN_MS=60_000;
const TPB_MAX_COOLDOWN_MS=5*60_000;

export function createVerifiedSourceCache(clock=()=>Date.now()){
 const entries=new Map(),inflight=new Map();
 let tpbCooldownUntil=0;
 // Serialize distinct uncached TPB queries inside this Worker isolate as well.
 // Identical queries already share inflight[k]; this gate prevents two different
 // TPB searches racing the origin before the first 429 sets the cooldown.
 let tpbTail=Promise.resolve();
 const key=(id,q,category)=>JSON.stringify([id,q,category]);
 function read(k){
  const item=entries.get(k);
  if(!item)return null;
  const age=clock()-item.at;
  if(age<0||age>STALE_MAX_MS){entries.delete(k);return null;}
  entries.delete(k);entries.set(k,item);
  return {item,age};
 }
 function staleResult(k){
  const old=read(k);
  return old?{items:old.item.items.map(x=>({...x})),
   cache:{mode:"stale",ageSeconds:Math.floor(old.age/1000)}}:null;
 }
 async function search(id,q,category,fetchResults){
  if(!ALLOWED.has(id))return {items:await fetchResults(),cache:null};
  const k=key(id,q,category);
  const cached=read(k);
  if(cached&&cached.age<FRESH_MS)
   return {items:cached.item.items.map(x=>({...x})),
     cache:{mode:"fresh",ageSeconds:Math.floor(cached.age/1000)}};
  if(inflight.has(k))return inflight.get(k);
  // Best-effort per-isolate cooldown across every TPB query, not just one term.
  if(id==="thepiratebay"&&clock()<tpbCooldownUntil){
   const old=staleResult(k);
   if(old)return old;
   throw Error("provider HTTP 429");
  }
  const work=(async()=>{
   let releaseTpb;
   if(id==="thepiratebay"){
    const previous=tpbTail;
    tpbTail=new Promise(resolve=>{releaseTpb=resolve;});
    await previous;
   }
   try{
    // Recheck AFTER waiting: the prior distinct query may just have
    // established an upstream 429 cooldown. Never retry during that window.
    if(id==="thepiratebay"&&clock()<tpbCooldownUntil){
     const old=staleResult(k);
     if(old)return old;
     throw Error("provider HTTP 429");
    }
    const items=await fetchResults();
    if(Array.isArray(items)&&items.length===0)entries.delete(k);
    if(Array.isArray(items)&&items.length>0&&items.length<=100){
     const size=JSON.stringify(items).length;
     if(size>0&&size<=MAX_SERIALIZED_BYTES){
      entries.delete(k);
      entries.set(k,{at:clock(),items:items.map(x=>({...x}))});
      while(entries.size>MAX_ENTRIES)entries.delete(entries.keys().next().value);
     }
    }
    return {items,cache:null};
   }catch(e){
    // Negative cache stores only the upstream 429 deadline, not fake results.
    if(id==="thepiratebay"&&/^provider HTTP 429/i.test(String(e?.message||""))){
     const ms=Number.isFinite(e.retryAfterMs)&&e.retryAfterMs>0
      ?Math.min(TPB_MAX_COOLDOWN_MS,e.retryAfterMs):TPB_DEFAULT_COOLDOWN_MS;
     tpbCooldownUntil=Math.max(tpbCooldownUntil,clock()+ms);
    }
    // Exact-query original results may be returned only visibly marked stale.
    const old=staleResult(k);
    if(old)return old;
    throw e;
   }finally{
    if(releaseTpb)releaseTpb();
    inflight.delete(k);
   }
  })();
  inflight.set(k,work);
  return work;
 }
 return {search};
}
export const verifiedSourceCache=createVerifiedSourceCache();
