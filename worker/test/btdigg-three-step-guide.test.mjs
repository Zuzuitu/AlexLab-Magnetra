import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const css=readFileSync(new URL("../../web/styles.css",import.meta.url),"utf8");
const start=html.indexOf('<dialog id="btdiggDialog"');
const end=html.indexOf('<dialog id="manualMagnetDialog"');
const dialog=html.slice(start,end);
const guide=dialog.match(/<ol class="btdigg-guide-steps">([\s\S]*?)<\/ol>/)?.[1]||"";
const steps=[...guide.matchAll(/<li class="btdigg-guide-step">([\s\S]*?)<\/li>/g)].map(match=>match[1]);

test("BTDigg iPhone instructions contain exactly 3 numbered steps in the right order",()=>{
 assert.ok(start>=0&&end>start,"BTDigg tutorial dialog must exist");
 assert.ok(dialog.includes("BTDigg în 3 pași"));
 assert.equal(steps.length,3,"one-time Safari configuration, BTDigg search, and PWA import");
 assert.match(steps[0],/Doar prima dată/);
 assert.match(steps[0],/Safari/);
 assert.match(steps[0],/Semne de carte/);
 assert.match(steps[0],/Editare/);
 assert.match(steps[0],/Adresă/);
 assert.match(steps[0],/Salvează/);
 assert.match(steps[1],/Caută pe BTDigg/);
 assert.match(steps[1],/Magnetra BTDigg/);
 assert.match(steps[2],/Adu rezultatele în Magnetra/);
 assert.match(steps[2],/Send to Flud/);
 assert.match(css,/counter-reset:btdiggstep/);
 assert.match(css,/content:counter\(btdiggstep\)/);
});
test("each BTDigg step has its own wired action; optional complex choices are collapsed",()=>{
 const idPerStep=["copyBTDiggClipboardBookmarklet","btdiggOpenSearch","btdiggImportFromClipboard"];
 for(let i=0;i<3;i++){
  assert.ok(steps[i].includes('id="'+idPerStep[i]+'"'),"Step "+(i+1)+" action exists");
  assert.equal(steps[i].includes("btdiggPasteInput"),false,"Manual input must not interrupt the main 3-step guide");
 }
 assert.ok(dialog.includes('<details class="btdigg-more"'));
 assert.ok(dialog.includes('id="btdiggImportManual"'));
 assert.ok(dialog.includes('id="btdiggPasteInput"'));
 assert.ok(dialog.indexOf('<details class="btdigg-more"')>dialog.indexOf('</ol>'));
 for(const id of [...idPerStep,"copyBTDiggBookmarklet","btdiggImportManual","btdiggPasteInput","btdiggMore","btdiggStepStatus"]){
  assert.equal(html.split('id="'+id+'"').length-1,1,"Unique UI ID "+id);
 }
 assert.match(app,/\$\("copyBTDiggClipboardBookmarklet"\)\.addEventListener\("click",\(\)=>copyBTDiggCode\("copy"\)\)/);
 assert.match(app,/\$\("btdiggImportFromClipboard"\)\.addEventListener\("click"/);
 assert.match(app,/importBTDiggFromClipboard\(text\)/);
 assert.match(app,/\$\("btdiggMore"\)\.open=true/);
});
test("Safari search links remain BTDigg-owned and import does not auto-send torrents",()=>{
 const flow=app.slice(app.indexOf("function showBTDiggDialog"),app.indexOf("async function search()"));
 assert.match(flow,/new URL\("https:\/\/btdig\.com\/"\)/);
 assert.match(flow,/BTDiggBridge\.bookmarklet\("copy"\)/);
 assert.doesNotMatch(flow,/sendMagnet\(/);
 assert.match(dialog,/Aceasta este o metodă manuală/);
});
