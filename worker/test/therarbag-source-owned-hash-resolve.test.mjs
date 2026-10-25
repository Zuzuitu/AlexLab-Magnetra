import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {magnetFromTheRarBgInfoHash,magnetFromTheRarBgSourceMetadata,normalizedTheRarBgMagnetHref,resolveLegacy} from "../src/legacy-adapters.mjs";

const HASH="a".repeat(40);
const sample='<html><main><h1>Public-domain sample</h1><div><strong>Info Hash:</strong> <code>'+HASH.toUpperCase()+'</code> <button>Copy Magnet</button></div></main></html>';

test("TheRarBg Cloudflare HTMLRewriter href preserves HTML ampersands; normalize exact BTIH",()=>{
  const href="magnet:?xt=urn:btih:"+HASH+"&amp;dn=Public-domain%20Sample&amp;tr=udp%3A%2F%2Ftracker.invalid";
  const expected="magnet:?xt=urn:btih:"+HASH+"&dn=Public-domain%20Sample&tr=udp%3A%2F%2Ftracker.invalid";
  assert.equal(normalizedTheRarBgMagnetHref(href),expected);
  assert.equal(normalizedTheRarBgMagnetHref(href.replaceAll("&amp;","&#38;")),expected);
  assert.equal(normalizedTheRarBgMagnetHref(href.replaceAll("&amp;","&#x26;")),expected);
  assert.equal(normalizedTheRarBgMagnetHref(expected),expected);
  assert.equal(normalizedTheRarBgMagnetHref("magnet:?xt=urn:btih:"+HASH), "magnet:?xt=urn:btih:"+HASH);
});
test("TheRarBg HTML entity normalization refuses other schemes, invalid hashes and oversized links",()=>{
  for(const candidate of [
    "https://therarbg.com/magnet", "magnet:?xt=urn:btih:"+"z".repeat(40),
    "magnet:?xt=urn:btih:"+"a".repeat(39),
    "magnet:?dn=Unrelated&xt=urn:btih:"+HASH,
    "magnet:?xt=urn:btih:"+HASH+"x",
    "magnet:?xt=urn:btih:"+HASH+"&dn="+"x".repeat(12000),
    null, "", 12
  ])assert.equal(normalizedTheRarBgMagnetHref(candidate),null);
});

test("TheRarBg unique source-labelled info hash yields a BTIH magnet",()=>{
  assert.equal(magnetFromTheRarBgInfoHash(sample),"magnet:?xt=urn:btih:"+HASH);
  assert.equal(magnetFromTheRarBgInfoHash("<p>Info Hash: &#160;<b>"+HASH+"</b></p>"),"magnet:?xt=urn:btih:"+HASH);
});

test("duplicate identical source-owned hash is unambiguous on mobile and desktop markup",()=>{
  const duplicated="<section class='desktop'>Info Hash: "+HASH+"</section>"+
                   "<section class='mobile'>Info Hash: "+HASH.toUpperCase()+"</section>";
  assert.equal(magnetFromTheRarBgInfoHash(duplicated),"magnet:?xt=urn:btih:"+HASH);
});

test("refuse ambiguous, scripted, unrelated, invalid and oversized hashes",()=>{
  assert.equal(magnetFromTheRarBgInfoHash("<p>"+HASH+"</p>"),null);
  assert.equal(magnetFromTheRarBgInfoHash("<p>Info Hash: "+"z".repeat(40)+"</p>"),null);
  assert.equal(magnetFromTheRarBgInfoHash("<p>Info Hash: "+HASH+"</p><p>Info Hash: "+"b".repeat(40)+"</p>"),null);
  assert.equal(magnetFromTheRarBgInfoHash("<script>var x='Info Hash: "+HASH+"'</script>"),null);
  assert.equal(magnetFromTheRarBgInfoHash("<style>Info Hash: "+HASH+"</style>"),null);
  assert.equal(magnetFromTheRarBgInfoHash("<p>Info Hash: "+HASH+"</p>"+" ".repeat(3_000_010)),null);
  assert.equal(magnetFromTheRarBgInfoHash(null),null);
});

