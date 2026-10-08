import {HTML_PROVIDER_SPECS} from "../src/html-adapters.mjs";
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {PROVIDERS,PROVIDER_MAP} from "../src/catalog.mjs";
import {hasAdapter,magnetFromHash,searchProvider} from "../src/providers.mjs";
import worker from "../src/index.mjs";
const hash="0123456789abcdef0123456789abcdef01234567";
const magnet="magnet:?xt=urn:btih:"+hash;
const response=obj=>new Response(JSON.stringify(obj),{headers:{"content-type":"application/json"}});
test("all 46 Android built-in providers are inventoried in original order",()=>{
 const source=readFileSync(new URL("../../app/src/main/kotlin/com/prajwalch/torrentsearch/di/BuiltinSearchProvidersModule.kt",import.meta.url),"utf8");
 const imports=[...source.matchAll(/^import com\.prajwalch\.torrentsearch\.providers\.([A-Za-z0-9]+)$/gm)].map(x=>x[1]);
 assert.equal(imports.length,46);
 assert.equal(PROVIDERS.length,46);
 assert.equal(new Set(PROVIDERS.map(p=>p.id)).size,46);
 const classNames=PROVIDERS.map(p=>p.id==="1337x"?"ThirteenThirtySevenX":p.id==="0magnet"?"ZeroMagnet":p.name.replace(/[^a-zA-Z0-9]/g,"")).map(x=>x.toLowerCase()).sort();
 assert.deepEqual(classNames,imports.map(x=>x.toLowerCase()).sort());
 for(const p of PROVIDERS){assert.ok(p.url.startsWith("https://"));assert.equal(p.ported,hasAdapter(p.id));}
});
test("reject invalid magnet hashes",()=>{
 assert.equal(magnetFromHash(hash),magnet);
 assert.equal(magnetFromHash("javascript:alert(1)"),null);
 assert.equal(magnetFromHash("invalid"),null);
});
test("Knaben adapter maps supported result fields",async()=>{
 const fetcher=async(url,opts)=>{
  assert.equal(url,"https://api.knaben.org/v1");
  assert.equal(JSON.parse(opts.body).query,"linux");
  return response({hits:[{id:"42",title:"Ubuntu ISO",magnetUrl:magnet,bytes:1073741824,seeders:18,peers:2,date:"2026-10-01",details:"https://knaben.org/example",categoryId:[4000000]}]});
 };
 const rows=await searchProvider("knaben","linux","all",fetcher);
 assert.equal(rows.length,1);assert.equal(rows[0].name,"Ubuntu ISO");assert.equal(rows[0].seeders,18);
 assert.equal(rows[0].size,"1 GB");assert.equal(rows[0].magnet,magnet);
});
test("TorrentsCSV constructs magnet without upstream trackers",async()=>{
 const fetcher=async(url)=>{assert.match(url,/q=test%20linux/);return response({torrents:[{name:"Test",infohash:hash,id:1,size_bytes:1024,seeders:7,leechers:1}]});};
 const rows=await searchProvider("torrentscsv","test linux","all",fetcher);
 assert.equal(rows.length,1);assert.equal(rows[0].magnet,magnet);
});
test("unknown provider cannot masquerade as searchable",async()=>{
 await assert.rejects(()=>searchProvider("invented-provider","linux","all"),/not ported/);
 await assert.rejects(()=>searchProvider("knaben","x","all"),/2–180/);
});
test("API catalog is complete and never publishes credentials",async()=>{
 const req=new Request("https://example.com/api/providers");
 const res=await worker.fetch(req,{});
 assert.equal(res.status,200);
 const data=await res.json();
 assert.equal(data.providers.length,46);
 assert.equal(JSON.stringify(data).includes("token"),false);
});
test("Companion rejects malformed pairing and non-same-origin POST",async()=>{
 const bad=new Request("https://magnetra.example/api/companion/magnet",{
  method:"POST",headers:{"origin":"https://evil.example","content-type":"application/json"},
  body:JSON.stringify({deviceId:"x",token:"a".repeat(25),magnet})
 });
 assert.equal((await worker.fetch(bad,{})).status,403);
 const invalid=new Request("https://magnetra.example/api/companion/magnet",{
  method:"POST",headers:{"origin":"https://magnetra.example","content-type":"application/json"},
  body:JSON.stringify({deviceId:"x",token:"a".repeat(25),magnet,autoStart:false})
 });
 assert.equal((await worker.fetch(invalid,{})).status,400);
});
test("Companion forwards only to fixed allowlisted endpoint, with idempotency ID",async()=>{
 const previous=globalThis.fetch;
 try{
  let called=false;
  globalThis.fetch=async(url,opts)=>{
    called=true;
    assert.equal(url,"https://flud-remote.alexlab.media/api/v1/device/"+"D".repeat(20)+"/magnet");
    assert.equal(opts.headers.authorization,"Bearer "+"T".repeat(26));
    const body=JSON.parse(opts.body);
    assert.equal(body.magnet,magnet);assert.equal(body.autoStart,false);assert.ok(body.requestId.length>=8);
    return new Response(JSON.stringify({ok:true,queued:true}),{status:202});
  };
  const req=new Request("https://magnetra.example/api/companion/magnet",{
   method:"POST",headers:{"origin":"https://magnetra.example","content-type":"application/json"},
   body:JSON.stringify({deviceId:"D".repeat(20),token:"T".repeat(26),magnet,autoStart:false})
  });
  const res=await worker.fetch(req,{});
  assert.equal(res.status,202);assert.equal((await res.json()).queued,true);assert.equal(called,true);
 }finally{globalThis.fetch=previous;}
});

