import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";
import {planSearchQuery} from "../src/query-relevance.mjs";
import {releaseFallbackIntent,matchesQualityFallback,rankReleaseAlternative,partitionReleases} from "../src/release-fallback.mjs";

const requested="The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA";
const plan=planSearchQuery(requested);
const magnet=n=>"magnet:?xt=urn:btih:"+String(n).repeat(40);
const make=(id,name)=>({id,name,magnet:magnet(id==="exact"?"a":"b")});
const exact=make("exact",requested);
const sameOtherGroup=make("group","The Dog Stars 2026 1080p 10bit WEB-DL x265 HEVC - OtherGroup");
const same8bit=make("depth","The Dog Stars 2026 1080p 8bit WEBRip x265 HEVC-PSA");
const codec264=make("codec","The Dog Stars 2026 1080p 10bit WEBRip x264-PSA");
const lower720=make("lower","The Dog Stars 2026 720p 10bit WEBRip x265-PSA");
const lower720Other=make("lower-other","The Dog Stars 2026 720p 10bit x265 -OtherGroup");
const lower720264=make("lower-264","The Dog Stars 2026 720p 10bit x264-PSA");
const upper2160=make("upper","The Dog Stars 2026 2160p 10bit x265-PSA");
const wrongYear=make("wrong-year","The Dog Stars 2025 1080p 10bit x265-PSA");
const wrongTitle=make("wrong-title","The Other Stars 2026 1080p 10bit x265-PSA");

test("release intent includes only user-requested video properties, optional group",()=>{
 assert.deepEqual(releaseFallbackIntent(requested,plan),{
  titleQuery:"The Dog Stars 2026",
  technicalTerms:["1080p","x265","10bit"],
  requestedGroup:"PSA",requestedResolution:1080,requestedCodec:"x265",requestedBitDepth:"10bit"
 });
 const withoutGroup="The Dog Stars 2026 1080p x265 10bit";
 const noGroup=releaseFallbackIntent(withoutGroup,planSearchQuery(withoutGroup));
 assert.equal(noGroup?.requestedGroup,null);
 assert.deepEqual(noGroup?.technicalTerms,["1080p","x265","10bit"]);
 for(const q of ["The Dog Stars 2026","Ubuntu 24.04","tt1234567"])
  assert.equal(releaseFallbackIntent(q,planSearchQuery(q)),null,q);
});

test("global rank prioritizes requested resolution before codec, bit depth, group",()=>{
 const candidates=[upper2160,lower720264,lower720Other,lower720,codec264,
  same8bit,sameOtherGroup];
 const scores=candidates.map(x=>({id:x.id,...rankReleaseAlternative(x,requested,plan)}));
 const order=scores.sort((a,b)=>a.fallbackRank-b.fallbackRank).map(x=>x.id);
 assert.deepEqual(order,["group","depth","codec","lower","lower-other","lower-264","upper"]);
 assert.ok(rankReleaseAlternative(codec264,requested,plan).fallbackRank<
   rankReleaseAlternative(lower720,requested,plan).fallbackRank,
   "1080p x264 must outrank 720p x265 when user requests 1080p x265");
 const d=rankReleaseAlternative(codec264,requested,plan);
 assert.deepEqual(d.fallbackDifferences,["codec"]);
 assert.deepEqual(d.fallbackActual,{resolution:"1080p",codec:"x264",bitDepth:"10bit"});
 assert.deepEqual(rankReleaseAlternative(lower720,requested,plan).fallbackDifferences,["resolution"]);
 assert.equal(rankReleaseAlternative(lower720,requested,plan).fallbackGroupMatches,true);
});

test("no wrong film or wrong year and never mistake unknown resolution for 1080p",()=>{
 for(const item of [wrongYear,wrongTitle]){
  assert.equal(rankReleaseAlternative(item,requested,plan),null);
  assert.equal(matchesQualityFallback(item,requested,plan),false);
 }
 const unknown=make("unknown","The Dog Stars 2026 x265 PSA");
 const ranked=rankReleaseAlternative(unknown,requested,plan);
 assert.ok(ranked);
 assert.ok(ranked.fallbackRank>rankReleaseAlternative(lower720,requested,plan).fallbackRank);
 assert.deepEqual(ranked.fallbackActual,{resolution:null,codec:"x265",bitDepth:null});
});

