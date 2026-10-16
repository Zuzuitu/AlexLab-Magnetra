import test from "node:test";
import assert from "node:assert/strict";
import probeWorker, {probeTunnel, TARGET} from "../probes/tunnel-1042-probe.mjs";

const health = "https://magnetra-rock64.alexlab.media/healthz";

test("fixed origin, one no-secret GET with bounded timeout and manual redirects", async () => {
  let requests = 0;
  const result = await probeTunnel(async (url, options) => {
    requests++;
    assert.equal(url, health);
    assert.equal(url, TARGET);
    assert.equal(options.method, "GET");
    assert.equal(options.redirect, "manual");
    assert.equal(options.headers.accept, "application/json");
    assert.equal(Object.hasOwn(options.headers, "authorization"), false);
    assert.ok(options.signal instanceof AbortSignal);
    return new Response(null, {status: 401});
  });
  assert.equal(requests, 1);
  assert.deepEqual(result, {result: "PASS_UNAUTHENTICATED_401", status: 401});
});

test("1042 HTML response recognized but response body never returned", async () => {
  const marker = "private secret do not print";
  const result = await probeTunnel(async () => new Response(
    "<html>Cloudflare Error 1042 " + marker + "</html>",
    {status: 530, headers: {"content-type": "text/html"}}
  ));
  assert.deepEqual(result, {result: "CLOUDFLARE_1042", status: 530});
  assert.ok(!JSON.stringify(result).includes(marker));
});

test("1042 rejected fetch exception classified without exposing its text", async () => {
  const marker = "private token do not print";
  const result = await probeTunnel(async () => {
    throw new Error("Cloudflare error 1042 " + marker);
  });
  assert.deepEqual(result, {result: "CLOUDFLARE_1042", status: null});
  assert.ok(!JSON.stringify(result).includes(marker));
});

test("timeouts and arbitrary transport error messages are sanitized", async () => {
  assert.deepEqual(await probeTunnel(async () => {
    throw new DOMException("Timeout", "TimeoutError");
  }), {result: "TIMEOUT", status: null});
  const marker = "private magnet or title";
  const result = await probeTunnel(async () => {
    throw new TypeError(marker);
  });
  assert.deepEqual(result, {result: "TRANSPORT_ERROR", status: null});
  assert.ok(!JSON.stringify(result).includes(marker));
});

test("wrong status, redirect and 530 without 1042 are never marked PASS", async () => {
  for (const [status, verdict] of [[200, "UNEXPECTED_HTTP"],
    [403, "UNEXPECTED_HTTP"], [302, "UNEXPECTED_REDIRECT"],
    [530, "UNEXPECTED_HTTP"]]) {
    const result = await probeTunnel(async () => new Response("bad", {status}));
    assert.deepEqual(result, {result: verdict, status});
  }
});

test("entrypoint rejects paths, querystrings and methods without outbound fetch", async () => {
  const urls = ["/", "/probe?url=https://evil.example", "/healthz", "/probe/"];
  for (const path of urls) {
    const response = await probeWorker.fetch(new Request("https://temp.example" + path));
    assert.equal(response.status, 404);
  }
  const post = await probeWorker.fetch(new Request("https://temp.example/probe", {method: "POST"}));
  assert.equal(post.status, 404);
});

test("static probe has no confidential data, mutable origin, Worker prod route or secrets", async () => {
  const source = await import("node:fs/promises")
    .then(fs => fs.readFile(new URL("../probes/tunnel-1042-probe.mjs", import.meta.url), "utf8"));
  assert.ok(source.includes("https://magnetra-rock64.alexlab.media/healthz"));
  for (const forbidden of ["MAGNETRA_GATEWAY_TOKEN", "BTDIGG_GATEWAY_TOKEN",
    "index.alexlab.media", "global_fetch_strictly_public",
    "wrangler deploy", "magnet:?", "/v1/eztvx/torrents"]) {
    assert.ok(!source.includes(forbidden), forbidden);
  }
});
