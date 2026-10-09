"use strict";
const $=id=>document.getElementById(id);
const STORAGE={selected:"magnetra.providers.v1",bookmarks:"magnetra.bookmarks.v1",pairing:"magnetra.companion.v1"};
const preferred=["knaben","torrentscsv","thepiratebay","internetarchive"];
const state={providers:[],audit:null,selected:new Set(preferred),items:[],bookmarks:{},pairing:null,bookmarksMode:false,searching:false,searchAbort:null};
const recentCompanionCommands=new Map();
const activeCompanionMagnets=new Set();
const activeCompanionItems=new Set();
const companionLabels=new Map();
// Remote deduplicates requestId for 120 seconds. Reuse that ID on rapid repeat taps.
function magnetIdentity(magnet,deviceId){
 const params=new URLSearchParams(magnet.slice(magnet.indexOf("?")+1));
 const xt=[...params.entries()].find(([key,value])=>key.toLowerCase()==="xt"&&/^urn:btih:/i.test(value))?.[1];
 return deviceId+"|"+(xt?xt.toLowerCase():magnet.trim());
}
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
 const audited=state.providers.filter(p=>p.lastAudit?.state==="results").length;
 const day=state.audit?.observedAt?new Date(state.audit.observedAt).toLocaleDateString():"unknown date";
 $("catalogSummary").textContent=ported+" adapters · "+audited+" returned results for '"+(state.audit?.query||"test")+"' on "+day+" (not live status)";
 for(const p of state.providers){
  const row=el("div","provider-row"+(p.ported?"":" missing"));
  const label=el("label");
  const input=document.createElement("input");
  input.type="checkbox";input.value=p.id;input.checked=state.selected.has(p.id);input.disabled=!p.ported;
  input.addEventListener("change",()=>{
    if(input.checked){
      if(state.selected.size>=state.providers.length){input.checked=false;toast("All available indexers are already selected.");return;}
      state.selected.add(p.id);
    }else state.selected.delete(p.id);
    save(STORAGE.selected,[...state.selected]);updateProviderCount();
  });
  const name=el("strong","",p.name);
  label.append(input,name);
  const audit=p.lastAudit?.state;
  const message=audit==="results"?"RESULTS IN TEST":audit==="empty-unverified"?"0 IN TEST":audit==="error"?"ERROR IN TEST":"NOT AUDITED";
  const marker=el("small","audit-"+(audit||"unknown"),p.ported?message:"PORT PENDING");
  if(audit)marker.title="Historical "+(state.audit?.query||"")+
    " query on "+(state.audit?.observedAt||"unknown date")+
    (p.lastAudit?.code?"; "+p.lastAudit.code:"")+
    (p.lastAudit?.count!=null?"; "+p.lastAudit.count+" results":"");
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
async function ensureMagnet(item){
 if(item.magnet?.startsWith("magnet:?"))return item.magnet;
 const source=item.magnetSource||item.details;
 if(!source)throw Error("Provider has no supported magnet or details link.");
 const res=await api("/api/resolve",{
  method:"POST",headers:{"content-type":"application/json"},
  body:JSON.stringify({provider:item.provider,details:source})
 });
 if(!res.magnet?.startsWith("magnet:?"))throw Error("Provider did not return a valid magnet.");
 item.magnet=res.magnet;
 if(state.bookmarks[item.id]){state.bookmarks[item.id]=item;save(STORAGE.bookmarks,state.bookmarks);}
 return item.magnet;
}
async function verifyCompanionReceipt(commandId) {
 if(!commandId||!state.pairing)return "Queued ✓";
 // Relay acceptance, Shield acknowledgement, and torrent download are distinct states.
 for(let attempt=0;attempt<4;attempt++){
  await new Promise(resolve=>setTimeout(resolve,2000));
  try{
   const data=await api("/api/companion/status",{
    method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(state.pairing)
   });
   if(data.lastResult?.id===commandId){
    if(data.lastResult.ok){toast("Shield acknowledged the magnet command.");return "Shield ✓";}
    toast("Shield rejected magnet: "+(data.lastResult.message||"Unknown error"));
    return "Retry send";
   }
  }catch{return "Queued ✓";}
 }
 toast("Queued; waiting for Shield confirmation.");
 return "Queued ✓";
}
async function sendMagnet(item,button){
 if(!state.pairing?.deviceId||!state.pairing?.token){openDialog("settingsDialog");toast("Pair Flud Companion first.");return;}
 const itemKey=item.id||item.magnet;
 if(activeCompanionItems.has(itemKey)){toast("This magnet is already being sent.");return;}
 const original=button.textContent;
 let activeKey=null;
 activeCompanionItems.add(itemKey);
 if(item.id)companionLabels.set(itemKey,"Sending…");
 button.disabled=true;button.textContent="Sending…";
 try{
   const magnet=await ensureMagnet(item);
   const key=magnetIdentity(magnet,state.pairing.deviceId);
   if(activeCompanionMagnets.has(key)){
     toast("This magnet is already being sent.");return;
   }
   activeCompanionMagnets.add(key);activeKey=key;
   const previous=recentCompanionCommands.get(key);
   const now=Date.now();
   const requestId=previous&&now-previous.at<110000?previous.requestId:crypto.randomUUID();
   recentCompanionCommands.set(key,{requestId,at:now});
   const body={...state.pairing,magnet,requestId};
   const result=await api("/api/companion/magnet",{
     method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)
   });
   if(!result.ok||result.queued!==true)throw Error("Relay did not confirm a queued command.");
   if(typeof result.id!=="string"||!result.id)throw Error("Relay returned no command receipt ID.");
   toast(result.duplicate?"Already queued in Companion.":"Magnet queued; awaiting Shield acknowledgement.");
   button.textContent="Queued ✓";
   if(item.id)companionLabels.set(itemKey,"Queued ✓");
   const label=await verifyCompanionReceipt(result.id);
   button.textContent=label;
   if(item.id)companionLabels.set(itemKey,label);
 }catch(e){
   toast(e.message);button.title=e.message;
   if(item.id)companionLabels.set(itemKey,"Retry send");
 }finally{
   if(activeKey)activeCompanionMagnets.delete(activeKey);
   activeCompanionItems.delete(itemKey);
   button.disabled=false;
   if(item.id)renderResults();
   else button.textContent=original;
 }
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
 $("notice").textContent=state.importNote&&!state.bookmarksMode&&sorted.some(x=>x.importedFromBrowser)?state.importNote:"";
 for(const item of sorted.slice(0,400)){
   const card=el("article","result");
   const body=el("div"),title=el("h3","result-title",item.name),info=el("div","result-info");
   info.append(el("span","tag",item.importedFromBrowser?"BTDigg · browser import":state.providers.find(p=>p.id===item.provider)?.name||item.provider));
   for(const field of [item.size, item.seeders!==null&&item.seeders!==undefined?item.seeders+" seeders":null,item.peers!==null&&item.peers!==undefined?item.peers+" peers":null,item.date?String(item.date).slice(0,10):null]){
     if(!field)continue;info.append(el("span","meta-dot","·"),el("span","",field));
   }
   body.append(title,info);
   const actions=el("div","result-actions");
   const sendButton=addAction(actions,companionLabels.get(item.id)||"Send to Flud",function(){sendMagnet(item,this)},"send");
   sendButton.disabled=activeCompanionItems.has(item.id);
   addAction(actions,"Copy",async()=>{try{await copyMagnet(await ensureMagnet(item));}catch(e){toast(e.message);}});
   addAction(actions,"Share",async()=>{
     try{
       const magnet=await ensureMagnet(item);
       if(navigator.share){
         try{await navigator.share({title:item.name,text:magnet});}
         catch(e){if(e?.name!=="AbortError")await copyMagnet(magnet);}
       }else await copyMagnet(magnet);
     }catch(e){toast(e.message);}
   });
   if(item.magnet){
     const magnet=el("a","action","Magnet");magnet.href=item.magnet;magnet.rel="noopener noreferrer";magnet.title="Open in your installed torrent client";actions.append(magnet);
   }else{
     addAction(actions,"Resolve",async function(){
       const old=this.textContent;this.disabled=true;this.textContent="Resolving…";
       try{await ensureMagnet(item);toast("Magnet resolved.");renderResults();}
       catch(e){toast(e.message);this.textContent=old;this.disabled=false;}
     });
   }
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
function renderProviderErrors(failures){
 const root=$("providerErrors");root.replaceChildren();
 if(!failures.length)return;
 const details=el("details","failed-sources");
 if(failures.length<=2)details.open=true;
 const summary=el("summary","failed-sources-title",failures.length+" indexer"+(failures.length===1?"":"s")+" unavailable · See alternatives");
 details.append(summary);
 const message=el("p","failed-sources-note",
  "Some external sites restrict searches from Cloudflare. Magnetra cannot bypass their verification. You can open a source directly or search independently through other indexers.");
 details.append(message);
 for(const failure of failures){
  const entry=el("div","source-failure");
  const line=el("div","source-failure-content");
  const provider=state.providers.find(p=>p.id===failure.provider);
  line.append(el("strong","",provider?.name||failure.provider));
  const message=failure.message||failure.error||"Provider unavailable";
  const why=el("span","",message);
  if(failure.error)why.title=failure.error;
  line.append(why);entry.append(line);
  const link=failure.openUrl || provider?.url;
  if(/^https:\/\//.test(link||"")){
   const a=el("a","source-open",failure.openUrl?"Open source search ↗":"Visit source ↗");
   a.href=link;a.target="_blank";a.rel="noopener noreferrer";
   entry.append(a);
  }
  if(failure.provider==="btdigg"){
    const imported=el("button","source-open","BTDigg: ghid în 3 pași ↗");
    imported.type="button";
    imported.addEventListener("click",showBTDiggDialog);
    entry.append(imported);
  }
  details.append(entry);
 }
 const alternatives=el("button","source-alt","Search with available indexers →");
 alternatives.type="button";
 alternatives.addEventListener("click",()=>{
  const ids=["knaben","torrentscsv","thepiratebay","internetarchive"].filter(id=>state.providers.some(p=>p.id===id&&p.ported));
  if(!ids.length){toast("No alternative indexers are available.");return;}
  state.selected=new Set(ids);
  save(STORAGE.selected,ids);updateProviderCount();renderProviders();
  if(state.searching){
    state.pendingAlternativeSearch=true;
    state.searchAbort?.abort();
    toast("Cancelling the current search and starting alternatives.");
  }else search();
 });
 details.append(alternatives);
 root.append(details);
}
function showBTDiggDialog(){
 const q=$("query").value.trim();
 const url=new URL("https://btdig.com/");
 if(q)url.pathname="/search",url.searchParams.set("q",q);
 $("btdiggOpenSearch").href=url.toString();
 $("btdiggBookmarkletLink").href=BTDiggBridge.bookmarklet();
 $("btdiggClipboardBookmarkletLink").href=BTDiggBridge.bookmarklet("copy");
 openDialog("btdiggDialog");
}
function applyBTDiggImport(imported){
 if(!imported?.results?.length)throw Error("No BTDigg results were imported.");
 state.items=imported.results;
 state.bookmarksMode=false;
 if(imported.query)$("query").value=imported.query;
 state.importNote="Imported "+imported.results.length+" BTDigg result(s) from your browser; not independently server-verified.";
 renderResults();
}
function importBTDiggFromClipboard(text){
 if(!globalThis.BTDiggBridge)throw Error("BTDigg importer script is unavailable.");
 applyBTDiggImport(BTDiggBridge.parseClipboard(text.trim()));
}
function importBTDiggBrowserResults(){
 if(!location.hash.startsWith("#btdigg="))return;
 const fragment=location.hash;
 // Never persist magnet-bearing fragment URLs in navigation history.
 try{history.replaceState(null,"",location.pathname+location.search);}
 catch{
  state.importNote="Browser import requires a history-safe context.";
  $("notice").textContent=state.importNote;
  return;
 }
 try{
  if(!globalThis.BTDiggBridge)throw Error("BTDigg importer script is unavailable.");
  applyBTDiggImport(BTDiggBridge.parsePayload(fragment));
 }catch(e){
  state.importNote=e.message||"Invalid BTDigg import.";
  $("notice").textContent=state.importNote;
 }
}
async function search(){
 if(state.searching){
  state.searchAbort?.abort();
  $("notice").textContent="Cancelling search; keeping results already found…";
  return;
 }
 const query=$("query").value.trim();
 if(query.length<2){toast("Enter at least two characters");return;}
 if(!state.selected.size){openDialog("providersDialog");toast("Select at least one indexer.");return;}
 const ids=[...state.selected],category=$("category").value,failures=[];
 const controller=new AbortController();
 state.searchAbort=controller;state.searching=true;state.bookmarksMode=false;state.items=[];state.importNote=null;
 $("searchButton").disabled=false;$("searchButton").textContent="Cancel search ×";
 $("notice").textContent="Searching "+ids.length+" indexers…";$("providerErrors").replaceChildren();renderResults();
 let completed=0,next=0;
 try{
  // Sliding pool: a slow provider never blocks the next queued provider.
  await Promise.all(Array.from({length:Math.min(3,ids.length)},async()=>{
   while(!controller.signal.aborted){
    const index=next++;
    if(index>=ids.length)return;
    const id=ids[index];
    const url=new URL("/api/search",location.origin);
    url.searchParams.set("q",query);url.searchParams.set("category",category);
    url.searchParams.set("providers",id);
    try{
     const data=await api(url.pathname+url.search,{signal:controller.signal});
     if(controller.signal.aborted)return;
     state.items.push(...(data.results||[]));
     for(const e of data.errors||[])failures.push(e);
    }catch(e){
     if(controller.signal.aborted)return;
     failures.push({provider:id,error:e.message,message:"Magnetra could not reach this provider through the API."});
    }
    if(controller.signal.aborted)return;
    completed++;
    renderResults();
    $("notice").textContent="Searched "+completed+"/"+ids.length+" indexers · "+state.items.length+" results found.";
    renderProviderErrors(failures);
   }
  }));
  if(!controller.signal.aborted){
   if(!state.items.length)$("notice").textContent=failures.length?"No results; some indexers failed.":"No matching results in selected indexers.";
   else $("notice").textContent="";
  }
 }finally{
  const cancelled=controller.signal.aborted;
  state.searchAbort=null;state.searching=false;
  $("searchButton").disabled=false;$("searchButton").textContent="Search →";
  renderResults();
  if(state.pendingAlternativeSearch){
   state.pendingAlternativeSearch=false;
   search();
   return;
  }
  if(cancelled)$("notice").textContent="Search cancelled. Results already found are preserved.";
  else $("resultsTitle").scrollIntoView({block:"nearest",behavior:"smooth"});
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
   return online;
 }catch(e){updatePairChip("Flud Companion · Unavailable");$("pairStatus").textContent=e.message;return false;}
}
function init(){
 importBTDiggBrowserResults();
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
 $("pasteMagnetButton").addEventListener("click",async function(){
  if(!state.pairing){openDialog("settingsDialog");toast("Pair Flud Companion first.");return;}
  try{
    const copied=(await navigator.clipboard.readText()).trim();
    if(copied.startsWith("magnet:?") && copied.length<=12000){
      await sendMagnet({magnet:copied},this);
      return;
    }
  }catch{ /* Clipboard API may be unavailable on iOS standalone PWA. */ }
  openDialog("manualMagnetDialog");
  $("manualMagnetInput").focus();
 });
 $("manualMagnetForm").addEventListener("submit",e=>{
  e.preventDefault();
  const magnet=$("manualMagnetInput").value.trim();
  if(!magnet.startsWith("magnet:?")||magnet.length>12000){
    toast("Paste a valid magnet link.");return;
  }
  closeDialog("manualMagnetDialog");
  sendMagnet({magnet},$("pasteMagnetButton"));
 });

 $("providersButton").addEventListener("click",()=>openDialog("providersDialog"));
 $("btdiggButton").addEventListener("click",showBTDiggDialog);
 async function copyBTDiggCode(mode){
  const status=$("btdiggStepStatus");
  try{
   if(!globalThis.BTDiggBridge)throw Error("Codul BTDigg nu este disponibil.");
   await navigator.clipboard.writeText(BTDiggBridge.bookmarklet(mode));
   status.textContent="✓ Cod copiat! În Safari creează bookmarkul și lipește codul la «Adresă».";
   toast("Codul Safari a fost copiat.");
  }catch{
   status.textContent="Copierea nu a reușit. Verifică permisiunea pentru clipboard și încearcă din nou.";
  }
 }
 $("copyBTDiggBookmarklet").addEventListener("click",()=>copyBTDiggCode("open"));
 $("copyBTDiggClipboardBookmarklet").addEventListener("click",()=>copyBTDiggCode("copy"));
 $("btdiggImportFromClipboard").addEventListener("click",async()=>{
  try{
   const text=await navigator.clipboard.readText();
   importBTDiggFromClipboard(text);
   $("btdiggPasteInput").value="";
   closeDialog("btdiggDialog");
   toast("Rezultatele BTDigg au fost importate.");
  }catch(e){
   const reason=String(e?.message||"");
   const tip=reason.includes("Clipboard does not contain")
    ?"Clipboardul nu conține rezultate BTDigg. Execută bookmarkul din pasul 2, apoi revino aici."
    :"Nu am putut citi rezultatele. Poți lipi codul manual în secțiunea de ajutor.";
   toast(tip);
   $("btdiggMore").open=true;
  }
 });
 $("btdiggImportManual").addEventListener("click",()=>{
  try{
   importBTDiggFromClipboard($("btdiggPasteInput").value);
   $("btdiggPasteInput").value="";
   closeDialog("btdiggDialog");
   toast("Rezultatele BTDigg au fost importate.");
  }catch{toast("Cod invalid. Copiază rezultatele din Safari înainte de import.");}
 });
 for(const button of document.querySelectorAll("[data-close]"))button.addEventListener("click",()=>closeDialog(button.dataset.close));
 $("viewBookmarks").addEventListener("click",()=>{
  state.bookmarksMode=!state.bookmarksMode;
  $("viewBookmarks").firstChild.textContent=state.bookmarksMode?"← Back to search ":"☆ Bookmarks ";
  renderResults();
 });
 $("selectWorking").addEventListener("click",()=>{
  const ids=state.providers.filter(p=>p.ported&&p.lastAudit?.state==="results").map(p=>p.id);
  if(!ids.length){toast("No tested sources with results in the saved audit.");return;}
  state.selected=new Set(ids);
  save(STORAGE.selected,ids);renderProviders();updateProviderCount();
  toast("Selected "+ids.length+" sources with results in the last audit (not guaranteed online).");
 });
 $("selectAllProviders").addEventListener("click",()=>{
  const ids=state.providers.filter(p=>p.ported).map(p=>p.id);
  state.selected=new Set(ids);
  save(STORAGE.selected,ids);renderProviders();updateProviderCount();
  toast("Selected all "+ids.length+" indexers, including sources that may fail.");
 });
 $("importPairing").addEventListener("click",()=>{
  try{
   const u=new URL($("pairLink").value.trim());
   if(u.origin!=="https://flud-remote.alexlab.media")throw Error("Only the approved Flud Companion relay is supported.");
   const params=new URLSearchParams(u.hash.replace(/^#/,""));
   const device=params.get("device")||"",token=params.get("token")||"";
   if(!/^[A-Za-z0-9_-]{16,128}$/.test(device)||token.length<20)throw Error("Remote QR link has no valid pairing credentials.");
   $("companionDevice").value=device;$("companionToken").value=token;
   $("pairLink").value="";
   toast("QR pairing imported. Tap Save pairing.");
  }catch(e){toast(e.message||"Invalid Remote QR URL");}
 });
 $("companionForm").addEventListener("submit",e=>{
  e.preventDefault();
  const deviceId=$("companionDevice").value.trim(),token=$("companionToken").value.trim();
  if(!/^[A-Za-z0-9_-]{16,128}$/.test(deviceId)||token.length<20){toast("Check Device ID and Remote token.");return;}
  state.pairing={deviceId,token,autoStart:$("companionAuto").checked};
  save(STORAGE.pairing,state.pairing);closeDialog("settingsDialog");toast("Companion paired in this browser.");status();
 });
 $("checkCompanion").addEventListener("click",async function(){
   if(!state.pairing){toast("Save Remote QR pairing first.");return;}
   this.disabled=true;const label=this.textContent;this.textContent="Checking…";
   try{const online=await status();toast(online?"Shield online.":"Shield offline or unavailable; see pairing status.");}
   finally{this.disabled=false;this.textContent=label;}
 });
 $("forgetCompanion").addEventListener("click",()=>{
   state.pairing=null;localStorage.removeItem(STORAGE.pairing);
   $("companionDevice").value="";$("companionToken").value="";$("companionAuto").checked=false;
   updatePairChip("Flud Companion · Not paired");toast("Pairing removed from this browser.");
 });
 api("/api/providers").then(({providers,audit})=>{
  state.providers=providers;state.audit=audit||null;
  chooseProviders();renderProviders();
  const tested=providers.filter(p=>p.lastAudit?.state==="results").length;
  $("notice").textContent=state.importNote||("Ready. "+providers.length+" source adapters; "+tested+" returned results in the last recorded test. Availability may change.");
  if(state.items.length)renderResults();
 }).catch(e=>$("notice").textContent="API unavailable: "+e.message);
 status();
 if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}
document.addEventListener("DOMContentLoaded",init);
