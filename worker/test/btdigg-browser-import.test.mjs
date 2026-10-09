import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const source=readFileSync(new URL("../../web/btdigg-bridge.js",import.meta.url),"utf8");
const app=readFileSync(new URL("../../web/app.js",import.meta.url),"utf8");
const hash="0123456789abcdef0123456789abcdef01234567";
const magnet="magnet:?xt=urn:btih:"+hash;
const detail="https://btdig.com/torrent/"+hash;
const makePayload=(rows,query="ubuntu")=>"#btdigg="+encodeURIComponent(JSON.stringify({
 v:1,query,results:rows
}));
const sample=(extra={})=>({name:"Ubuntu official ISO",magnet,details:detail,size:"3.1 GB",date:"2 days ago",...extra});
function bridge(){
 const box={URL,URLSearchParams,Set,JSON,decodeURIComponent,encodeURIComponent};
 box.globalThis=box;
 runInNewContext(source,box,{filename:"web/btdigg-bridge.js"});
 return box.BTDiggBridge;
}
test("import accepts genuine BTDigg-shaped browser results and de-duplicates infohashes",()=>{
 const b=bridge();
 const parsed=b.parsePayload(makePayload([sample(),sample({name:"Duplicate"})]));
 assert.equal(parsed.query,"ubuntu");
 assert.equal(parsed.results.length,1);
 assert.equal(parsed.results[0].provider,"btdigg");
 assert.equal(parsed.results[0].id,"btdigg:browser:"+hash);
 assert.equal(parsed.results[0].magnet,magnet);
 assert.equal(parsed.results[0].details,detail);
 assert.equal(parsed.results[0].importedFromBrowser,true);
});
test("no unknown origins, invalid torrents, spoofed magnetic links or malformed structures",()=>{
 const b=bridge();
 for(const change of [
  {details:"https://evil.example/torrent/"+hash},
  {details:"https://btdig.com.evil.example/torrent/"+hash},
  {details:"https://btdig.com@evil.example/torrent/"+hash},
  {details:"http://btdig.com/torrent/"+hash},
  {details:"https://btdig.com.tld/torrent/"+hash},
  {details:"https://btdig.com/search?q=ubuntu"},
  {magnet:"javascript:alert(1)"},
  {magnet:"magnet:?xt=urn:btih:invalid"},
  {name:""}
 ]) assert.throws(()=>b.parsePayload(makePayload([sample(change)])));
 assert.throws(()=>b.parsePayload("#btdigg=%7B"));
 assert.throws(()=>b.parsePayload(makePayload([sample()],"a".repeat(181))));
 assert.throws(()=>b.parsePayload(makePayload(Array(26).fill(sample()))));
 assert.throws(()=>b.parsePayload("#btdigg="+"A".repeat(50001)));
 assert.equal(b.parsePayload("#anything=else"),null);
});
function fixtureRow(name="Ubuntu official ISO"){
 const title={textContent:name,getAttribute(key){return key==="href"?"/torrent/"+hash:null;}};
 const link={getAttribute(key){return key==="href"?magnet:null;}};
 return {querySelector(selector){
  if(selector==="div.torrent_name a")return title;
  if(selector==='div.torrent_magnet a[href^="magnet:?"]')return link;
  if(selector==="span.torrent_size")return {textContent:"3.1 GB"};
  if(selector==="span.torrent_age")return {textContent:"2 days ago"};
  return null;
 }};
}
function runBookmarklet(origin,rows){
 const b=bridge();let destination="",alerted="";
 assert.equal(b.bookmarklet().includes("\n"),false,"Safari bookmarklet URL should be single-line");
 const location={protocol:"https:",hostname:origin,origin:"https://"+origin,
  pathname:"/search",search:"?q=ubuntu",assign(url){destination=url;}};
 const box={location,URL,URLSearchParams,document:{
  querySelectorAll(selector){
   assert.equal(selector,"div.one_result");
   return rows;
  }
 },alert(message){alerted=message;},encodeURIComponent,JSON};
 runInNewContext(b.bookmarklet().slice("javascript:".length),box,{filename:"BTDigg Safari bookmarklet"});
 return {destination,alerted};
}
test("bookmarklet extracts actual displayed BTDigg page into fragment (no network or credentials)",()=>{
 const done=runBookmarklet("btdig.com",[fixtureRow(),fixtureRow("Another name")]);
 assert.equal(done.alerted,"");
 assert.ok(done.destination.startsWith("https://index.alexlab.media/#btdigg="));
 const parsed=bridge().parsePayload(new URL(done.destination).hash);
 assert.equal(parsed.query,"ubuntu");
 assert.equal(parsed.results.length,1,"hashes are deduplicated at import boundary");
 assert.equal(parsed.results[0].name,"Ubuntu official ISO");
});
test("bookmarklet rejects off-origin execution and empty results instead of inventing records",()=>{
 const wrong=runBookmarklet("evil.example",[fixtureRow()]);
 assert.equal(wrong.destination,"");
 assert.match(wrong.alerted,/btdig\.com\/search/);
 const empty=runBookmarklet("btdig.com",[]);
 assert.equal(empty.destination,"");
 assert.match(empty.alerted,/No readable BTDigg magnets/);
});
test("Magnetra consumes browser import locally and immediately scrubs the fragment",()=>{
 const BTDiggBridge=bridge();
 const location={origin:"https://index.alexlab.media",pathname:"/",search:"",hash:makePayload([sample()])};
 const elements=new Map();
 function element(id){
  if(!elements.has(id))elements.set(id,{
   value:"",textContent:"",scrollIntoView(){},replaceChildren(){},classList:{add(){},remove(){},toggle(){}}
  });
  return elements.get(id);
 }
 let scrubbed=false;
 const box={document:{getElementById:element,addEventListener(){}},location,
   history:{replaceState(_,__,path){scrubbed=true;assert.equal(path,"/");location.hash="";}},
   BTDiggBridge,URL,URLSearchParams,Set,Map,Date,Promise,AbortController,
   setTimeout,clearTimeout,console};
 box.globalThis=box;
 runInNewContext(app+"\nrenderResults=()=>{};globalThis.debug={importBTDiggBrowserResults,state};",box);
 box.debug.importBTDiggBrowserResults();
 assert.equal(scrubbed,true);
 assert.equal(location.hash,"");
 assert.equal(box.debug.state.items.length,1);
 assert.equal(box.debug.state.items[0].provider,"btdigg");
 assert.equal(element("query").value,"ubuntu");
 assert.match(box.debug.state.importNote,/not independently server-verified/);
});

