import test from "node:test";
import assert from "node:assert/strict";
import {PROVIDERS} from "../src/catalog.mjs";
import {SOURCE_AUDIT} from "../src/source-audit.mjs";
import {RECOVERY_EVIDENCE_DATE,ROCK64_EVIDENCE,recoveryFor,recoveryPlan,recoverySummary} from "../src/recovery-strategy.mjs";
import worker from "../src/index.mjs";

test("all original 46 providers get one deterministic, complete strategy",()=>{
 const plan=recoveryPlan();
 assert.equal(plan.length,46);
 assert.equal(new Set(plan.map(x=>x.provider)).size,46);
 assert.deepEqual(plan.map(x=>x.provider).sort(),PROVIDERS.map(x=>x.id).sort());
 assert.deepEqual(plan.map(x=>x.provider).sort(),Object.keys(SOURCE_AUDIT.outcomes).sort());
 assert.deepEqual(recoveryPlan(),plan);
 for(const p of plan){
  assert.equal(p.historicalState,SOURCE_AUDIT.outcomes[p.provider].state);
  assert.equal(p.autoReroute,false);
  assert.equal(p.proof,"dated_observation_not_live_uptime");
  assert.match(p.nextAction,/^[A-Z0-9_]+$/);
  assert.equal(typeof p.priority,"number");
  assert.ok(p.rock64Evidence);
 }
 assert.equal(recoveryFor("invented"),null);
});

test("only evidence-backed EZTV and preexisting BTDigg can use existing gateways",()=>{
 const ready=recoveryPlan().filter(x=>x.gatewayEligible);
 assert.deepEqual(ready.map(x=>x.provider).sort(),["btdigg","eztvx"]);
 assert.deepEqual(recoveryFor("eztvx").strategy,"GATEWAY_READY_FOR_AUTH_TEST");
 assert.equal(recoveryFor("eztvx").nextAction,"OWNER_APPROVED_WORKER_AUTHENTICATED_E2E");
 assert.equal(recoveryFor("btdigg").strategy,"EXISTING_GATEWAY");
 assert.equal(recoveryFor("btdigg").rock64Evidence,"existing_gateway");
 assert.equal(ready.every(x=>x.autoReroute===false),true);
});

test("real Rock64 403 blocks naive residential rerouting",()=>{
 for(const id of ["1337x","bt4g","extdotto"]){
  assert.equal(recoveryFor(id).strategy,"BLOCKED_BOTH_PATHS");
  assert.equal(recoveryFor(id).gatewayEligible,false);
  assert.equal(recoveryFor(id).nextAction,"DO_NOT_REROUTE_WITHOUT_NEW_SOURCE_EVIDENCE");
 }
});

test("only historical redirects receive investigation, not auto-follow/host migration",()=>{
 for(const id of ["bitsearch","oxtorrent","torrent9"]){
  const item=recoveryFor(id);
  assert.equal(item.strategy,"CHECK_REDIRECT_CANDIDATE");
  assert.equal(item.gatewayEligible,false);
  assert.equal(item.autoReroute,false);
  assert.equal(item.nextAction,"VERIFY_NEW_SOURCE_ORIGIN_AND_REAL_ROWS");
  assert.equal(ROCK64_EVIDENCE[id].kind,"redirect_candidate");
 }
});

test("unverified empties remain unverified, rate limits do not auto retry",()=>{
 for(const id of ["ytsmx","anilibria","animetosho"]){
  assert.equal(recoveryFor(id).strategy,"VERIFY_EMPTY_SAMPLE");
 }
 assert.equal(recoveryFor("nyaasi").strategy,"RATE_LIMITED");
 assert.equal(recoveryFor("nyaasi").nextAction,"HONOR_RATE_LIMIT_NO_AUTORETRY");
 assert.equal(recoveryFor("torrentz").strategy,"LOCAL_TRANSPORT_FAILURE");
 assert.equal(recoveryFor("xxxclub").strategy,"UPSTREAM_FAILURE");
 assert.equal(recoveryFor("knaben").strategy,"KEEP_OBSERVED_RESULTS");
});

test("summary exact 46, priority ordering, fixed audit provenance and no secrets",()=>{
 const summary=recoverySummary();
 assert.equal(summary.total,46);
 assert.equal(summary.catalogCount,46);
 assert.equal(Object.values(summary.byStrategy).reduce((a,b)=>a+b,0),46);
 assert.equal(summary.historicalAuditRun,38373699387);
 assert.equal(summary.evidenceAsOf,RECOVERY_EVIDENCE_DATE);
 assert.equal(summary.requiresRealSourceProof,true);
 assert.equal(summary.autoReroute,false);
 assert.equal(summary.noProviderDeleted,true);
 for(const id of summary.gatewayEligible)assert.ok(["btdigg","eztvx"].includes(id));
 const plan=recoveryPlan();
 assert.deepEqual(plan.map(x=>x.priority),[...plan.map(x=>x.priority)].sort((a,b)=>a-b));
 assert.ok(!JSON.stringify(plan).includes("magnet:?"));
 assert.ok(!JSON.stringify(plan).includes("MAGNETRA_GATEWAY_TOKEN"));
});

test("recovery endpoint is a static evidence plan, not a remote fetch or health claim",async()=>{
 const rsp=await worker.fetch(new Request("https://index.alexlab.media/api/recovery-plan"),{});
 assert.equal(rsp.status,200);
 const obj=await rsp.json();
 assert.equal(obj.summary.total,46);
 assert.equal(obj.providers.length,46);
 assert.deepEqual(obj.providers,recoveryPlan());
 assert.equal(obj.summary.autoReroute,false);
 const other=await worker.fetch(new Request("https://index.alexlab.media/api/providers"),{});
 const providers=(await other.json()).providers;
 assert.equal(providers.length,46);
 assert.deepEqual(providers.map(p=>p.recovery),PROVIDERS.map(p=>recoveryFor(p.id)));
});


test("2026-10-16 Rock64 alternate-host results are not mistaken for recovered indexers",()=>{
 for(const id of ["oxtorrent","torrent9"]){
  const data=recoveryFor(id);
  assert.equal(data.strategy,"CHECK_REDIRECT_CANDIDATE");
  assert.match(data.rock64Detail,/http_200_table_hint_only_20261016$/);
  assert.equal(data.gatewayEligible,false);
  assert.equal(data.autoReroute,false);
 }
 const bitsearch=recoveryFor("bitsearch");
 assert.match(bitsearch.rock64Detail,/http_520_20261016_no_verified_rows$/);
 assert.equal(bitsearch.gatewayEligible,false);
});
