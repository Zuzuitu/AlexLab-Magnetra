import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {magnetFromTheRarBgInfoHash,resolveLegacy} from "../src/legacy-adapters.mjs";

const HASH="a".repeat(40);
const sample='<html><main><h1>Public-domain sample</h1><div><strong>Info Hash:</strong> <code>'+HASH.toUpperCase()+'</code> <button>Copy Magnet</button></div></main></html>';

test("TheRarBg unique source-labelled info hash yields a BTIH magnet",()=>{
  assert.equal(magnetFromTheRarBgInfoHash(sample),"magnet:?xt=urn:btih:"+HASH);
  assert.equal(magnetFromTheRarBgInfoHash("<p>Info Hash: &#160;<b>"+HASH+"</b></p>"),"magnet:?xt=urn:btih:"+HASH);
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
