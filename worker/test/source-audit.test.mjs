import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {SOURCE_AUDIT,auditFor} from "../src/source-audit.mjs";
import {PROVIDERS} from "../src/catalog.mjs";
import worker from "../src/index.mjs";

test("dated production snapshot covers each of the original 46 providers, without inventing live state",()=>{
 const ids=Object.keys(SOURCE_AUDIT.outcomes);
 assert.equal(ids.length,46);
 assert.deepEqual(ids.sort(),PROVIDERS.map(p=>p.id).sort());
 assert.match(SOURCE_AUDIT.observedAt,/^2026-10-08T/);
 assert.equal(SOURCE_AUDIT.query,"ubuntu");
 assert.equal(SOURCE_AUDIT.workflowRunId,37816874771);
 const rows=Object.values(SOURCE_AUDIT.outcomes);
 assert.equal(rows.filter(x=>x.state==="results").length,12);
 assert.equal(rows.filter(x=>x.state==="empty-unverified").length,12);
 assert.equal(rows.filter(x=>x.state==="error").length,22);
 assert.equal(auditFor("btdigg").code,"TIMEOUT");
 assert.equal(auditFor("nyaasi").code,"RATE_LIMIT");
 assert.equal(auditFor("knaben").state,"results");
 assert.equal(auditFor("imaginary"),null);
});
test("provider endpoint conveys timestamped audit metadata and all 46 source statuses",async()=>{
 const result=await worker.fetch(new Request("https://index.alexlab.media/api/providers"),{});
 assert.equal(result.status,200);
 const data=await result.json();
 assert.equal(data.audit.workflowRunId,37816874771);
 assert.equal(data.providers.length,46);
 for(const p of data.providers)assert.deepEqual(p.lastAudit,SOURCE_AUDIT.outcomes[p.id],p.id);
});
test("source-selection UI never treats all implemented adapters as verified working",()=>{
 const src=readFileSync(new URL("../../web/app.js",import.meta.url),"utf-8");
 const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf-8");
 assert.match(src,/id="selectWorking"|\$\("selectWorking"\)/);
 assert.match(src,/p\.lastAudit\?\.state==="results"/);
 assert.match(src,/\$\("selectAllProviders"\)/);
 assert.ok(!src.includes('state.selected=new Set(state.providers.filter(p=>p.ported).map(p=>p.id));\n  save(STORAGE.selected,[...state.selected]);renderProviders();updateProviderCount();\n });'),"old misleading Select working handler is forbidden");
 assert.ok(html.includes('id="selectAllProviders"'));
 assert.ok(html.includes('Select last-audit results'));
 assert.ok(html.includes('not live uptime'));
});
