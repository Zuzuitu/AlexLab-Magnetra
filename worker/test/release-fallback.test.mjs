import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";
import {planSearchQuery} from "../src/query-relevance.mjs";
import {releaseFallbackIntent,matchesQualityFallback,partitionReleases} from "../src/release-fallback.mjs";

const requested="The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA";
const exact={id:"same",name:requested,magnet:"magnet:?xt=urn:btih:"+"a".repeat(40)};
const alternate={id:"other",name:"The Dog Stars 2026 1080p 10bit WEB-DL x265 HEVC - OtherGroup",magnet:"magnet:?xt=urn:btih:"+"b".repeat(40)};
const wrongResolution={id:"4k",name:"The Dog Stars 2026 2160p 10bit x265 - OtherGroup"};
const wrongCodec={id:"264",name:"The Dog Stars 2026 1080p 10bit x264 - OtherGroup"};
const wrongDepth={id:"8bit",name:"The Dog Stars 2026 1080p 8bit x265 - OtherGroup"};
const wrongYear={id:"2025",name:"The Dog Stars 2025 1080p 10bit x265 - OtherGroup"};
const otherFilm={id:"other-film",name:"The Other Stars 2026 1080p 10bit x265 - OtherGroup"};

test("explicit group suffix qualifies for fallback, but ONLY user-supplied video requirements survive",()=>{
 const plan=planSearchQuery(requested);
 assert.deepEqual(releaseFallbackIntent(requested,plan),{
  titleQuery:"The Dog Stars 2026",
  technicalTerms:["1080p","x265","10bit"],
  requestedGroup:"PSA"
 });
 assert.equal(matchesQualityFallback(alternate,requested,plan),true);
 for(const row of [wrongResolution,wrongCodec,wrongDepth,wrongYear,otherFilm])
  assert.equal(matchesQualityFallback(row,requested,plan),false,row.id);
});

test("source-owned exact release always wins; alternatives are distinct and never fabricated",()=>{
 const rows=[alternate,exact,wrongResolution,wrongCodec,wrongDepth,wrongYear,otherFilm];
 const part=partitionReleases(rows,requested,planSearchQuery(requested));
 assert.deepEqual(part.exact,[exact]);
 assert.deepEqual(part.alternatives,[alternate]);
 assert.equal(part.excluded,rows.length-2);
 assert.equal(part.alternatives[0].magnet,alternate.magnet);
 assert.equal(part.exact[0].magnet,exact.magnet);
 assert.deepEqual(part.criteria,["1080p","x265","10bit"]);
 assert.equal(part.requestedGroup,"PSA");
});

test("ordinary queries, no group, and IMDb/hash lookups never broaden to group alternatives",()=>{
 for(const q of ["The Dog Stars 2026","Ubuntu 24.04",
  "The Dog Stars 2026 1080p x265 10bit","tt1234567",
  "The.Dog.Stars.2026.1080p.10bit.x265"]){
  assert.equal(releaseFallbackIntent(q,planSearchQuery(q)),null,q);
 }
});

test("one genuine upstream response returns exact and quality alternatives in different API fields",async()=>{
 const before=globalThis.fetch;
 const calls=[];
 try{
  globalThis.fetch=async(u,options)=>{
   calls.push({url:String(u),options});
   assert.equal(String(u),"https://api.knaben.org/v1");
   assert.equal(JSON.parse(options.body).query,"The Dog Stars 2026 1080p x265 10bit");
   return new Response(JSON.stringify({hits:[
    {id:"good",title:requested,magnetUrl:exact.magnet,seeders:8},
    {id:"alternate",title:alternate.name,magnetUrl:alternate.magnet,seeders:5},
    {id:"wrong-4k",title:wrongResolution.name,magnetUrl:"magnet:?xt=urn:btih:"+"c".repeat(40),seeders:30}
   ]}),{headers:{"content-type":"application/json"}});
  };
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+"&providers=knaben";
  const res=await worker.fetch(new Request(url),{});
  assert.equal(res.status,200);
  const data=await res.json();
  assert.equal(calls.length,1,"one upstream call, never auto-retry or silently search again");
  assert.equal(data.total,1);
  assert.equal(data.alternativeTotal,1);
  assert.deepEqual(data.fallbackCriteria,["1080p","x265","10bit"]);
  assert.equal(data.requestedGroup,"PSA");
  assert.equal(data.results[0].name,requested);
  assert.equal(data.results[0].magnet,exact.magnet);
  assert.equal(data.alternatives[0].name,alternate.name);
  assert.equal(data.alternatives[0].magnet,alternate.magnet);
  assert.equal(data.alternatives[0].releaseMatch,"quality-alternative");
  assert.equal(data.stats[0].count,1);
  assert.equal(data.stats[0].alternativeCount,1);
  assert.equal(data.stats[0].rawCount,3);
  assert.equal(data.excludedOffTopic,1);
 }finally{globalThis.fetch=before;}
});

test("API allows alternatives only when there is no exact match, but never represents them as exact",async()=>{
 const before=globalThis.fetch;
 try{
  globalThis.fetch=async()=>new Response(JSON.stringify({hits:[
   {id:"alternate",title:alternate.name,magnetUrl:alternate.magnet,seeders:5}
  ]}),{headers:{"content-type":"application/json"}});
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+"&providers=knaben";
  const data=await (await worker.fetch(new Request(url),{})).json();
  assert.equal(data.total,0);
  assert.equal(data.results.length,0);
  assert.equal(data.alternativeTotal,1);
  assert.equal(data.alternatives[0].releaseMatch,"quality-alternative");
 }finally{globalThis.fetch=before;}
});

test("35 hidden legacy adapters do not receive the curated-only group-fallback policy",async()=>{
 const before=globalThis.fetch;
 const observed=[];
 try{
  globalThis.fetch=async(url,options)=>{
   observed.push({url:String(url),options});
   assert.equal(String(url),"https://btsow.live/bts/data/api/search");
   assert.equal(JSON.parse(options.body)[0].search,"The Dog Stars 2026");
   return new Response(JSON.stringify({data:[{
    hash:"e".repeat(40),name:alternate.name,size:"1.73 GB"
   }]}),{headers:{"content-type":"application/json"}});
  };
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+
   "&providers=btsow";
  const result=await (await worker.fetch(new Request(url),{})).json();
  assert.equal(observed.length,1);
  assert.equal(result.total,0);
  assert.equal(result.alternativeTotal,0);
  assert.deepEqual(result.alternatives,[]);
  assert.equal(result.requestedGroup,undefined);
  assert.equal(result.stats[0].rawCount,1);
  assert.equal(result.stats[0].excludedOffTopic,1);
 }finally{globalThis.fetch=before;}
});