// Real TheRarBg music/detail pages place a ".torrent File" anchor in
// their own "Torrent:" action row before "Info Hash:".
// A missing textual hash can be recovered from that source-provided metadata
// pointer, without ever downloading a torrent or querying a second indexer.
const cacheLink=(hash=HASH,host="itorrents.org")=>
  "<div>Torrent: <span>Magnet Download</span> "+
  "<a class='download' href='https://"+host+"/torrent/"+hash.toUpperCase()+".torrent'>.torrent File</a>"+
  " <button>Copy Magnet</button> <span>Info Hash:</span> <input readonly value=''></div>";

test("source-endorsed iTorrents .torrent link provides BTIH even when visible label is blank",()=>{
  assert.equal(magnetFromTheRarBgInfoHash(cacheLink()),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink()),"magnet:?xt=urn:btih:"+HASH);
  const withSpan=cacheLink().replace(".torrent File</a>", "<strong>.torrent File</strong></a>");
  assert.equal(magnetFromTheRarBgSourceMetadata(withSpan),"magnet:?xt=urn:btih:"+HASH);
});

// Public TheRarBg detail screenshot shows the action row labelled Torrent:
// with Magnet Download, .torrent File, Copy Magnet and Info Hash. A hash
// stored solely in that field's input value must be source-owned, never a
// hash borrowed from the page's related posts or from scripts.
const inputRow=(hash=HASH)=>"<table><tr><th>Torrent:</th><td>"+
  "<a>Magnet Download</a> <a>.torrent File</a> <button>Copy Magnet</button>"+
  "<div><strong>Info Hash:</strong> <input readonly value='"+hash+"'></div>"+
  "</td></tr></table>";

test("TheRarBg original Info Hash input value supplies a source-owned BTIH",()=>{
  assert.equal(magnetFromTheRarBgInfoHash(inputRow()),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow()),"magnet:?xt=urn:btih:"+HASH);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow(HASH.toUpperCase())),
    "magnet:?xt=urn:btih:"+HASH);
});

test("TheRarBg input fallback refuses unlabelled, unrelated, script-only, and malformed hashes",()=>{
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow().replace("Info Hash:","Other Hash:")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow().replace("Magnet Download","Other Action")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow().replace("Copy Magnet","Other Action")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow("z".repeat(40))),null);
  assert.equal(magnetFromTheRarBgSourceMetadata("<script>"+inputRow()+"</script>"),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(
    "<h2>Similar Posts:</h2><div>Info Hash:<input value='"+HASH+"'></div>"),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(
    inputRow().replace("<input readonly", "</td></tr><tr><td><input readonly")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(
    inputRow()+ "<input value='"+"b".repeat(40)+"'>"),
    "magnet:?xt=urn:btih:"+HASH);
});

test("TheRarBg rejects ambiguous source input, text and cache-link evidence",()=>{
  const second="b".repeat(40);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow()+inputRow(second)),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow()+"<p>Info Hash: "+second+"</p>"),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow()+cacheLink(second)),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(inputRow()+cacheLink()),"magnet:?xt=urn:btih:"+HASH);
});

test("one exact TheRarBg detail HTML input value resolves without other source requests",async()=>{
  const prior=globalThis.HTMLRewriter;
  class FakeHTMLRewriter {on(){return this} transform(response){return response}}
  globalThis.HTMLRewriter=FakeHTMLRewriter;
  let calls=0;
  try{
    const detailUrl="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
    const result=await resolveLegacy("therarbag",detailUrl,async(url,options)=>{
      calls++;
      assert.equal(url,detailUrl);
      assert.equal(options.redirect,"manual");
      return new Response(inputRow(),{status:200,headers:{"content-type":"text/html"}});
    });
    assert.equal(result.magnet,"magnet:?xt=urn:btih:"+HASH);
    assert.equal(calls,1);
  }finally{
    if(prior===undefined)delete globalThis.HTMLRewriter;
    else globalThis.HTMLRewriter=prior;
  }
});

