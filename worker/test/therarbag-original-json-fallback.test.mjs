import test from "node:test";
import assert from "node:assert/strict";
import {resolveLegacy,theRarBgOriginalJsonHash} from "../src/legacy-adapters.mjs";

const DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
const JSON_URL=DETAIL+"?format=json";
const HASH="a".repeat(40);
const OTHER="b".repeat(40);
const dummyHtml="<html><body><div>Magnet Download</div><div>Info Hash: unavailable</div></body></html>";
const validJson=()=>new Response(JSON.stringify({info_hash:HASH,name:"Public domain fixture"}),{
  status:200,headers:{"content-type":"application/json"}
});
async function withWorkerdRewriterMock(fn){
 const prior=globalThis.HTMLRewriter;
 class FakeHTMLRewriter{on(){return this}transform(res){return res}}
 globalThis.HTMLRewriter=FakeHTMLRewriter;
 try{return await fn()}finally{
  if(prior===undefined)delete globalThis.HTMLRewriter;
  else globalThis.HTMLRewriter=prior;
 }
}

test("exact TheRarBg source JSON fallback resolves a failed HTML-only original page",async()=>{
 await withWorkerdRewriterMock(async()=>{
  const calls=[];
  const result=await resolveLegacy("therarbag",DETAIL,async(url,opts)=>{
   calls.push({url,method:opts.method,redirect:opts.redirect,accept:opts.headers?.accept});
   if(url===DETAIL)return new Response(dummyHtml,{status:200,headers:{"content-type":"text/html"}});
   if(url===JSON_URL)return validJson();
   throw Error("unapproved destination");
  });
  assert.deepEqual(result,{magnet:"magnet:?xt=urn:btih:"+HASH});
  assert.deepEqual(calls.map(x=>x.url),[DETAIL,JSON_URL]);
  assert.equal(calls[0].redirect,"manual");
  assert.equal(calls[1].redirect,"manual");
  assert.equal(calls[1].method,"GET");
  assert.equal(calls[1].accept,"application/json");
 });
});

test("TheRarBg source JSON is not fetched if existing HTML fallback succeeds",async()=>{
 await withWorkerdRewriterMock(async()=>{
  let calls=0;
  const res=await resolveLegacy("therarbag",DETAIL,async(url)=>{
   calls++;
   assert.equal(url,DETAIL);
   return new Response("<html><div>Info Hash: "+HASH+"</div></html>",{
    status:200,headers:{"content-type":"text/html"}});
  });
  assert.equal(res.magnet,"magnet:?xt=urn:btih:"+HASH);
  assert.equal(calls,1);
 });
});

test("only the exact fixed original source URL is eligible",async()=>{
 for(const url of [
  "https://therarbg.com.evil.example/post-detail/95bf8b/title/",
  "https://therarbg.com/download/95bf8b/title/",
  "https://therarbg.com/post-detail/95bf8b/title/?redirect=1",
  "https://therarbg.com/post-detail/95bf8b/title/#fragment",
  "http://therarbg.com/post-detail/95bf8b/title/",
  "https://user@therarbg.com/post-detail/95bf8b/title/",
  "https://therarbg.com/post-detail/95bf8b/../evil/"
 ]){
  let calls=0;
  const result=await theRarBgOriginalJsonHash(url,dummyHtml,async()=>{
   calls++;return validJson();
  });
  assert.equal(result,null,url);
  assert.equal(calls,0,url);
 }
});

test("JSON accepts strict original response root or wrapped info_hash only",async()=>{
 for(const body of [
  "{}",JSON.stringify({results:[{info_hash:HASH}]}),
  JSON.stringify({error:"upstream error",info_hash:HASH}),
  JSON.stringify({data:{info_hash:"z".repeat(40)}}),
  JSON.stringify({data:[{info_hash:HASH}]}),
  JSON.stringify({data:{info_hash:OTHER.slice(0,39)}}),
  JSON.stringify({data:{info_hash:"magnet:?xt=urn:btih:"+HASH}}),
  "{bad json"
 ]){
  const got=await theRarBgOriginalJsonHash(DETAIL,dummyHtml,
    async()=>new Response(body,{status:200,headers:{"content-type":"application/json"}}));
  assert.equal(got,null);
 }
});

test("TheRarBg original top-level info_hash works without a JSON data wrapper",async()=>{
 for(const body of [
  {info_hash:HASH,name:"Original TheRarBg"},
  {data:{info_hash:HASH,name:"Original TheRarBg"}},
  {info_hash:HASH.toUpperCase(),data:{info_hash:HASH}}
 ]){
  const response=await theRarBgOriginalJsonHash(DETAIL,dummyHtml,async()=>
    new Response(JSON.stringify(body),{status:200,headers:{"content-type":"application/json"}}));
  assert.equal(response,"magnet:?xt=urn:btih:"+HASH);
 }
});

test("ambiguous, malformed or error-envelope hashes are rejected",async()=>{
 for(const body of [
  {info_hash:HASH,data:{info_hash:OTHER}},
  {info_hash:HASH,data:{info_hash:"z".repeat(40)}},
  {info_hash:"z".repeat(40),data:{info_hash:HASH}},
  {info_hash:null,data:{info_hash:HASH}},
  {error:"forbidden",info_hash:HASH},
  {results:[{info_hash:HASH}]},
  [{info_hash:HASH}]
 ]){
  const response=await theRarBgOriginalJsonHash(DETAIL,dummyHtml,async()=>
    new Response(JSON.stringify(body),{status:200,headers:{"content-type":"application/json"}}));
  assert.equal(response,null);
 }
});

test("reject raw HTML, redirects, Cloudflare challenge, and HTTP errors at exact JSON endpoint",async()=>{
 for(const config of [
  {status:302,headers:{"location":DETAIL}},
  {status:403},
  {status:200,headers:{"content-type":"text/html"}},
  {status:200,headers:{"content-type":"application/json","cf-mitigated":"challenge"}},
  {status:200,headers:{"content-type":"application/json","content-length":"3000001"}}
 ]){
  const x=await theRarBgOriginalJsonHash(DETAIL,dummyHtml,async()=>
   new Response(JSON.stringify({data:{info_hash:HASH}}),config));
  assert.equal(x,null);
 }
});

test("explicit contradictory source metadata or magnet anchor rejects JSON candidate",async()=>{
 for(const html of [
  "<p>Info Hash: "+OTHER+"</p>",
  "<p>Info Hash: "+HASH+"</p><p>Info Hash: "+OTHER+"</p>",
  '<a href="magnet:?xt=urn:btih:'+OTHER+'&amp;dn=Wrong">Magnet</a>'
 ]){
  const result=await theRarBgOriginalJsonHash(DETAIL,html,async()=>validJson());
  assert.equal(result,null);
 }
 assert.equal(await theRarBgOriginalJsonHash(DETAIL,
  "<p>Info Hash: "+HASH+"</p>",async()=>validJson()),
  "magnet:?xt=urn:btih:"+HASH);
});

test("JSON fetch transport exception remains a normal unresolved result and never switches provider",async()=>{
 await withWorkerdRewriterMock(async()=>{
  let calls=0;
  await assert.rejects(async()=>resolveLegacy("therarbag",DETAIL,async(url)=>{
   calls++;
   if(url===DETAIL)return new Response(dummyHtml,{status:200,headers:{"content-type":"text/html"}});
   if(url===JSON_URL)throw Error("connection refused: secret environment token");
   throw Error("unexpected fetch");
  }),/provider details page contains no supported magnet link/);
  assert.equal(calls,2);
 });
});
