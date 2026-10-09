// User-initiated BTDigg browser import. This does NOT bypass BTDigg's rate limits
// and does NOT replace the direct BTDigg provider or claim server-verification.
(function(){
"use strict";
const PREFIX="#btdigg=";
const ORIGIN="https://index.alexlab.media";
const INFOHASH=/^(?:[0-9a-f]{40}|[a-z2-7]{32})$/i;
function checkedMagnet(value){
 if(typeof value!=="string"||value.length>12000||!value.startsWith("magnet:?"))return null;
 try{
  const parsed=new URL(value);
  if(parsed.protocol!=="magnet:")return null;
  const xt=[...parsed.searchParams.entries()].find(([key,val])=>key.toLowerCase()==="xt"&&/^urn:btih:/i.test(val));
  if(!xt)return null;
  const hash=xt[1].slice(9);
  if(!INFOHASH.test(hash))return null;
  return {hash:hash.toLowerCase(),magnet:value};
 }catch{return null;}
}
function fromBTDigg(url){
 try{
  const u=new URL(url);
  return u.protocol==="https:"&&(u.hostname==="btdig.com"||u.hostname==="www.btdig.com")&&
   u.username===""&&u.password===""&&u.port===""&&u.pathname.startsWith("/torrent/")&&u.hash===""?
   u.toString():null;
 }catch{return null;}
}
function parsePayload(hash){
 if(typeof hash!=="string"||!hash.startsWith(PREFIX))return null;
 if(hash.length>50000)throw Error("BTDigg import link is too large.");
 let payload;
 try{payload=JSON.parse(decodeURIComponent(hash.slice(PREFIX.length)));}catch{throw Error("Invalid BTDigg browser import link.");}
 if(!payload||payload.v!==1||typeof payload.query!=="string"||payload.query.length>180||
    !Array.isArray(payload.results)||payload.results.length>25)
  throw Error("BTDigg import format is invalid.");
 const results=[],seen=new Set();
 for(const row of payload.results){
  if(!row||typeof row.name!=="string"||row.name.length>240||!row.name.trim())continue;
  const valid=checkedMagnet(row.magnet);
  if(!valid||seen.has(valid.hash))continue;
  if(row.details!=null&&!fromBTDigg(row.details))continue;
  if(row.size!=null&&(typeof row.size!=="string"||row.size.length>60))continue;
  if(row.date!=null&&(typeof row.date!=="string"||row.date.length>80))continue;
  seen.add(valid.hash);
  results.push({
   id:"btdigg:browser:"+valid.hash,provider:"btdigg",
   name:row.name.trim(),magnet:valid.magnet,size:row.size||"",
   date:row.date||null,seeders:null,peers:null,
   details:row.details||null,category:"all",importedFromBrowser:true
  });
 }
 if(!results.length)throw Error("BTDigg import contains no valid result magnets.");
 return {query:payload.query.trim(),results};
}
// Self-contained on purpose: this function's source is inserted into a Safari/Firefox
// bookmarklet and runs ONLY after the user explicitly invokes it on btdig.com.
// No cross-origin reads, cookies, credentials, external scripts or hidden requests.
function collectPage(){
 if(location.protocol!=="https:"||
    !(location.hostname==="btdig.com"||location.hostname==="www.btdig.com")||
    !/^\/search\/?$/.test(location.pathname)){
  alert("Open the BTDigg search results page (btdig.com/search) first.");return;
 }
 const items=[];
 for(const row of [...document.querySelectorAll("div.one_result")].slice(0,25)){
  const title=row.querySelector("div.torrent_name a");
  const magnet=row.querySelector('div.torrent_magnet a[href^="magnet:?"]');
  if(!title||!magnet)continue;
  const name=(title.textContent||"").trim().replace(/\s+/g," ");
  const href=magnet.getAttribute("href")||"";
  if(!name||name.length>240||!href.startsWith("magnet:?")||href.length>12000)continue;
  let hash=null;
  try{
   const params=new URL(href).searchParams;
   for(const [key,value] of params){
    if(key.toLowerCase()==="xt"&&/^urn:btih:/i.test(value)){
     const match=value.slice(9);
     if(/^(?:[0-9a-f]{40}|[a-z2-7]{32})$/i.test(match)){hash=match;break;}
    }
   }
  }catch{}
  if(!hash)continue;
  const detailHref=title.getAttribute("href");
  let details=null;
  try{
   if(detailHref){
    const u=new URL(detailHref,location.origin);
    if(u.protocol==="https:"&&(u.hostname==="btdig.com"||u.hostname==="www.btdig.com")&&
       u.pathname.startsWith("/torrent/")&&!u.hash&&!u.username&&!u.password&&!u.port)
     details=u.toString();
   }
  }catch{}
  const size=(row.querySelector("span.torrent_size")?.textContent||"").trim().slice(0,60);
  const date=(row.querySelector("span.torrent_age")?.textContent||"").trim().slice(0,80);
  items.push({name,magnet:href,details,size,date});
 }
 if(!items.length){alert("No readable BTDigg magnets were found on this page. The site's layout may have changed.");return;}
 const payload={v:1,query:(new URLSearchParams(location.search).get("q")||"").slice(0,180),results:items};
 let encoded=encodeURIComponent(JSON.stringify(payload));
 while(encoded.length>24000&&payload.results.length>1){
  payload.results.pop();encoded=encodeURIComponent(JSON.stringify(payload));
 }
 if(encoded.length>24000){alert("A BTDigg result was too large to import safely.");return;}
 location.assign("https://index.alexlab.media/#btdigg="+encoded);
}
function bookmarklet(){return "javascript:("+collectPage.toString()+")()";}
globalThis.BTDiggBridge=Object.freeze({parsePayload,checkedMagnet,bookmarklet,origin:ORIGIN});
})();
