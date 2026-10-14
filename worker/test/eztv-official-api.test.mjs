import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {searchEZTVOfficial} from "../src/eztv-official-api.mjs";
import {searchProvider,hasAdapter} from "../src/providers.mjs";
import {classifyProviderError} from "../src/provider-recovery.mjs";
const hash="0123456789abcdef0123456789abcdef01234567";
const magnet="magnet:?xt=urn:btih:"+hash+"&dn=Supernatural.S01E01";
const asResponse=object=>new Response(JSON.stringify(object),{
 headers:{"content-type":"application/json"}
});
const exact=[{score:0.99,show:{name:"Supernatural",externals:{imdb:"tt0460681"}}}];
const torrents={imdb_id:"460681",torrents_count:1,limit:100,page:1,torrents:[{
 id:42,hash,title:"Supernatural S01E01 1080p",magnet_url:magnet,
 filename:"Supernatural.S01E01.1080p.mkv",seeds:5,peers:2,
 size_bytes:"1073741824",date_released_unix:1660000000,
 episode_url:"https://eztvx.to/ep/42/example/"
}]};
test("EZTV indexer uses TVmaze only as exact-series-name-to-IMDb mapping",async()=>{
 assert.ok(hasAdapter("eztvx"));
 let requests=0;
 const fetcher=async(url,options)=>{
  requests++;
  assert.equal(options.redirect,"manual");
  assert.equal(options.method,"GET");
  assert.equal(options.headers["accept"],"application/json");
  if(requests===1){
   assert.equal(url,"https://api.tvmaze.com/search/shows?q=Supernatural");
   return asResponse(exact);
  }
  if(requests===2){
   assert.equal(url,"https://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=1");
   return asResponse(torrents);
  }
  throw Error("Unexpected third request / auto retry");
 };
 const rows=await searchProvider("eztvx","Supernatural","series",fetcher);
 assert.equal(requests,2);
 assert.equal(rows.length,1);
 assert.equal(rows[0].provider,"eztvx");
 assert.equal(rows[0].category,"series");
 assert.equal(rows[0].name,"Supernatural S01E01 1080p");
 assert.equal(rows[0].magnet,magnet);
 assert.equal(rows[0].seeders,5);
 assert.equal(rows[0].peers,2);
 assert.equal(rows[0].size,"1 GB");
 assert.equal(rows[0].details,"https://eztvx.to/ep/42/example/");
});

test("search by precise IMDb ID needs EZTV API only, with no TVmaze lookup",async()=>{
 const calls=[];
 const data=await searchEZTVOfficial("tt0460681","all",async url=>{
  calls.push(url);
  return asResponse(torrents);
 });
 assert.equal(calls.length,1);
 assert.equal(new URL(calls[0]).hostname,"eztvx.to");
 assert.equal(data.length,1);
});

test("ambiguous or fuzzy TVmaze matches do not silently claim another show's torrents",async()=>{
 for(const metadata of [
  [{show:{name:"Supernatural: The Return",externals:{imdb:"tt0460681"}}}],
  [...exact,...exact],
  [{show:{name:"Supernatural",externals:{imdb:null}}}]
 ]){
  let calls=0;
  const result=await searchEZTVOfficial("Supernatural","series",async()=>{
   calls++;
   return asResponse(metadata);
  });
  assert.deepEqual(result,[]);
  assert.equal(calls,1,"ambiguous/unmatched series must not query EZTV with guessed IMDb IDs");
 }
});

test("live-observed duplicate exact TV titles cannot silently choose the wrong IMDb ID",async()=>{
 const tvmaze=[
  {show:{name:"Supernatural",externals:{imdb:"tt0460681"}}},
  {show:{name:"Supernatural",externals:{imdb:"tt0396375"}}}
 ];
 let calls=0;
 let failure;
 await assert.rejects(
  ()=>searchEZTVOfficial("Supernatural","series",async()=>{
   calls++;
   return asResponse(tvmaze);
  }),
  err=>{
   failure=err;
   return /EZTV series title ambiguous/.test(err.message);
  }
 );
 assert.equal(calls,1,"ambiguity must not trigger a torrent API call");
 assert.deepEqual(classifyProviderError(failure),{
  code:"AMBIGUOUS_TITLE",
  message:"Several TV series have this exact title. Search by its IMDb ID.",
  retryable:false
 });
});

