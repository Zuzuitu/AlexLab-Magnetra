import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const script=readFileSync(new URL("../../rock64/diagnose_btdigg_readonly.sh",import.meta.url),"utf8");

test("Rock64 BTDigg diagnostics read only existing service state and redacted timing events",()=>{
 assert.match(script,/SERVICE="magnetra-btdigg.service"/);
 assert.match(script,/systemctl is-active --quiet/);
 assert.match(script,/journalctl -u "\$SERVICE" --since "-120 minutes"/);
 assert.match(script,/obj.get\("event"\)!="btdigg_upstream_timing"/);
 assert.match(script,/safe=\("failure","total_ms","dns_ms","tcp_ms","tls_ms","open_ms","read_ms"\)/);
 assert.match(script,/for row in rows\[-8:\]/);
 for(const forbidden of [
  /\bcurl\b/,/\bwget\b/,/\bssh\b/,/\bscp\b/,/\bngrok\b/,
  /systemctl (?:restart|stop|start|reload|enable|disable)/,
  /\beval\s/,/\bexec\s/,/\/etc\/magnetra-btdigg\/gateway\.env/,
  /MAGNETRA_BTDIGG_TOKEN=|Bearer\s+/,
 ])assert.doesNotMatch(script,forbidden);
});
