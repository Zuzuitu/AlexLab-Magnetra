import test from "node:test";
import assert from "node:assert/strict";
import {rock64EZTVFetcher,EZTV_GATEWAY_ORIGIN} from "../src/eztv-rock64.mjs";
import {searchProvider} from "../src/providers.mjs";
const secret="S".repeat(64);
const original="https://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=1";
const ok=data=>new Response(JSON.stringify(data),{headers:{"content-type":"application/json"}});
const row={imdb_id:"460681",id:17,hash:"a".repeat(40),title:"EZTV original result",
 magnet_url:"magnet:?xt=urn:btih:"+"a".repeat(40),seeds:3,peers:2,size_bytes:98765};
const fixture={imdb_id:"460681",torrents_count:15,limit:100,page:1,torrents:[row]};

test("gateway only active on valid secret, never for other sources",async()=>{
 assert.equal(rock64EZTVFetcher({}),null);
 assert.equal(rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:""}),null);
 assert.throws(()=>rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:"short"}));
 let calls=0;
 const source=rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:secret},async(url,opts)=>{
  calls++;
  assert.equal(new URL(url).origin,EZTV_GATEWAY_ORIGIN);
  assert.equal(new URL(url).pathname,"/v1/torrents");
  assert.equal(new URL(url).searchParams.get("imdb_id"),"460681");
  assert.equal(opts.method,"GET");
  assert.equal(opts.redirect,"manual");
  assert.equal(opts.headers.authorization,"Bearer "+secret);
  return ok(fixture);
 });
 const results=await searchProvider("eztvx","tt0460681","series",source);
 assert.equal(calls,1);
 assert.equal(results.length,1);
 assert.equal(results[0].provider,"eztvx");
 assert.equal(results[0].magnet,row.magnet_url);
 assert.equal(results[0].name,row.title);
 assert.equal(results[0].seeders,3);
});

test("TVmaze lookup goes directly to official metadata, EZTV routes only to isolated gateway",async()=>{
 const calls=[];
 const source=rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:secret},async(url,options)=>{
  calls.push({url,options});
  if(new URL(url).hostname==="api.tvmaze.com")
   return ok([{show:{name:"Example Show",externals:{imdb:"tt0460681"}}}]);
  assert.equal(new URL(url).origin,EZTV_GATEWAY_ORIGIN);
  return ok(fixture);
 });
 const xs=await searchProvider("eztvx","Example Show","series",source);
 assert.equal(xs.length,1);
 assert.equal(calls.length,2);
 assert.equal(calls[0].url,"https://api.tvmaze.com/search/shows?q=Example%20Show");
 assert.ok(!calls[0].options.headers.authorization);
});

test("reject arbitrary target URLs and malformed parameters before any gateway call",async()=>{
 let requests=0;
 const source=rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:secret},async()=>{requests++;return ok(fixture);});
 for(const url of [
  "https://evil.example/api/get-torrents?imdb_id=460681&limit=100&page=1",
  "http://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=1",
  "https://eztvx.to/api/get-torrents?imdb_id=460681&limit=99&page=1",
  "https://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=2",
  "https://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=1&url=x",
  "https://eztvx.to/api/get-torrents?imdb_id=460681&imdb_id=99999&limit=100&page=1",
  "https://eztvx.to/api/get-torrents?imdb_id=x&limit=100&page=1",
  "https://eztvx.to/api/get-torrents?imdb_id=460681&limit=100&page=1#fragment",
  "https://api.tvmaze.com/search/shows?q=Example&url=evil"
 ]) await assert.rejects(()=>source(url));
 assert.equal(requests,0);
});

test("HTTP upstream errors and tunnel failures never cause retry or fabricate results",async()=>{
 const cases=[
  [()=>new Response("",{status:401}),/authorization failed/],
  [()=>new Response("",{status:403}),/upstream HTTP 403/],
  [()=>new Response("",{status:429}),/HTTP 429/],
  [()=>new Response("",{status:504}),/upstream timed out/],
  [()=>new Response("",{status:302,headers:{location:"https://evil.example"}}),/redirect refused/],
  [()=>new Response("<html>challenge</html>",{headers:{"content-type":"text/html"}}),/non-JSON/],
  [()=>{throw new DOMException("timeout","TimeoutError");},/tunnel timed out/],
  [()=>{throw new TypeError("private hostname");},/transport failed/]
 ];
 for(const [behavior,pattern] of cases){
  let requests=0;
  const source=rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:secret},async()=>{requests++;return behavior();});
  await assert.rejects(()=>source(original),pattern);
  assert.equal(requests,1);
 }
});

test("no source substitution: no-result gateway answer stays empty",async()=>{
 const source=rock64EZTVFetcher({EZTV_GATEWAY_TOKEN:secret},async()=>ok({
  imdb_id:"460681",torrents_count:0,limit:100,page:1
 }));
 assert.deepEqual(await searchProvider("eztvx","tt0460681","all",source),[]);
});

test("full Worker API uses EZTV gateway only when its secret is supplied",async()=>{
 const {default:app}=await import("../src/index.mjs");
 const originalFetch=globalThis.fetch;
 const origins=[];
 try{
  globalThis.fetch=async(url,options={})=>{
   const parsed=new URL(url);
   origins.push(parsed.origin);
   if(parsed.origin!==EZTV_GATEWAY_ORIGIN)
    throw Error("A non-EZTV request tried to leave the mock");
   assert.equal(options.headers.authorization,"Bearer "+secret);
   return ok(fixture);
  };
  const request=new Request("https://index.alexlab.media/api/search?q=tt0460681&providers=eztvx");
  const response=await app.fetch(request,{EZTV_GATEWAY_TOKEN:secret});
  const parsed=await response.json();
  assert.equal(response.status,200);
  assert.deepEqual(parsed.stats,[{provider:"eztvx",count:1,ok:true}]);
  assert.equal(parsed.total,1);
  assert.equal(parsed.results[0].provider,"eztvx");
  assert.equal(parsed.results[0].magnet,row.magnet_url);
  assert.deepEqual(origins,[EZTV_GATEWAY_ORIGIN]);
 } finally{
  globalThis.fetch=originalFetch;
 }
});