test("EZTV API response must confirm exact IMDb ID, otherwise never show recent unrelated releases",async()=>{
 const bad={...torrents,imdb_id:null};
 let calls=0;
 const rows=await searchEZTVOfficial("tt0460681","all",async()=>{
  calls++;
  return asResponse(bad);
 });
 assert.deepEqual(rows,[]);
 assert.equal(calls,1);
});

test("Rock64-observed absent torrent array with explicit zero count is an empty response",async()=>{
 // Field set is real (2026-10-14); zero count remains to be confirmed by probe.
 for(const count of [0,"0"]){
  let calls=0;
  const payload={imdb_id:460681,torrents_count:count,limit:2,page:1};
  const result=await searchEZTVOfficial("tt0460681","all",async url=>{
   calls++;
   assert.equal(new URL(url).searchParams.get("imdb_id"),"460681");
   return asResponse(payload);
  });
  assert.deepEqual(result,[]);
  assert.equal(calls,1,"no fallback into unrelated recent releases");
 }
});

test("missing torrents with positive, missing or invalid count is still an error",async()=>{
 for(const payload of [
  {imdb_id:460681,torrents_count:2,limit:2,page:1},
  {imdb_id:460681,torrents_count:"2",limit:2,page:1},
  {imdb_id:460681,limit:2,page:1},
  {imdb_id:460681,torrents:null,torrents_count:0},
  {imdb_id:460681,torrents_count:0,error:"API failed"},
  {imdb_id:460681,torrents_count:0,errors:["API failed"]}
 ]){
  await assert.rejects(
   ()=>searchEZTVOfficial("tt0460681","all",async()=>asResponse(payload)),
   /EZTV API (shape unexpected|reported an error)/
  );
 }
});

test("empty EZTV response with a different IMDb echo remains untrusted",async()=>{
 const payload={imdb_id:460682,limit:2,page:1,torrents_count:0};
 const result=await searchEZTVOfficial("tt0460681","all",async()=>asResponse(payload));
 assert.deepEqual(result,[]);
});

test("non-series search never requests metadata or torrents from EZTV",async()=>{
 for(const category of ["movies","books","apps","porn","games","music","other","anime"]){
  let calls=0;
  const rows=await searchProvider("eztvx","Supernatural",category,async()=>{calls++;throw Error("bad fetch")});
  assert.deepEqual(rows,[]);
  assert.equal(calls,0);
 }
});

test("only real EZTV torrents with valid magnet can be returned",async()=>{
 const input={...torrents,torrents:[
  {...torrents.torrents[0],magnet_url:"javascript:bad",hash:"bad",id:1},
  {...torrents.torrents[0],id:2,magnet_url:null,episode_url:"https://attacker.invalid/ep/42/"},
  {...torrents.torrents[0],id:3,title:"",filename:""}
 ]};
 const results=await searchProvider("eztvx","tt0460681","all",async()=>asResponse(input));
 assert.equal(results.length,1);
 assert.equal(results[0].magnet,"magnet:?xt=urn:btih:"+hash);
 assert.equal(results[0].details,null,"no untrusted off-origin episode URL");
});

test("source HTTP 403/429, redirects and missing JSON are surfaced honestly without retries",async()=>{
 for(const response of [
  new Response("",{status:403}),
  new Response("",{status:429}),
  new Response("",{status:302,headers:{location:"https://wrong.example"}}),
  new Response("<html>error</html>",{headers:{"content-type":"text/html"}})
 ]){
  let calls=0;
  await assert.rejects(
   ()=>searchEZTVOfficial("tt0460681","all",async()=>{
    calls++;
    return response.clone();
   })
  );
  assert.equal(calls,1,"no automatic retries or source substitution");
 }
});

test("TVmaze attribution and no token exposure in public PWA markup",()=>{
 const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
 assert.match(html,/https:\/\/www\.tvmaze\.com/);
 assert.match(html,/torrent results come only from EZTV/);
 assert.doesNotMatch(html,/TVMAZE_API_KEY|EZTV_API_KEY/);
});