test("AniLibria fetches release torrent lists through its original two-stage API",async()=>{
 const calls=[];
 const fetcher=async(url)=>{
  calls.push(url);
  if(url.includes("/app/search/releases"))return response([{id:4}]);
  if(url.endsWith("/anime/torrents/release/4"))return response([{
   id:9,hash,magnet,label:"Anime 1080p",size:1048576,seeders:12,leechers:2,
   release:{alias:"anime-show",name:{main:"Anime"}}
  }]);
  throw Error("unexpected URL");
 };
 const results=await searchProvider("anilibria","anime","anime",fetcher);
 assert.equal(calls.length,2);
 assert.equal(results.length,1);
 assert.equal(results[0].name,"Anime 1080p");
 assert.equal(results[0].seeders,12);
});

test("PWA manifest and service worker keep API/network commands out of offline cache",()=>{
 const manifest=JSON.parse(readFileSync(new URL("../../web/manifest.webmanifest",import.meta.url),"utf8"));
 assert.equal(manifest.name,"AlexLab Magnetra");
 assert.equal(manifest.display,"standalone");
 assert.ok(manifest.icons.length);
 const sw=readFileSync(new URL("../../web/sw.js",import.meta.url),"utf8");
 assert.ok(sw.includes('u.pathname.startsWith("/api/")'));
 assert.ok(sw.includes('e.request.method!=="GET"'));
});

test("ten fixed-endpoint HTML adapter contracts are registered and encoded",()=>{
 assert.equal(Object.keys(HTML_PROVIDER_SPECS).length,10);
 for(const [id,spec] of Object.entries(HTML_PROVIDER_SPECS)){
  assert.equal(hasAdapter(id),true);
  assert.equal(PROVIDER_MAP.get(id).ported,true);
  assert.ok(spec.rows&&spec.name);
  assert.ok(spec.magnet||spec.hashFromFile||spec.hashFromDetails);
  const url=new URL(spec.search("foo & bar","all"));
  assert.equal(url.origin,spec.host);
  assert.ok(url.toString().includes("foo"));
  assert.ok(url.toString().includes("%26"),id+": search query was not encoded");
 }
});

test("missing seed/leech fields remain unknown rather than fabricated zero",async()=>{
 const hash="0123456789abcdef0123456789abcdef01234567";
 const rows=await searchProvider("torrentscsv","ubuntu","all",async()=>new Response(JSON.stringify({torrents:[{name:"Ubuntu ISO",id:77,infohash:hash,size_bytes:1024}]}),{headers:{"content-type":"application/json"}}));
 assert.equal(rows.length,1);
 assert.equal(rows[0].seeders,null);
 assert.equal(rows[0].peers,null);
});
