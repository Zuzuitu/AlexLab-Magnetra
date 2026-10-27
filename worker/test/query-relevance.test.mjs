import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";
import {filterRelevance,queryTerms,relevantTitle,planSearchQuery} from "../src/query-relevance.mjs";

const hash="0123456789abcdef0123456789abcdef01234567";
const movie="the good dinosaur 2015";
const original=[
 {id:"oxtorrent:1",provider:"oxtorrent",name:"The.Good.Dinosaur.2015.1080p.BluRay.x265.HEVC"},
 {id:"torrent9:2",provider:"torrent9",name:"The Good Dinosaur (2015) 1080p BRRip x264 -YTS"},
 {id:"torrentscsv:3",provider:"torrentscsv",name:"The Good Dinosaur (2015)",date:"2016-02-06"},
 {id:"torrent9:4",provider:"torrent9",name:"Good.Luck.Have.Fun.Dont.Die.2026.Multi.Ad.720P.WEBRIP-NOTAG"},
 {id:"torrent9:5",provider:"torrent9",name:"Knock Knock 2015 TRUEFRENCH DVDRip XviD AC3"},
 {id:"torrent9:6",provider:"torrent9",name:"The Hateful Eight 2015 TRUEFRENCH BDRip"},
 {id:"torrent9:7",provider:"torrent9",name:"Dr. Good! c'est bon! - Janvier-février 2023"},
 {id:"torrent9:8",provider:"torrent9",name:"The Good Dinosaur (2016) WEBRip"},
];
test("long video release filenames become one honest title/year query",()=>{
 const filename="The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA";
 assert.deepEqual(planSearchQuery(filename),{searchedAs:"The Dog Stars 2026",broadened:true});
 assert.deepEqual(planSearchQuery("The Dog Stars 1080p PSA"),{searchedAs:"The Dog Stars",broadened:true});
 assert.deepEqual(planSearchQuery("the doa stars 1080p psa"),{searchedAs:"the doa stars",broadened:true},
  "do not invent a spelling correction or fabricate a title");
 for(const untouched of ["The Dog Stars 2026","Ubuntu 24.04","tt21285562",
  "the","10bit","x265","The Good Dinosaur 2015"]){
  const plan=planSearchQuery(untouched);
  assert.equal(plan.searchedAs,untouched);
  assert.equal(plan.broadened,false);
 }
 assert.equal(relevantTitle("The Dog Stars 2026","The Dog Stars 2025 1080p PSA"),false,
  "real release year must still match");
});

test("Worker searches the release title once per provider, not every quality or group token",async()=>{
 const before=globalThis.fetch;
 const seen=[];
 try{
  globalThis.fetch=async(url,opts)=>{
   seen.push({url:String(url),opts});
   assert.equal(String(url),"https://api.knaben.org/v1");
   assert.equal(JSON.parse(opts.body).query,"The Dog Stars 2026");
   return new Response(JSON.stringify({hits:[
    {id:"dog:1",title:"The Dog Stars (2026) 1080p WEB-DL x265 BONE",magnetUrl:"magnet:?xt=urn:btih:"+hash,seeders:7},
    {id:"other:2",title:"The Other Stars (2026) x265 PSA",magnetUrl:"magnet:?xt=urn:btih:"+hash,seeders:100}
   ]}),{headers:{"content-type":"application/json"}});
  };
  const raw="The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA";
  const url="https://index.alexlab.media/api/search?q="+encodeURIComponent(raw)+"&providers=knaben&category=all";
  const res=await worker.fetch(new Request(url),{});
  assert.equal(res.status,200);
  const data=await res.json();
  assert.equal(data.query,raw);
  assert.equal(data.searchedAs,"The Dog Stars 2026","must inform UI when original filename was simplified");
  assert.equal(seen.length,1,"no hidden rerun, fallback or second provider query");
  assert.equal(data.total,1);
  assert.equal(data.excludedOffTopic,1);
  assert.equal(data.results[0].name,"The Dog Stars (2026) 1080p WEB-DL x265 BONE");
  assert.equal(data.results[0].provider,"knaben");
  assert.equal(data.results[0].magnet,"magnet:?xt=urn:btih:"+hash);
 }finally{globalThis.fetch=before;}
});

