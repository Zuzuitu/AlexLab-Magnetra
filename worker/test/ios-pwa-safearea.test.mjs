import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const css=readFileSync(new URL("../../web/styles.css",import.meta.url),"utf8");
const html=readFileSync(new URL("../../web/index.html",import.meta.url),"utf8");
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const sw=readFileSync(new URL("../../web/sw.js",import.meta.url),"utf8");

test("iOS installed PWA reserves status-bar safe area without shifting ordinary Safari layout",()=>{
  assert.match(html,/name="viewport"[^>]*viewport-fit=cover/);
  assert.match(html,/name="apple-mobile-web-app-status-bar-style" content="black-translucent"/);
  assert.match(css,/@media\s*\(max-width:760px\)\s*and\s*\(display-mode:standalone\)\s*\{/);
  assert.match(css,/\.site-shell\{padding-top:max\(60px,env\(safe-area-inset-top,0px\)\)\}/);
  assert.match(css,/html\.ios-standalone \.site-shell\{padding-top:max\(60px,env\(safe-area-inset-top,0px\)\)\}/);
  assert.match(app,/navigator\.standalone===true/);
  assert.match(app,/document\.documentElement\.classList\.add\("ios-standalone"\)/);
});

test("standalone header settings and language controls preserve tappable minimum sizes",()=>{
  assert.match(html,/id="settingsButton"[^>]*aria-label="Configurează Flud Companion"/);
  assert.match(html,/id="languageSelect"[^>]*aria-label="Limbă"/);
  assert.match(css,/#settingsButton\{width:44px;height:44px;min-width:44px;min-height:44px\}/);
  assert.match(css,/#languageSelect\{min-height:44px\}/);
  assert.match(app,/\$\("settingsButton"\)\.addEventListener\("click",\(\)=>openDialog\("settingsDialog"\)\)/);
});

test("installed service worker refreshes the safe-area stylesheet through a new cache",()=>{
  assert.match(sw,/const CACHE="alexlab-magnetra-v8"/);
  assert.match(sw,/const FRESH_ASSETS=new Set\(\[[^\]]*"\/styles\.css"/);
  assert.match(sw,/fetch\(event\.request,\{cache:"no-store"\}\)/);
});
