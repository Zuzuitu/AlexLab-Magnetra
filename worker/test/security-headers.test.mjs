import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const headers=readFileSync(new URL("../../web/_headers",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const worker=readFileSync(new URL("../src/index.mjs",import.meta.url),"utf8");

function requiredHeader(name) {
  const line=headers.split(/\r?\n/).find(line=>line.trimStart().startsWith(name+": "));
  assert.ok(line,"Required header missing: "+name);
  return line.split(": ").slice(1).join(": ");
}

test("Cloudflare static asset headers define conservative browser isolation",()=>{
  assert.match(headers,/^\/\*$/m);
  const csp=requiredHeader("Content-Security-Policy");
  for(const directive of ["default-src 'self'","script-src 'self'","connect-src 'self'","object-src 'none'","frame-ancestors 'none'","base-uri 'none'","form-action 'self'"])
    assert.ok(csp.includes(directive),"CSP directive missing: "+directive);
  assert.ok(!csp.includes("'unsafe-eval'"));
  assert.ok(!/script-src[^;]*unsafe-inline/.test(csp));
  assert.equal(requiredHeader("X-Frame-Options"),"DENY");
  assert.equal(requiredHeader("X-Content-Type-Options"),"nosniff");
  assert.equal(requiredHeader("Referrer-Policy"),"no-referrer");
  assert.ok(requiredHeader("Permissions-Policy").includes("camera=()"));
  assert.ok(!/Access-Control-Allow-Origin:/i.test(headers));
});

test("frontend keeps external code out and Worker API remains separate",()=>{
  for(const scriptTag of html.match(/<script\b[^>]*>/g)??[])
    assert.match(scriptTag,/\bsrc="\/[^"]+"/);
  assert.match(worker,/url\.pathname\.startsWith\("\/api\/"\)/);
  assert.match(worker,/env\?\.ASSETS\) return env\.ASSETS\.fetch\(request\)/);
  assert.match(worker,/x-content-type-options"\s*:\s*"nosniff"/);
});