test("screenshot regression: exact title and title-year match; unrelated hits excluded",()=>{
 const {matches,excluded}=filterRelevance(original,movie);
 assert.deepEqual(matches.map(x=>x.id),original.slice(0,3).map(x=>x.id));
 assert.equal(excluded,5);
 assert.equal(matches[0],original[0],"do not copy/rename real source rows or alter provenance");
});
test("release separators, accent normalization and case keep legitimate results",()=>{
 for(const title of [
  "The.Good.Dinosaur.2015.1080p.BluRay.x265-YTS",
  "THE GOOD DINOSAUR [2015] HEVC",
  "Good Dinosaur 2015 DUAL RoDubbed",
  "The_Good_Dinosaur_2015_2160p_DV"
 ])assert.equal(relevantTitle(movie,title),true,title);
 assert.equal(relevantTitle("Pokémon 2026","Pokemon.2026.Multi"),true);
 assert.equal(relevantTitle("Ubuntu 24.04","ubuntu-24.04.1-desktop-amd64.iso"),true);
});
test("full token boundaries block coincidental year, word prefix, substring, date metadata",()=>{
 assert.equal(relevantTitle(movie,"Good Luck and the Dinosaur 2016"),false);
 assert.equal(relevantTitle(movie,"The Good Dinosaurs 2015"),false);
 assert.equal(relevantTitle(movie,"The Good Dinosaur 2016"),false);
 assert.equal(relevantTitle("2026","The Good Dinosaur (2015)"),false);
 assert.equal(relevantTitle("the good dinosaur 2015","Knock Knock (2015)"),false);
 assert.equal(relevantTitle("the good dinosaur 2015",null),false);
 assert.equal(relevantTitle("ubuntu","Xubuntu 22.04"),false);
 assert.deepEqual(queryTerms("The Good Dinosaur (2015)"),["good","dinosaur","2015"]);
});
test("single term, title-only, and original exact identifier lookups remain supported",()=>{
 assert.equal(relevantTitle("ubuntu","Ubuntu 26.04 ISO"),true);
 assert.equal(relevantTitle("2026","Anime.Release.2026.1080p"),true);
 assert.equal(relevantTitle("tt0413573","Greys Anatomy S01E01 720p"),true);
 assert.equal(relevantTitle(hash,"Ubuntu 26.04 ISO"),true);
 assert.equal(relevantTitle("the","The.Good.Dinosaur.2015"),true);
});
test("Worker API globally filters original source responses and preserves truthful counts",async()=>{
 const old=globalThis.fetch;
 const seen=[];
 try{
  globalThis.fetch=async (url,opts)=>{
   seen.push({url:String(url),method:opts?.method});
   if(String(url)==="https://api.knaben.org/v1")
    return new Response(JSON.stringify({hits:[
     {id:"1",title:"The Good Dinosaur (2015) 1080p BRRip x264",magnetUrl:"magnet:?xt=urn:btih:"+hash,seeders:100},
     {id:"2",title:"Knock Knock 2015 TRUEFRENCH DVDRip",magnetUrl:"magnet:?xt=urn:btih:"+hash,seeders:200},
     {id:"3",title:"Good.Luck.Have.Fun.Dont.Die.2026.720p",magnetUrl:"magnet:?xt=urn:btih:"+hash,seeders:300}
    ]}),{headers:{"content-type":"application/json"}});
   if(String(url).startsWith("https://torrents-csv.com/service/search?q="))
    return new Response(JSON.stringify({torrents:[
     {id:"4",name:"The.Good.Dinosaur.2015.1080p.BluRay.x265",infohash:hash,seeders:101},
     {id:"5",name:"The Hateful Eight 2015 BDRip",infohash:hash,seeders:999}
    ]}),{headers:{"content-type":"application/json"}});
   throw Error("Unexpected source: "+String(url));
  };
  const url="https://index.alexlab.media/api/search?q=the%20good%20dinosaur%202015&providers=knaben,torrentscsv&category=all";
  const response=await worker.fetch(new Request(url),{});
  assert.equal(response.status,200);
  const data=await response.json();
  assert.equal(seen.length,2,"no retries, extra provider requests or fallbacks");
  assert.equal(data.total,2);
  assert.equal(data.results.length,2);
  assert.equal(data.excludedOffTopic,3);
  assert.deepEqual(data.results.map(x=>x.provider),["knaben","torrentscsv"]);
  assert.deepEqual(data.stats.map(x=>({
   id:x.provider,count:x.count,rawCount:x.rawCount,excluded:x.excludedOffTopic,ok:x.ok
  })),[
   {id:"knaben",count:1,rawCount:3,excluded:2,ok:true},
   {id:"torrentscsv",count:1,rawCount:2,excluded:1,ok:true}
  ]);
  assert.deepEqual(data.errors,[]);
  assert.ok(data.results.every(x=>relevantTitle(movie,x.name)));
  assert.ok(data.results.every(x=>x.magnet?.startsWith("magnet:?xt=urn:btih:")));
 }finally{globalThis.fetch=old;}
});
test("source HTTP errors remain errors and never turn into off-topic exclusions",async()=>{
 const previous=globalThis.fetch;
 try{
  globalThis.fetch=async()=>new Response("",{status:403,headers:{"content-type":"text/plain"}});
  const res=await worker.fetch(new Request("https://index.alexlab.media/api/search?q=the%20good%20dinosaur%202015&providers=torrentscsv"),{});
  const data=await res.json();
  assert.equal(data.total,0);
  assert.equal(data.excludedOffTopic,0);
  assert.equal(data.errors.length,1);
  assert.equal(data.stats[0].ok,false);
  assert.equal(data.stats[0].count,0);
  assert.equal(data.stats[0].excludedOffTopic,0);
 }finally{globalThis.fetch=previous;}
});
