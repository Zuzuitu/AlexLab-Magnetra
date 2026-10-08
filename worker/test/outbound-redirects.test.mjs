import test from "node:test";
import assert from "node:assert/strict";
import {searchProvider} from "../src/providers.mjs";

const redirect=(status,location)=>new Response(null,{status,headers:{location}});
const json=(value)=>new Response(JSON.stringify(value),{status:200,headers:{"content-type":"application/json"}});

test("JSON provider refuses off-origin redirect without ever contacting its target",async()=>{
 const visited=[];
 const fetcher=async(url,options)=>{
  visited.push(String(url));
  assert.equal(options.redirect,"manual");
  return redirect(302,"https://untrusted.example/collect");
 };
 await assert.rejects(()=>searchProvider("torrentscsv","ubuntu","all",fetcher),/redirect left the approved origin/);
 assert.deepEqual(visited,["https://torrents-csv.com/service/search?q=ubuntu"]);
});

test("JSON provider follows at most one same-origin HTTPS redirect and still parses",async()=>{
 const visited=[];
 const fetcher=async(url,options)=>{
  assert.equal(options.redirect,"manual");
  visited.push(String(url));
  if(visited.length===1)return redirect(302,"/service/search-v2?q=ubuntu");
  return json({torrents:[]});
 };
 assert.deepEqual(await searchProvider("torrentscsv","ubuntu","all",fetcher),[]);
 assert.deepEqual(visited,[
  "https://torrents-csv.com/service/search?q=ubuntu",
  "https://torrents-csv.com/service/search-v2?q=ubuntu"
 ]);
});

test("repeated JSON redirects terminate after one allowed hop",async()=>{
 let calls=0;
 const fetcher=async()=>{
  calls++;
  return redirect(302,"/service/search?q=ubuntu");
 };
 await assert.rejects(()=>searchProvider("torrentscsv","ubuntu","all",fetcher),/redirected repeatedly/);
 assert.equal(calls,2);
});

test("API-backed POST source retains method and JSON payload under guarded fetch",async()=>{
 const fetcher=async(url,options)=>{
  assert.equal(url,"https://api.knaben.org/v1");
  assert.equal(options.redirect,"manual");
  assert.equal(options.method,"POST");
  assert.equal(JSON.parse(options.body).query,"ubuntu");
  return json({hits:[]});
 };
 const result=await searchProvider("knaben","ubuntu","all",fetcher);
 assert.equal(result.length,0);
});

test("Nyaa HTML provider refuses cross-origin redirect before attempting HTML parsing",async()=>{
 let calls=0;
 await assert.rejects(()=>searchProvider("nyaasi","ubuntu","all",async(url,options)=>{
  calls++;
  assert.equal(options.redirect,"manual");
  return redirect(302,"https://external.example/redirected");
 }),/redirect left the approved origin/);
 assert.equal(calls,1);
});

test("rate-limited API sources are not automatically retried",async()=>{
 let calls=0;
 await assert.rejects(()=>searchProvider("torrentscsv","ubuntu","all",async()=>{
  calls++;
  return new Response("too many requests",{status:429});
 }),/provider HTTP 429/);
 assert.equal(calls,1);
});