test("H.265/H.264 aliases, release suffix before .mkv and missing group behave safely",()=>{
 const withExt=requested+".mkv";
 assert.equal(releaseFallbackIntent(withExt,planSearchQuery(withExt)).requestedGroup,"PSA");
 const h264=make("h264","The Dog Stars 2026 1080p 10bit H.264-PSA");
 const r=rankReleaseAlternative(h264,requested,plan);
 assert.equal(r.fallbackActual.codec,"h264");
 assert.ok(r.fallbackRank<rankReleaseAlternative(lower720,requested,plan).fallbackRank);
 const h265=make("h265","The Dog Stars 2026 1080p 10bit H.265-OtherGroup");
 assert.equal(rankReleaseAlternative(h265,requested,plan).fallbackActual.codec,"h265");
 assert.ok(rankReleaseAlternative(h265,requested,plan).fallbackRank<
  rankReleaseAlternative(codec264,requested,plan).fallbackRank);
});

test("partition keeps source magnet unchanged and never mislabels fallback as exact",()=>{
 const original=[lower720,wrongTitle,sameOtherGroup,exact,codec264,lower720Other,
   same8bit,wrongYear,upper2160];
 const result=partitionReleases(original,requested,plan);
 assert.deepEqual(result.exact,[exact]);
 assert.deepEqual(result.alternatives.map(x=>x.id),["group","depth","codec","lower","lower-other","upper"]);
 assert.equal(result.excluded,2);
 assert.equal(result.alternatives.find(x=>x.id==="lower").magnet,lower720.magnet);
 assert.equal(result.exact[0],exact);
 assert.deepEqual(result.criteria,["1080p","x265","10bit"]);
 assert.equal(result.requestedGroup,"PSA");
});

test("single real-source-mock response yields ranked alternatives, not extra search calls",async()=>{
 const old=globalThis.fetch;let calls=0;
 try{
  globalThis.fetch=async(url,options)=>{
   calls++;
   assert.equal(String(url),"https://api.knaben.org/v1");
   assert.equal(JSON.parse(options.body).query,"The Dog Stars 2026");
   const hits=[sameOtherGroup,codec264,lower720,upper2160,wrongYear].map(x=>({
    id:x.id,title:x.name,magnetUrl:x.magnet,seeders:5
   }));
   return new Response(JSON.stringify({hits}),{headers:{"content-type":"application/json"}});
  };
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+"&providers=knaben";
  const data=await (await worker.fetch(new Request(url),{})).json();
  assert.equal(calls,1);
  assert.equal(data.total,0);
  assert.equal(data.alternativeTotal,4);
  assert.equal(data.alternatives[0].name,sameOtherGroup.name);
  assert.deepEqual(data.alternatives.map(x=>x.name),[sameOtherGroup.name,codec264.name,lower720.name,upper2160.name]);
  assert.equal(data.alternatives[0].releaseMatch,"quality-alternative");
  assert.equal(data.alternatives[0].fallbackRank,1);
  assert.equal(data.stats[0].count,0);
  assert.equal(data.stats[0].alternativeCount,4);
  assert.equal(data.excludedOffTopic,1);
 }finally{globalThis.fetch=old;}
});

test("exact source rows remain first-class and alternatives cannot be silently substituted",async()=>{
 const old=globalThis.fetch;
 try{
  globalThis.fetch=async()=>new Response(JSON.stringify({hits:[
   {id:"exact",title:requested,magnetUrl:exact.magnet},
   {id:"codec",title:codec264.name,magnetUrl:codec264.magnet}
  ]}),{headers:{"content-type":"application/json"}});
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+"&providers=knaben";
  const data=await (await worker.fetch(new Request(url),{})).json();
  assert.equal(data.total,1);
  assert.equal(data.results[0].name,requested);
  assert.equal(data.alternativeTotal,1);
  assert.ok(data.alternatives[0].fallbackRank>0);
 }finally{globalThis.fetch=old;}
});

test("35 hidden adapters do not receive owner-only ranked alternative behavior",async()=>{
 const old=globalThis.fetch;
 try{
  globalThis.fetch=async(url,options)=>{
   assert.equal(String(url),"https://btsow.live/bts/data/api/search");
   assert.equal(JSON.parse(options.body)[0].search,"The Dog Stars 2026");
   return new Response(JSON.stringify({data:[{hash:"e".repeat(40),name:lower720.name}]}),
    {headers:{"content-type":"application/json"}});
  };
  const data=await (await worker.fetch(new Request(
   "https://index.alexlab.media/api/search?q="+encodeURIComponent(requested)+"&providers=btsow"),{})).json();
  assert.equal(data.alternativeTotal,0);
  assert.deepEqual(data.alternatives,[]);
  assert.equal(data.total,0);
  assert.equal(data.stats[0].rawCount,1);
 }finally{globalThis.fetch=old;}
});
