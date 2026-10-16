// One canonical, evidence-based recovery decision for ALL 46 original indexers.
// Planning only: never changes transport, source identity, endpoint or secrets.
// A dated snapshot is NOT live availability. Gateway opt-in is separately gated.
import {PROVIDERS,PROVIDER_MAP} from "./catalog.mjs";
import {SOURCE_AUDIT,auditFor} from "./source-audit.mjs";

export const RECOVERY_EVIDENCE_DATE="2026-10-16";

// Only independently documented Rock64 observations or previously accepted
// gateways go here. Never infer Rock64 success from HTTP 200 or redirects.
export const ROCK64_EVIDENCE=Object.freeze({
 btdigg:Object.freeze({kind:"existing_gateway",detail:"isolated_8796"}),
 eztvx:Object.freeze({kind:"authentic_magnet_parity",detail:"original_8797_8798_53_exact"}),
 "1337x":Object.freeze({kind:"blocked_from_both",detail:"rock64_http_403"}),
 bt4g:Object.freeze({kind:"blocked_from_both",detail:"rock64_http_403"}),
 extdotto:Object.freeze({kind:"blocked_from_both",detail:"rock64_http_403"}),
 bitsearch:Object.freeze({kind:"redirect_candidate",detail:"bitsearch.to_to_bitsearch.eu"}),
 oxtorrent:Object.freeze({kind:"redirect_candidate",detail:"oxtorrent.co_to_www.oxtorrent.co"}),
 torrent9:Object.freeze({kind:"redirect_candidate",detail:"www6.torrent9.to_to_www7.torrent9.to"}),
 torrentz:Object.freeze({kind:"transport_failure",detail:"torrentz2.nz_rock64"}),
});

const POLICIES=Object.freeze({
 KEEP_OBSERVED_RESULTS:Object.freeze({priority:70,nextAction:"RECHECK_WITH_REPRESENTATIVE_QUERY",gatewayEligible:false}),
 VERIFY_EMPTY_SAMPLE:Object.freeze({priority:65,nextAction:"REPEAT_RELEVANT_QUERY_BEFORE_DECLARING_FAILURE",gatewayEligible:false}),
 COMPARE_EGRESS:Object.freeze({priority:30,nextAction:"BOUNDED_READONLY_RESIDENTIAL_PROBE",gatewayEligible:false}),
 CHECK_REDIRECT_CANDIDATE:Object.freeze({priority:15,nextAction:"VERIFY_NEW_SOURCE_ORIGIN_AND_REAL_ROWS",gatewayEligible:false}),
 BLOCKED_BOTH_PATHS:Object.freeze({priority:80,nextAction:"DO_NOT_REROUTE_WITHOUT_NEW_SOURCE_EVIDENCE",gatewayEligible:false}),
 RATE_LIMITED:Object.freeze({priority:85,nextAction:"HONOR_RATE_LIMIT_NO_AUTORETRY",gatewayEligible:false}),
 UPSTREAM_FAILURE:Object.freeze({priority:90,nextAction:"VERIFY_SOURCE_UPSTREAM_STATUS",gatewayEligible:false}),
 LOCAL_TRANSPORT_FAILURE:Object.freeze({priority:55,nextAction:"DIAGNOSE_ROCK64_DNS_TLS_TRANSPORT",gatewayEligible:false}),
 GATEWAY_READY_FOR_AUTH_TEST:Object.freeze({priority:5,nextAction:"OWNER_APPROVED_WORKER_AUTHENTICATED_E2E",gatewayEligible:true}),
 EXISTING_GATEWAY:Object.freeze({priority:75,nextAction:"PRESERVE_EXISTING_BTDIGG_GATEWAY",gatewayEligible:true})
});

function policyFor(id,audit,evidence){
 if(id==="btdigg")return "EXISTING_GATEWAY";
 if(id==="eztvx")return "GATEWAY_READY_FOR_AUTH_TEST";
 if(evidence?.kind==="blocked_from_both")return "BLOCKED_BOTH_PATHS";
 if(evidence?.kind==="redirect_candidate")return "CHECK_REDIRECT_CANDIDATE";
 if(evidence?.kind==="transport_failure")return "LOCAL_TRANSPORT_FAILURE";
 if(audit?.state==="results")return "KEEP_OBSERVED_RESULTS";
 if(audit?.state==="empty-unverified")return "VERIFY_EMPTY_SAMPLE";
 if(audit?.code==="RATE_LIMIT")return "RATE_LIMITED";
 if(audit?.code==="UPSTREAM_ERROR")return "UPSTREAM_FAILURE";
 return "COMPARE_EGRESS";
}

/** No arbitrary IDs/URLs, no auto-fallback to unrelated providers. */
export function recoveryFor(id){
 if(!PROVIDER_MAP.has(id))return null;
 const audit=auditFor(id);
 const evidence=ROCK64_EVIDENCE[id]||null;
 const strategy=policyFor(id,audit,evidence);
 const policy=POLICIES[strategy];
 return Object.freeze({
  provider:id,
  historicalState:audit?.state||"unverified",
  historicalErrorCode:audit?.code||null,
  strategy,
  priority:policy.priority,
  nextAction:policy.nextAction,
  rock64Evidence:evidence?.kind||"not_tested",
  rock64Detail:evidence?.detail||null,
  // Eligibility here is limited to existing, already tested endpoints;
  // it never means a production Worker secret or route was enabled.
  gatewayEligible:policy.gatewayEligible,
  autoReroute:false,
  proof:"dated_observation_not_live_uptime"
 });
}

export function recoveryPlan(){
 return PROVIDERS.map(p=>recoveryFor(p.id))
  .sort((a,b)=>a.priority-b.priority||a.provider.localeCompare(b.provider));
}

export function recoverySummary(){
 const planned=recoveryPlan();
 const byStrategy={};
 for(const p of planned)byStrategy[p.strategy]=(byStrategy[p.strategy]||0)+1;
 return Object.freeze({
  total:planned.length,
  catalogCount:PROVIDERS.length,
  historicalObservedAt:SOURCE_AUDIT.observedAt,
  historicalAuditRun:SOURCE_AUDIT.workflowRunId,
  evidenceAsOf:RECOVERY_EVIDENCE_DATE,
  byStrategy,
  gatewayEligible:planned.filter(p=>p.gatewayEligible).map(p=>p.provider),
  requiresRealSourceProof:true,
  autoReroute:false,
  noProviderDeleted:true
 });
}
