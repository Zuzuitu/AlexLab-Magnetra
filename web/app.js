"use strict";
const $=id=>document.getElementById(id);
const STORAGE={selected:"magnetra.providers.v1",bookmarks:"magnetra.bookmarks.v1",pairing:"magnetra.companion.v1"};
const preferred=["knaben","torrentscsv","nyaasi","internetarchive"];
const state={providers:[],selected:new Set(preferred),items:[],bookmarks:{},pairing:null,bookmarksMode:false,searching:false};
const api=async(path,options={})=>{
  const response=await fetch(path,{cache:"no-store",...options});
  let data;
  try{data=await response.json();}catch{throw Error("Server returned an invalid response");}
  if(!response.ok)throw Error(data.error||"Request failed ("+response.status+")");
  return data;
};
function load(key,fallback){
  try {const value=JSON.parse(localStorage.getItem(key)||"null");return value??fallback;}catch{return fallback;}
}
function save(key,value){localStorage.setItem(key,JSON.stringify(value));}
function el(tag,className,text){
 const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=String(text);return e;
}
let toastTimer;
function toast(message){
  clearTimeout(toastTimer);const t=$("toast");t.textContent=message;t.classList.add("show");
  toastTimer=setTimeout(()=>t.classList.remove("show"),3500);
}
function openDialog(id){$(id).showModal();}
function closeDialog(id){$(id).close();}
function updatePairChip(text,online=false){
 const chip=$("companionChip");chip.classList.toggle("online",online);
 $("companionStatus").textContent=text;
}
function updateBookmarkCount(){const count=$("bookmarkCount");if(count)count.textContent=String(Object.keys(state.bookmarks).length);}
function chooseProviders(){
 const stored=load(STORAGE.selected,null);
 if(Array.isArray(stored))state.selected=new Set(stored);
 const valid=new Set(state.providers.filter(x=>x.ported).map(x=>x.id));
 state.selected=new Set([...state.selected].filter(x=>valid.has(x)));
 if(!state.selected.size)state.selected=new Set(preferred.filter(x=>valid.has(x)));
 save(STORAGE.selected,[...state.selected]);
 updateProviderCount();
}
function updateProviderCount(){$("providerCount").textContent=String(state.selected.size)+"/"+state.providers.length;}
function renderProviders(){
 const grid=$("providerGrid");grid.replaceChildren();
 const ported=state.providers.filter(p=>p.ported).length;
 $("catalogSummary").textContent=ported+" ported · "+state.providers.length+" total upstream";
 for(const p of state.providers){
  const row=el("div","provider-row"+(p.ported?"":" missing"));
  const label=el("label");
  const input=document.createElement("input");
  input.type="checkbox";input.value=p.id;input.checked=state.selected.has(p.id);input.disabled=!p.ported;
  input.addEventListener("change",()=>{
    if(input.checked){
      if(state.selected.size>=15){input.checked=false;toast("Maximum 15 indexers per search.");return;}
      state.selected.add(p.id);
    }else state.selected.delete(p.id);
    save(STORAGE.selected,[...state.selected]);updateProviderCount();
  });
  const name=el("strong","",p.name);
  label.append(input,name);
  const marker=el("small","",p.ported?"READY":"PORT PENDING");
  row.append(label,marker);grid.append(row);
 }
}
function sortItems(items){
 const selected=$("sort").value;
 const sorted=[...items];
 const size=s=>{if(!s)return 0;const m=String(s).match(/^([\d.,]+)\s*(B|KB|MB|GB|TB|PB)/i);if(!m)return 0;return parseFloat(m[1].replace(",","."))*1024**["B","KB","MB","GB","TB","PB"].indexOf(m[2].toUpperCase());};
 if(selected==="seeders")sorted.sort((a,b)=>(b.seeders??-1)-(a.seeders??-1));
 else if(selected==="date")sorted.sort((a,b)=>Date.parse(b.date||0)-Date.parse(a.date||0));
 else if(selected==="size")sorted.sort((a,b)=>size(b.size)-size(a.size));
 else sorted.sort((a,b)=>a.name.localeCompare(b.name));
 return sorted;
}
function addAction(container,label,onClick,cls=""){
 const button=el("button","action "+cls,label);button.type="button";button.addEventListener("click",onClick);container.append(button);return button;
}
function downloadAction(container,label,url){
 if(!/^https:\/\//.test(url||""))return;
 const a=el("a","action",label);a.href=url;a.target="_blank";a.rel="noopener noreferrer";container.append(a);
}
async function copyMagnet(magnet) {
 try {await navigator.clipboard.writeText(magnet);toast("Magnet copied");}
 catch {
   const t=document.createElement("textarea");t.value=magnet;t.style.position="fixed";t.style.top="-999px";document.body.append(t);t.select();
   const ok=document.execCommand("copy");t.remove();toast(ok?"Magnet copied":"Copy failed");
 }
}
async function sendMagnet(item,button){
 if(!state.pairing?.deviceId||!state.pairing?.token){openDialog("settingsDialog");toast("Pair Flud Companion first.");return;}
 const original=button.textContent;
 button.disabled=true;button.textContent="Sending…";
 try{
   const body={...state.pairing,magnet:item.magnet,requestId:crypto.randomUUID()};
   const result=await api("/api/companion/magnet",{
     method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)
   });
   if(result.ok&&result.queued)toast("Magnet queued in Flud Companion.");
   else toast("Companion accepted magnet.");
 }catch(e){toast(e.message);button.title=e.message;}
 finally{button.disabled=false;button.textContent=original;}
}
function renderResults(){
 const root=$("results");root.replaceChildren();
 const items=state.bookmarksMode?Object.values(state.bookmarks):state.items;
 const sorted=sortItems(items);$("resultCount").textContent=sorted.length+" RESULTS";
 $("resultsTitle").textContent=state.bookmarksMode?"Saved bookmarks":"Search results";
 if(!sorted.length){
   if(state.bookmarksMode)$("notice").textContent="No bookmarks saved yet.";
   else if(!state.searching && state.items.length===0 && $("query").value.trim())$("notice").textContent="No results. Try another query or indexer.";
   return;
 }
 $("notice").textContent="";
 for(const item of sorted.slice(0,400)){
   const card=el("article","result");
   const body=el("div"),title=el("h3","result-title",item.name),info=el("div","result-info");
   info.append(el("span","tag",state.providers.find(p=>p.id===item.provider)?.name||item.provider));
   for(const field of [item.size, item.seeders!==null&&item.seeders!==undefined?item.seeders+" seeders":null,item.peers!==null&&item.peers!==undefined?item.peers+" peers":null,item.date?String(item.date).slice(0,10):null]){
     if(!field)continue;info.append(el("span","meta-dot","·"),el("span","",field));
   }
   body.append(title,info);
   const actions=el("div","result-actions");
   addAction(actions,"Send to Flud",function(){sendMagnet(item,this)},"send");
   addAction(actions,"Copy",()=>copyMagnet(item.magnet));
   const magnet=el("a","action","Magnet");magnet.href=item.magnet;magnet.rel="noopener noreferrer";magnet.title="Open in your installed torrent client";actions.append(magnet);
   if(item.torrentFile)downloadAction(actions,".torrent ↗",item.torrentFile);
   if(item.details)downloadAction(actions,"Details ↗",item.details);
   const saved=Boolean(state.bookmarks[item.id]);
   addAction(actions,saved?"★":"☆",()=>{
     if(state.bookmarks[item.id])delete state.bookmarks[item.id];else state.bookmarks[item.id]=item;
     save(STORAGE.bookmarks,state.bookmarks);updateBookmarkCount();renderResults();
   },saved?"saved":"");
   card.append(body,actions);root.append(card);
 }
}
async function search(){
 if(state.searching)return;
 const query=$("query").value.trim();
 if(query.length<2){toast("Enter at least two characters");return;}
 if(!state.selected.size){openDialog("providersDialog");toast("Select at least one working indexer.");return;}
 state.searching=true;state.bookmarksMode=false;state.items=[];
 $("searchButton").disabled=true;$("searchButton").textContent="Searching…";
 $("notice").textContent="Searching "+state.selected.size+" indexers…";$("providerErrors").replaceChildren();renderResults();
 try{
   const url=new URL("/api/search",location.origin);
   url.searchParams.set("q",query);url.searchParams.set("category",$("category").value);
   url.searchParams.set("providers",[...state.selected].join(","));
   const data=await api(url.pathname+url.search);
   state.items=data.results||[];
   const failed=(data.errors||[]).map(e=>(state.providers.find(p=>p.id===e.provider)?.name||e.provider)+": "+e.error);
   if(failed.length)$("providerErrors").textContent=failed.join(" · ");
   if(!state.items.length)$("notice").textContent=failed.length?"No results; some sources failed.":"No matching results in selected indexers.";
 }catch(e){$("notice").textContent=e.message;toast("Search failed: "+e.message);}
 finally{
   state.searching=false;$("searchButton").disabled=false;$("searchButton").textContent="Search →";renderResults();
   $("resultsTitle").scrollIntoView({block:"nearest",behavior:"smooth"});
 }
}
async function status(){
 if(!state.pairing){updatePairChip("Flud Companion · Not paired");return;}
 try{
   const data=await api("/api/companion/status",{
     method:"POST",headers:{"content-type":"application/json"},
     body:JSON.stringify(state.pairing)
   });
   const online=data.online===true;
   updatePairChip("Flud Companion · "+(online?"Online":"Offline"),online);
   $("pairStatus").textContent=online?"Shield online · Auto-start "+(data.autoStartReady?"ready":"not ready"):"Shield offline";
 }catch(e){updatePairChip("Flud Companion · Unavailable");$("pairStatus").textContent=e.message;}
}
function init(){
 state.bookmarks=load(STORAGE.bookmarks,{});
 state.pairing=load(STORAGE.pairing,null);
 if(state.pairing){
  $("companionDevice").value=state.pairing.deviceId||"";
  $("companionToken").value=state.pairing.token||"";
  $("companionAuto").checked=state.pairing.autoStart===true;
 }
 updateBookmarkCount();
 $("searchForm").addEventListener("submit",e=>{e.preventDefault();search();});
 $("sort").addEventListener("change",renderResults);
 $("settingsButton").addEventListener("click",()=>openDialog("settingsDialog"));
 $("companionChip").addEventListener("click",()=>openDialog("settingsDialog"));
 $("providersButton").addEventListener("click",()=>openDialog("providersDialog"));
 for(const button of document.querySelectorAll("[data-close]"))button.addEventListener("click",()=>closeDialog(button.dataset.close));
 $("viewBookmarks").addEventListener("click",()=>{
  state.bookmarksMode=!state.bookmarksMode;
  $("viewBookmarks").firstChild.textContent=state.bookmarksMode?"← Back to search ":"☆ Bookmarks ";
  renderResults();
 });
 $("selectWorking").addEventListener("click",()=>{
  state.selected=new Set(state.providers.filter(p=>p.ported).map(p=>p.id).slice(0,15));
  save(STORAGE.selected,[...state.selected]);renderProviders();updateProviderCount();
 });
 $("companionForm").addEventListener("submit",e=>{
  e.preventDefault();
  const deviceId=$("companionDevice").value.trim(),token=$("companionToken").value.trim();
  if(!/^[A-Za-z0-9_-]{16,128}$/.test(deviceId)||token.length<20){toast("Check Device ID and Remote token.");return;}
  state.pairing={deviceId,token,autoStart:$("companionAuto").checked};
  save(STORAGE.pairing,state.pairing);closeDialog("settingsDialog");toast("Companion paired in this browser.");status();
 });
 $("forgetCompanion").addEventListener("click",()=>{
   state.pairing=null;localStorage.removeItem(STORAGE.pairing);
   $("companionDevice").value="";$("companionToken").value="";$("companionAuto").checked=false;
   updatePairChip("Flud Companion · Not paired");toast("Pairing removed from this browser.");
 });
 api("/api/providers").then(({providers})=>{
  state.providers=providers;chooseProviders();renderProviders();
  $("notice").textContent="Ready. "+providers.filter(p=>p.ported).length+" indexers are ported; "+providers.length+" are inventoried.";
 }).catch(e=>$("notice").textContent="API unavailable: "+e.message);
 status();
 if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}
document.addEventListener("DOMContentLoaded",init);