test("source-endorsed cache hash must agree with any labelled original hash",()=>{
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace("<input readonly value=''>",HASH)),
    "magnet:?xt=urn:btih:"+HASH);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace("<input readonly value=''>","b".repeat(40))),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink()+"<p>Info Hash: "+"b".repeat(40)+"</p>"),null);
});

test("reject off-origin cache lookalikes, any HTTP cache, and unrelated source links",()=>{
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink(HASH,"itorrents.org.attacker.test")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace("https://","http://")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace(".torrent'>",".torrent?u=tracking'>")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace("Torrent:", "Recommended posts:")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink().replace("Info Hash:", "Related torrent:")),null);
  assert.equal(magnetFromTheRarBgSourceMetadata("<script>"+cacheLink()+"</script>"),null);
  assert.equal(magnetFromTheRarBgSourceMetadata(cacheLink()+cacheLink("b".repeat(40))),null);
});

test("original TheRarBg .torrent action resolves with one allowed detail fetch and zero torrent downloads",async()=>{
  const prior=globalThis.HTMLRewriter;
  class FakeHTMLRewriter {on(){return this} transform(response){return response}}
  globalThis.HTMLRewriter=FakeHTMLRewriter;
  let called=0;
  try{
    const url="https://therarbg.com/post-detail/a-test/public-domain-test/";
    const result=await resolveLegacy("therarbag",url,async(target,options)=>{
      called++;
      assert.equal(target,url);
      assert.equal(options.redirect,"manual");
      return new Response(cacheLink(),{status:200,headers:{"content-type":"text/html"}});
    });
    assert.equal(result.magnet,"magnet:?xt=urn:btih:"+HASH);
    assert.equal(called,1);
  }finally{
    if(prior===undefined)delete globalThis.HTMLRewriter;
    else globalThis.HTMLRewriter=prior;
  }
});

test("same-origin TheRarBg HTML with labelled hash resolves with one request",async()=>{
  const prior=globalThis.HTMLRewriter;
  class FakeHTMLRewriter {on(){return this} transform(response){return response}}
  globalThis.HTMLRewriter=FakeHTMLRewriter;
  let called=0;
  try{
    const url="https://therarbg.com/post-detail/a-test/public-domain-test/";
    const result=await resolveLegacy("therarbag",url,async(target,options)=>{
      called++;assert.equal(target,url);assert.equal(options.redirect,"manual");
      return new Response(sample,{status:200,headers:{"content-type":"text/html"}});
    });
    assert.equal(result.magnet,"magnet:?xt=urn:btih:"+HASH);
    assert.equal(called,1);
  }finally{
    if(prior===undefined)delete globalThis.HTMLRewriter;
    else globalThis.HTMLRewriter=prior;
  }
});

test("HTTP 502 stays a real upstream failure, never bypassed or retried",async()=>{
  let called=0;
  await assert.rejects(
    resolveLegacy("therarbag","https://therarbg.com/post-detail/a-test/public-domain-test/",async()=>{
      called++;return new Response("Bad Gateway",{status:502});
    }),
    /provider HTTP 502/
  );
  assert.equal(called,1);
});

test("unapproved details origin never fetched",async()=>{
  let called=0;
  await assert.rejects(
    resolveLegacy("therarbag","https://other.example/post-detail/a-test",async()=>{
      called++;throw Error("should not fetch");
    }),
    /details URL not allowed/
  );
  assert.equal(called,0);
});

test("localized fallback can direct users to source Details after a 502",()=>{
  const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
  const ui=readFileSync(new URL("../../web/i18n.js",import.meta.url),"utf8");
  assert.match(app,/function magnetFailureText\(item,error\)/);
  assert.match(app,/item\?\.provider==="therarbag"/);
  assert.match(ui,/TheRarBg could not provide this magnet/);
  assert.match(ui,/Deschide „Detalii/);
  assert.match(ui,/Apri «Dettagli/);
});
