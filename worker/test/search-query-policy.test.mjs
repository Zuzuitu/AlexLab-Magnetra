import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {PROVIDERS} from "../src/catalog.mjs";
import {planSearchQuery} from "../src/query-relevance.mjs";
import {CURATED_EXACT_PROVIDER_IDS,sourceQueryFor,sourceQueryModeFor} from "../src/search-query-policy.mjs";

const exact="The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA";
const normalized="The Dog Stars 2026";
const short="The Dog Stars 2026";
const plan=planSearchQuery(exact);

test("strict 10 curated source contract equals current PWA visibility, without reviving hidden providers",()=>{
 const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
 const m=app.match(/const hiddenIndexerIds=new Set\(\[([^\]]+)\]\)/);
 assert.ok(m,"source-visibility manifest must be parsed exactly");
 const hidden=new Set(JSON.parse("["+m[1]+"]"));
 const visible=PROVIDERS.filter(p=>!hidden.has(p.id)).map(p=>p.id).sort();
 assert.equal(hidden.size,36);
 assert.equal(visible.length,10);
 assert.deepEqual([...CURATED_EXACT_PROVIDER_IDS].sort(),visible);
 assert.equal(hidden.has("subsplease"),true);
 assert.equal(hidden.has("audiobookbay"),true);
 assert.equal(CURATED_EXACT_PROVIDER_IDS.includes("subsplease"),false);
 assert.equal(CURATED_EXACT_PROVIDER_IDS.includes("audiobookbay"),false);
});

test("BTDigg gets owner-proven literal; 9 others use one broad title/year request for all fallback tiers",()=>{
 assert.equal(plan.searchedAs,short);
 for(const id of CURATED_EXACT_PROVIDER_IDS){
  const actual=sourceQueryFor(id,exact,plan);
  assert.equal(actual,id==="btdigg"?exact:normalized,id);
  assert.equal(sourceQueryModeFor(id,exact,plan),id==="btdigg"?"all-terms-literal":"title-ranked-fallback");
  const terms=new Set((actual.match(/[\p{L}\p{N}]+/gu)||[]).map(x=>x.toLowerCase()));
  for(const t of ["dog","stars","2026"])
   assert.ok(terms.has(t),`${id} lost film identity term ${t}`);
  if(id!=="btdigg"){
   for(const redundant of ["1080p","x265","10bit","webrip","6ch","hevc","psa"])
    assert.equal(terms.has(redundant),false,`${id} must not block alternative formats with ${redundant}`);
  }
 }
});

test("hidden 36 providers retain title/year discovery, but original strict matching is separate",()=>{
 for(const provider of PROVIDERS.filter(x=>!CURATED_EXACT_PROVIDER_IDS.includes(x.id))){
  assert.equal(sourceQueryFor(provider.id,exact,plan),short,provider.id);
  assert.equal(sourceQueryModeFor(provider.id,exact,plan),"title",provider.id);
 }
});

test("ordinary movie titles, hashes and IMDb lookups preserve exact user text",()=>{
 for(const q of ["The Dog Stars 2026","Ubuntu 24.04","tt1234567","abc ".trim(),"the good dinosaur 2015"]){
  const p=planSearchQuery(q);
  for(const id of CURATED_EXACT_PROVIDER_IDS)
   assert.equal(sourceQueryFor(id,q,p),q,id+": "+q);
 }
});

test("one bad source cannot trigger an implicit second source query or fallback",()=>{
 // Planner is pure and returns one deterministic string per provider.
 // It never accesses network APIs or creates batches.
 const a=sourceQueryFor("thepiratebay",exact,plan);
 assert.equal(a,normalized);
 assert.equal(sourceQueryFor("thepiratebay",exact,plan),a);
 assert.equal(sourceQueryFor("btdigg",exact,plan),exact);
 assert.equal(sourceQueryFor("ytsmx",exact,plan),short);
});