test("Safari copy-mode bookmarklet exports visible BTDigg results without redirecting",async()=>{
 const b=bridge();
 const copied=[],alerts=[];
 let opened=false;
 const location={protocol:"https:",hostname:"btdig.com",origin:"https://btdig.com",
  pathname:"/search",search:"?q=ubuntu",assign(){opened=true;}};
 const box={location,URL,URLSearchParams,encodeURIComponent,JSON,
  document:{querySelectorAll(){return [fixtureRow()];}},
  navigator:{clipboard:{writeText:async text=>{copied.push(text);}}},
  alert:msg=>alerts.push(msg),
  window:{prompt(){throw Error("unexpected prompt");}}};
 const url=b.bookmarklet("copy");
 assert.ok(url.startsWith("javascript:"));
 assert.equal(url.includes("\n"),false,"bookmarklet URL must remain single-line");
 runInNewContext(url.slice("javascript:".length),box);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(opened,false);
 assert.equal(copied.length,1);
 assert.ok(copied[0].startsWith("BTDIGG_IMPORT:"));
 const data=b.parseClipboard(copied[0]);
 assert.equal(data.results.length,1);
 assert.equal(data.results[0].provider,"btdigg");
 assert.match(alerts[0],/copied/i);
});
test("clipboard import rejects missing marker and spoofed origins",()=>{
 const b=bridge();
 const valid="BTDIGG_IMPORT:"+makePayload([sample()]).slice("#btdigg=".length);
 assert.equal(b.parseClipboard(valid).results[0].magnet,magnet);
 for(const invalid of [
  "", "magnet:?xt=urn:btih:"+hash,"https://btdig.com/",
  "BTDIGG_IMPORT:%7B", "BTDIGG_IMPORT:"+"A".repeat(50001),
  "BTDIGG_IMPORT:"+makePayload([sample({details:"https://evil.example/torrent/"+hash})]).slice("#btdigg=".length)
 ])assert.throws(()=>b.parseClipboard(invalid));
});
test("PWA clipboard import preserves existing Flud pairing and puts BTDigg rows in result state",()=>{
 const b=bridge();
 const elements=new Map();
 const element=id=>{
  if(!elements.has(id))elements.set(id,{value:"",textContent:"",replaceChildren(){},
   classList:{add(){},remove(){},toggle(){}}});
  return elements.get(id);
 };
 const box={
  document:{getElementById:element,addEventListener(){}},
  BTDiggBridge:b,URL,URLSearchParams,Set,Map,Date,Promise,AbortController,setTimeout,clearTimeout
 };
 box.globalThis=box;
 runInNewContext(app+"\nrenderResults=()=>{};globalThis.debug={importBTDiggFromClipboard,state};",box);
 const pairing={deviceId:"D".repeat(20),token:"T".repeat(25),autoStart:false};
 box.debug.state.pairing=pairing;
 const exported="BTDIGG_IMPORT:"+makePayload([sample()]).slice("#btdigg=".length);
 box.debug.importBTDiggFromClipboard(exported);
 assert.equal(box.debug.state.pairing,pairing);
 assert.equal(box.debug.state.items[0].provider,"btdigg");
 assert.equal(box.debug.state.items[0].magnet,magnet);
 assert.equal(element("query").value,"ubuntu");
 assert.match(box.debug.state.importNote,/not independently server-verified/);
});
