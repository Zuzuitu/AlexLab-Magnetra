import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {safeProviderHtml} from "../src/legacy-adapters.mjs";
test("BTDigg outer budget is 18s; original shared 11s remains for other legacy adapters",async()=>{
 const fetcher=async(url,opts)=>new Response("<html>ok</html>",{headers:{"content-type":"text/html"}});
 assert.equal(await safeProviderHtml("https://example.test",{},fetcher,18000),"<html>ok</html>");
 await assert.rejects(()=>safeProviderHtml("https://example.test",{},fetcher,18001),/Invalid bounded/);
 const source=fs.readFileSync(new URL("../src/legacy-adapters.mjs",import.meta.url),"utf8");
 assert.match(source,/const TIMEOUT = 11_000/);
 assert.match(source,/const BTDIGG_WORKER_TIMEOUT = 18_000/);
 assert.match(source,/id==="btdigg"\?BTDIGG_WORKER_TIMEOUT:TIMEOUT/);
});
