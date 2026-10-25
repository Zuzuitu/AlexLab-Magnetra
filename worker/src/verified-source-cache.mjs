// Best-effort same-isolate cache of source-authenticated POSITIVE search results.
// This is NOT a new crawler, alternate origin, generic proxy or persistent store.
// Never synthesize magnet hashes, substitute providers or retry upstream 429/403.
export const FRESH_MS=4*60_000;
export const STALE_MAX_MS=20*60_000;
const MAX_ENTRIES=12;
const MAX_SERIALIZED_BYTES=160_000;
const ALLOWED=new Set(["btdigg","thepiratebay"]);

export function createVerifiedSourceCache(clock=()=>Date.now()){
 const entries=new Map(),inflight=new Map();
 const key=(id,q,category)=>JSON.stringify([id,q,category]);
 function read(k){
  const item=entries.get(k);
  if(!item)return null;
  const age=clock()-item.at;
  if(age<0||age>STALE_MAX_MS){entries.delete(k);return null;}
  entries.delete(k);entries.set(k,item);
  return {item,age};
 }
 async function search(id,q,category,fetchResults){
  if(!ALLOWED.has(id))return {items:await fetchResults(),cache:null};
  const k=key(id,q,category);
  const cached=read(k);
  if(cached&&cached.age<FRESH_MS)
   return {items:cached.item.items.map(x=>({...x})),
     cache:{mode:"fresh",ageSeconds:Math.floor(cached.age/1000)}};
  if(inflight.has(k))return inflight.get(k);
  const work=(async()=>{
   try{
    const items=await fetchResults();
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
    // Only an identical original-source, exact-query, still-bounded positive
    // result may substitute a failing request. Surface STALE clearly in API/UI.
    const old=read(k);
    if(old)return {items:old.item.items.map(x=>({...x})),
      cache:{mode:"stale",ageSeconds:Math.floor(old.age/1000)}};
    throw e;
   }finally{inflight.delete(k);}
  })();
  inflight.set(k,work);
  return work;
 }
 return {search};
}
export const verifiedSourceCache=createVerifiedSourceCache();
