import test from "node:test";
import assert from "node:assert/strict";
import {HTML_PROVIDER_SPECS} from "../src/html-adapters.mjs";

test("BTDigg one_result holds its OWN title, size, details and magnet",()=>{
 const spec=HTML_PROVIDER_SPECS.btdigg;
 assert.equal(spec.host,"https://btdig.com");
 assert.equal(spec.rows,"div.one_result",
  "never split the torrent_name and torrent_magnet siblings into separate result rows");
 assert.equal(spec.name,"div.torrent_name a");
 assert.equal(spec.details,"div.torrent_name a");
 assert.equal(spec.magnet,'div.torrent_magnet a[href^="magnet:?xt=urn:btih:"]');
 assert.equal(spec.size,"span.torrent_size");
 assert.equal(spec.date,"span.torrent_age");
 assert.equal(spec.search("ubuntu"),"https://btdig.com/search?q=ubuntu");
 // HTMLRewriter handlers intentionally anchor all fields to spec.rows.
 // These selectors guarantee every field is sought under the same source row.
 for(const field of ["name","magnet","size","details"]){
  assert.ok((spec.rows+" "+spec[field]).startsWith("div.one_result "));
 }
 assert.notEqual(spec.rows,"div.one_result > div");
});

test("no other HTML provider search contract is affected by BTDigg row repair",()=>{
 assert.equal(HTML_PROVIDER_SPECS.dmhy.rows,"table#topic_list > tbody > tr");
 assert.equal(HTML_PROVIDER_SPECS.torrentkitty.rows,"table#archiveResult > tbody > tr");
 assert.equal(HTML_PROVIDER_SPECS.limetorrents.rows,".table2 > tbody > tr");
});
