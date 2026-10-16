#!/usr/bin/env node
// Offline 46-provider recovery report. Reads tracked source audit + measured
// Rock64 evidence only. NO network, credentials, magnet URLs or side effects.
import {recoveryPlan,recoverySummary} from "../worker/src/recovery-strategy.mjs";

const args=process.argv.slice(2);
if(args.length>1||args.some(a=>!["--json","--summary"].includes(a))){
 console.error("Usage: node scripts/recovery-plan.mjs [--json | --summary]");
 process.exitCode=2;
}else{
 const summary=recoverySummary(),plan=recoveryPlan();
 if(args.includes("--json")){
  console.log(JSON.stringify({summary,providers:plan},null,2));
 }else{
  console.log("Magnetra: evidence-gated provider recovery (OFFLINE, no network)");
  console.log("Historical observation:",summary.historicalObservedAt,
   "run",summary.historicalAuditRun);
  console.log("Original providers:",summary.total,
   "— NO live-uptime or automatic gateway claims");
  console.log("Strategies:",JSON.stringify(summary.byStrategy));
  if(!args.includes("--summary")){
   console.log("PRIORITY | PROVIDER | STRATEGY | NEXT APPROVED EVIDENCE ACTION");
   for(const p of plan)console.log(
    String(p.priority).padStart(3), "|",
    p.provider.padEnd(19), "|",p.strategy.padEnd(27),"|",p.nextAction
   );
  }
 }
}
