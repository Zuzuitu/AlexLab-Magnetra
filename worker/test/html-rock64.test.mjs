import test from "node:test";
import assert from "node:assert/strict";
import {routeHtmlRequest,rock64HtmlFetcher,HTML_GATEWAY_ORIGIN} from "../src/html-rock64.mjs";
import {LEGACY_SPECS} from "../src/legacy-specs.mjs";

const TOKEN="S".repeat(64);

test("two verified hosts only, exact search and detail source routes",()=>{
 assert.equal(LEGACY_SPECS.oxtorrent.host,"https://www.oxtorrent.co");
 assert.equal(LEGACY_SPECS.torrent9.host,"https://www7.torrent9.to");
 const entries=[
  ["oxtorrent","https://www.oxtorrent.co/recherche/ubuntu","search","ubuntu"],
  ["torrent9","https://www7.torrent9.to/search_torrent/ubuntu.html","search","ubuntu"],
  ["oxtorrent","https://www.oxtorrent.co/torrent/132583/ubuntu-title","detail","/torrent/132583/ubuntu-title"],
  ["torrent9","https://www7.torrent9.to/torrent/133873/ubuntu-title","detail","/torrent/133873/ubuntu-title"]
 ];
 for(const [id,src,mode,value] of entries){
  const u=new URL(routeHtmlRequest(id,src));
  assert.equal(u.origin,HTML_GATEWAY_ORIGIN);
  assert.equal(u.pathname,"/v1/"+id+"/html");
  assert.equal(u.searchParams.get("mode"),mode);
  assert.equal(u.searchParams.get(mode==="search"?"q":"path"),value);
 }
});
test("owner-reported OxTorrent detail URL maps to exact fixed gateway route",()=>{
 // This URL was copied from the iPhone result's Details action on Oct 19.
 // A wrong assumption that this slug is noncanonical would hide the real bug.
 const source="https://www.oxtorrent.co/torrent/133995/toy-story-5-2026-multi-ca-1080p-web-h264-supply";
 const route=new URL(routeHtmlRequest("oxtorrent",source));
 assert.equal(route.origin,HTML_GATEWAY_ORIGIN);
 assert.equal(route.pathname,"/v1/oxtorrent/html");
 assert.equal(route.searchParams.get("mode"),"detail");
 assert.equal(route.searchParams.get("path"),"/torrent/133995/toy-story-5-2026-multi-ca-1080p-web-h264-supply");
 assert.equal(route.searchParams.size,2);
});

test("no activation without secret, never use arbitrary destination",async()=>{
 assert.equal(rock64HtmlFetcher("oxtorrent",{}),null);
 assert.equal(rock64HtmlFetcher("torrent9",{MAGNETRA_GATEWAY_TOKEN:""}),null);
 assert.equal(rock64HtmlFetcher("bitsearch",{MAGNETRA_GATEWAY_TOKEN:TOKEN}),null);
 assert.throws(()=>rock64HtmlFetcher("oxtorrent",{MAGNETRA_GATEWAY_TOKEN:"weak"}));
 let outgoing=0;
 const xf=rock64HtmlFetcher("oxtorrent",{MAGNETRA_GATEWAY_TOKEN:TOKEN},async()=>{outgoing++;return new Response("<html/>",{headers:{"content-type":"text/html"}})});
 for(const bad of [
  "https://evil.invalid/torrent/1/title",
  "https://oxtorrent.co/recherche/ubuntu",
  "http://www.oxtorrent.co/recherche/ubuntu",
  "https://u:p@www.oxtorrent.co/recherche/ubuntu",
  "https://www.oxtorrent.co/recherche/ubuntu?url=https://evil.invalid",
  "https://www.oxtorrent.co/torrent/1/title?x=1",
  "https://www.oxtorrent.co/torrent/1/title#fragment",
  "https://www.oxtorrent.co/search/test",
  "https://www.oxtorrent.co/torrent/1/../admin",
  "https://www.oxtorrent.co/torrent/1/title/subpath"
 ]) await assert.rejects(()=>xf(bad));
 assert.equal(outgoing,0);
});
test("only hardcoded 8798 tunnel URL, server bearer, no upstream header forwarding",async()=>{
 const calls=[];
 const xf=rock64HtmlFetcher("torrent9",{MAGNETRA_GATEWAY_TOKEN:TOKEN},async(u,opts)=>{
  calls.push({u,opts});
  return new Response("<html>source response</html>",{headers:{"content-type":"text/html"}});
 });
 const response=await xf("https://www7.torrent9.to/search_torrent/ubuntu.html",
  {method:"GET",headers:{"Cookie":"bad","Authorization":"Bearer attacker"}});
 assert.equal(await response.text(),"<html>source response</html>");
 assert.equal(calls.length,1);
 assert.equal(new URL(calls[0].u).origin,HTML_GATEWAY_ORIGIN);
 assert.deepEqual(calls[0].opts.headers,{authorization:"Bearer "+TOKEN,accept:"text/html"});
 assert.equal(calls[0].opts.redirect,"manual");
 await assert.rejects(()=>xf("https://www7.torrent9.to/search_torrent/ubuntu.html",
  {method:"POST",body:"abc"}));
 assert.equal(calls.length,1);
});
test("upstream errors never substituted or retried",async()=>{
 for(const code of [401,403,429,504,302,520]){
  let calls=0;
  const xf=rock64HtmlFetcher("oxtorrent",{MAGNETRA_GATEWAY_TOKEN:TOKEN},async()=>{
   calls++;return new Response(null,{status:code});
  });
  await assert.rejects(()=>xf("https://www.oxtorrent.co/recherche/ubuntu"));
  assert.equal(calls,1);
 }
});
