import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,existsSync} from "node:fs";

const fromRoot=name=>new URL("../../"+name,import.meta.url);
const html=readFileSync(fromRoot("web/index.html"),"utf8");
const app=readFileSync(fromRoot("web/app.js"),"utf8");
const css=readFileSync(fromRoot("web/styles.css"),"utf8");
const sw=readFileSync(fromRoot("web/sw.js"),"utf8");

test("BTDigg Safari bookmarks, instructions and clipboard imports are completely retired",()=>{
 for(const former of ["btdiggDialog","btdiggButton","btdiggPasteInput",
  "copyBTDiggBookmarklet","btdiggImportFromClipboard","btdiggBookmarkletLink",
  "BTDIGG_IMPORT:","BTDigg în 3 pași","BTDiggBridge","showBTDiggDialog"])
  assert.equal((html+app+css).includes(former),false,"Retired feature must not remain: "+former);
 assert.equal(existsSync(fromRoot("web/btdigg-bridge.js")),false);
 assert.equal(existsSync(fromRoot("worker/test/btdigg-browser-import.test.mjs")),false);
 assert.equal(existsSync(fromRoot("worker/test/btdigg-three-step-guide.test.mjs")),false);
 assert.equal(sw.includes("btdigg-bridge.js"),false);
 assert.equal(sw.includes("alexlab-magnetra-v13"),true);
 assert.ok(sw.includes("/i18n.js"),"translation asset cached and refreshed");
});

test("only BTDigg source-error browser prompt disappears; Flud and provider catalog remain intact",()=>{
 const worker=readFileSync(fromRoot("worker/src/index.mjs"),"utf8");
 const catalog=readFileSync(fromRoot("worker/src/catalog.mjs"),"utf8");
 assert.match(worker,/rock64BTDiggFetcher/);
 assert.match(worker,/id==="btdigg"\?null:directSearchUrl\(id,sourceQuery\)/);
 assert.match(app,/failure\.provider==="btdigg"\?null:\(failure\.openUrl \|\| provider\?\.url\)/);
 assert.equal((catalog.match(/"id": "/g)||[]).length,46);
 assert.match(catalog,/"id": "btdigg"/);
 for(const keep of ["pasteMagnetButton","manualMagnetDialog","companionChip","providersButton"]){
  assert.ok(html.includes('id="'+keep+'"'),"Unrelated capability was deleted: "+keep);
 }
 assert.match(app,/sendMagnet\(\{magnet\}/);
});
