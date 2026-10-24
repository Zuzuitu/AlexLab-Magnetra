"use strict";
const $=id=>document.getElementById(id);
const currentLanguage=()=>globalThis.MagnetraI18n?.language==="it"?"it-IT":"ro-RO";
// Only localized strings are shown in the live PWA. Fallback supports offline tests.
const tr=(key,args={})=>{
 const translated=globalThis.MagnetraI18n?.t(key,args);
 return translated||String(key).replace(/\{(\w+)\}/g,(_,name)=>String(args[name]??""));
};
// Diagnostic mode is explicit, session/URL-scoped and stores no private values.
const theRarBgDiagnosticMode=typeof location!=="undefined"&&
 typeof URLSearchParams!=="undefined"&&
 new URLSearchParams(location.search||"").get("magnetra_diag")==="1";
function theRarBgDiagnosticSuffix(error){
 if(!theRarBgDiagnosticMode)return "";
 const data=error?.magnetraDiagnostic;
 if(!data||data.build!=="THERARBAG_IPHONE_DIAG_V1")
   return " [Trace: Worker fără raport]";
 const stage=value=>typeof value==="string"&&/^[A-Z0-9_]{3,40}$/.test(value)?value:"UNAVAILABLE";
 const fp=typeof data.detailFingerprint==="string"&&/^[a-f0-9]{12}$/.test(data.detailFingerprint)
   ?data.detailFingerprint:"unavailable";
 const time=Number.isFinite(data.elapsedMs)?Math.max(0,Math.min(30000,Math.round(data.elapsedMs))):0;
 return " [Trace "+data.build+"; URL "+fp+"; HTML "+stage(data.htmlStage)+
   "; JSON "+stage(data.jsonStage)+"; "+time+"ms]";
}
const genericError=(failure)=>{
 const code=String(failure?.code||"").toUpperCase();
 const msg=String(failure?.message||failure?.error||"").toLowerCase();
 if(/TIMEOUT/.test(code)||/timed out|timeout/.test(msg))return tr("Provider timed out");
 if(/RATE_LIMIT|429/.test(code)||/rate.limit|too many requests/.test(msg))return tr("Provider rate limited");
 if(/REDIRECT/.test(code)||/redirect/.test(msg))return tr("Provider redirected");
 if(/403|BLOCK|REJECT|FORBIDDEN/.test(code)||/reject|forbidden/.test(msg))return tr("Provider request rejected");
 return tr("Provider unavailable");
};
// A 502 from the provider itself cannot be repaired in the browser.
 // Keep the existing Details action as a manual, source-owned fallback.
function magnetFailureText(item,error){
 if(item?.provider==="therarbag"){
  const failures={
   SOURCE_HTTP_403:"TheRarBg refused the details request (403). Open Details on the source site.",
   SOURCE_HTTP_404:"TheRarBg details page is missing (404). Open Details on the source site.",
   SOURCE_HTTP_429:"TheRarBg is limiting requests (429). Try this result later.",
   SOURCE_HTTP_500:"TheRarBg details server returned 500. Try this result later.",
   SOURCE_HTTP_502:"TheRarBg details server returned 502. Try this result later.",
   SOURCE_HTTP_503:"TheRarBg details server returned 503. Try this result later.",
   SOURCE_HTTP_504:"TheRarBg details server returned 504. Try this result later.",
   SOURCE_CHALLENGE:"TheRarBg requires browser verification. Open Details on the source site.",
   DETAIL_NO_BTIH:"TheRarBg details page did not contain a supported magnet or unique info hash.",
   SOURCE_TIMEOUT:"TheRarBg details request timed out. Try this result later.",
   SOURCE_REDIRECT:"TheRarBg details redirected outside the approved source route.",
   SOURCE_PAGE_TOO_LARGE:"TheRarBg details page exceeded the safe size limit.",
   DETAIL_URL_REJECTED:"TheRarBg details URL was rejected by source validation.",
   SOURCE_NETWORK:"Magnetra could not connect to TheRarBg details.",
   WORKER_RUNTIME:"The magnet resolver is temporarily unavailable.",
   CLIENT_NETWORK:"Your phone could not reach Magnetra's magnet resolver.",
   CLIENT_ABORT:"The magnet request was cancelled before completion.",
   EDGE_403:"Magnetra was blocked before receiving a server response (HTTP 403).",
   RESPONSE_NOT_JSON:"Magnetra received a non-JSON response while resolving the magnet."
  };
  return tr(failures[error?.magnetraCode]||"TheRarBg could not provide this magnet. Open Details to try it on the source site.")+
    theRarBgDiagnosticSuffix(error);
 }
 return genericError(error);
}
const STORAGE={selected:"magnetra.providers.v1",bookmarks:"magnetra.bookmarks.v1",pairing:"magnetra.companion.v1",paused:"magnetra.paused-indexers.v1"};
const preferred=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"];
const previousPreferred=["knaben","torrentscsv","thepiratebay","internetarchive"];
// Owner-curated PWA picker exclusion only: all 46 adapters remain in the API/Android.
// Excluded IDs cannot be displayed, selected, restored from old localStorage,
// bulk-selected or queried by the PWA. They are not removed from source code.
const hiddenIndexerIds=new Set(["anirena","bt4g","bitsearch","extdotto","eztvx","filemood","limetorrents","nyaasi","1337x","tokyotoshokan","torrentdatabase","torrentdownloadinfo","torrentdownloads","torrentkitty","uindex","xxxclub","torrentz","animetosho","mikanproject","bangumimoe","btsow","dmhy","linuxtracker","mypornclub","nekobt","sukebeinyaa","ytsmx","anilibria","blueroms","epublibre","megapeer","rutorinfo","xxxtracker","fitgirlrepacks"]);
const BTDIGG_MIN_GAP_MS=5500;
// Client-side pacing only. This does not bypass the Rock64 rate limit or retry
// failed searches; it defers one user-requested search and is abortable.
const btdiggPacing={nextAllowedAt:0,lastGoodQuery:null,lastGoodUntil:0};
function btdiggWaitMs(query,at=Date.now()){
 if(query===btdiggPacing.lastGoodQuery&&at<btdiggPacing.lastGoodUntil)return 0;
 return Math.max(0,btdiggPacing.nextAllowedAt-at);
}
async function waitForBTDigg(query,signal){
 const wait=btdiggWaitMs(query);
 if(wait){
  $("notice").textContent=tr("BTDigg: waiting {n}s to respect source search limits…",{n:Math.ceil(wait/1000)});
  await new Promise((resolve,reject)=>{
   if(signal.aborted){reject(new DOMException("Search cancelled","AbortError"));return;}
   let done=false;
   let timer;
   const finish=(cancelled)=>{
    if(done)return;
    done=true;
    clearTimeout(timer);
    signal.removeEventListener("abort",onAbort);
    if(cancelled)reject(new DOMException("Search cancelled","AbortError"));
    else resolve();
   };
   const onAbort=()=>finish(true);
   signal.addEventListener("abort",onAbort,{once:true});
   timer=setTimeout(()=>finish(false),wait);
  });
 }
 if(signal.aborted)throw new DOMException("Search cancelled","AbortError");
}
const state={providers:[],audit:null,selected:new Set(preferred),items:[],bookmarks:{},pairing:null,bookmarksMode:false,searching:false,searchAbort:null,sessionAudit:{},excludedOffTopic:0,pausedIds:new Set()};
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
  let response;
  try{response=await fetch(path,{cache:"no-store",...options});}
  catch(e){
    if(path!=="/api/resolve")throw e;
    const failure=Error(tr("Provider unavailable"));
    failure.magnetraCode=e?.name==="AbortError"?"CLIENT_ABORT":"CLIENT_NETWORK";
    throw failure;
  }
  let data;
  try{data=await response.json();}catch{
    const failure=Error(tr("Server returned an invalid response"));
    if(path==="/api/resolve")failure.magnetraCode=response.status===403?"EDGE_403":"RESPONSE_NOT_JSON";
    throw failure;
  }
  if(!response.ok){
    const failure=Error(tr("Request failed ({code})",{code:response.status}));
    if(path==="/api/resolve"){
      // Server-side codes are finite, source-specific classifications.
      // Never echo provider exception strings, URLs, magnets or tokens.
      if(typeof data?.code==="string"&&/^[A-Z0-9_]{3,40}$/.test(data.code))
        failure.magnetraCode=data.code;
      if(theRarBgDiagnosticMode&&data?.diagnostic?.build==="THERARBAG_IPHONE_DIAG_V1")
        failure.magnetraDiagnostic=data.diagnostic;
    }
    throw failure;
  }
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
  // The opt-in finite forensic string stays visible long enough for an owner
  // screenshot; normal notifications retain their original 3.5-second timing.
  const duration=theRarBgDiagnosticMode&&message.includes("[Trace")?20000:3500;
  toastTimer=setTimeout(()=>t.classList.remove("show"),duration);
}
function openDialog(id){$(id).showModal();}
function closeDialog(id){$(id).close();}
function updatePairChip(text,online=false){
 const chip=$("companionChip");chip.classList.toggle("online",online);
 $("companionStatus").textContent=text;
}
function updateBookmarkCount(){const count=$("bookmarkCount");if(count)count.textContent=String(Object.keys(state.bookmarks).length);}
// A provider error at the end of a completed search only affects future searches.
 // No source retries, no removal of adapter identity and no changes to Flud.
function pausedFromFailures(ids,failures,selected){
 const queried=new Set(ids);
 const failed=new Set(failures.map(f=>f.provider).filter(id=>queried.has(id)&&selected.has(id)));
 const active=[...selected].filter(id=>queried.has(id)&&!failed.has(id));
 return active.length?[...failed]:[];
}
function savePausedSources(){
 save(STORAGE.paused,[...state.pausedIds]);
 const visible=[...state.pausedIds].filter(id=>selectableProviders().some(p=>p.id===id));
 $("sourceHealthSummary").textContent=visible.length?
  tr("{n} failed indexer(s) paused automatically. Next searches use the remaining selected sources; tap Indexers to retry.",{n:visible.length}):"";
}
function unpauseSources(ids){
 for(const id of ids)state.pausedIds.delete(id);
 savePausedSources();
}
function pauseFailedSources(ids,failures){
 const paused=pausedFromFailures(ids,failures,state.selected);
 if(!paused.length)return 0;
 for(const id of paused){
  state.selected.delete(id);
  state.pausedIds.add(id);
 }
 save(STORAGE.selected,[...state.selected]);
 savePausedSources();
 updateProviderCount();renderProviders();
 return paused.length;
}
function selectableProviders(){
 return state.providers.filter(p=>p.ported&&!hiddenIndexerIds.has(p.id));
}
function chooseProviders(){
 const stored=load(STORAGE.selected,null);
 if(Array.isArray(stored)){
  // One-time, non-destructive migration: only the exact old default
  // gets BTDigg added. A user's custom selection or manual opt-out wins.
  const wasOldDefault=stored.length===previousPreferred.length&&
    previousPreferred.every(id=>stored.includes(id));
  state.selected=new Set(wasOldDefault?preferred:stored);
 }
 const valid=new Set(selectableProviders().map(p=>p.id));
 state.selected=new Set([...state.selected].filter(x=>valid.has(x)));
 if(!state.selected.size)state.selected=new Set(preferred.filter(x=>valid.has(x)));
 const recorded=load(STORAGE.paused,[]);
 state.pausedIds=new Set((Array.isArray(recorded)?recorded:[])
  .filter(id=>valid.has(id)&&!state.selected.has(id)));
 save(STORAGE.selected,[...state.selected]);
 savePausedSources();
 updateProviderCount();
}
function updateProviderCount(){$("providerCount").textContent=String(state.selected.size)+"/"+selectableProviders().length;}
// Prioritize sources with real AlexLab gateway/resolve work and proved adapters.
// UI ordering does not affect original provider IDs, source attribution or uptime.
const priorityIndexerIds=[
 "btdigg","torrent9","oxtorrent",
 "knaben","torrentscsv","thepiratebay","internetarchive"
];
function orderedProviders(providers){
 const priority=new Map(priorityIndexerIds.map((id,index)=>[id,index]));
 // Prioritized source IDs remain at the top even if an audit reports an error;
 // all other visible sources are ordered by actual observed audit status.
 const rank=p=>{
  if(!p.ported)return 3;
  const status=state.sessionAudit[p.id]?.state||p.lastAudit?.state;
  return status==="results"?0:status==="error"?2:1;
 };
 return [...providers].filter(p=>!hiddenIndexerIds.has(p.id)).sort((a,b)=>{
  const aPriority=priority.get(a.id),bPriority=priority.get(b.id);
  if(aPriority!==undefined||bPriority!==undefined){
   if(aPriority===undefined)return 1;
   if(bPriority===undefined)return -1;
   return aPriority-bPriority;
  }
  return rank(a)-rank(b)||
   a.name.localeCompare(b.name,undefined,{sensitivity:"base"})||
   a.id.localeCompare(b.id);
 });
}
function renderProviders(){
 const grid=$("providerGrid");grid.replaceChildren();
 const visible=selectableProviders();
 const ported=visible.length;
 const audited=visible.filter(p=>p.lastAudit?.state==="results").length;
 $("catalogSummary").textContent=tr("{n} sources available",{n:ported});
 for(const p of orderedProviders(visible)){
  const row=el("div","provider-row"+(p.ported?"":" missing"));
  const label=el("label");
  const input=document.createElement("input");
  input.type="checkbox";input.value=p.id;input.checked=state.selected.has(p.id);input.disabled=!p.ported;
  input.addEventListener("change",()=>{
    if(input.checked){
      if(state.selected.size>=selectableProviders().length){input.checked=false;toast(tr("All visible indexers are already selected."));return;}
      state.selected.add(p.id);
      unpauseSources([p.id]);
    }else state.selected.delete(p.id);
    save(STORAGE.selected,[...state.selected]);updateProviderCount();
  });
  const name=el("strong","",p.name);
  label.append(input,name);
  const paused=state.pausedIds.has(p.id)&&!state.selected.has(p.id);
  row.append(label);
  if(paused)row.append(el("small","audit-error",tr("Paused")));
  grid.append(row);
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
 try {await navigator.clipboard.writeText(magnet);toast(tr("Magnet copied"));}
 catch {
   const t=document.createElement("textarea");t.value=magnet;t.style.position="fixed";t.style.top="-999px";document.body.append(t);t.select();
   const ok=document.execCommand("copy");t.remove();toast(tr(ok?"Magnet copied":"Copy failed"));
 }
}
async function ensureMagnet(item){
 if(item.magnet?.startsWith("magnet:?"))return item.magnet;
 // Verified production 2026 card audit: OxTorrent/Torrent9 magnetSource
 // points to a noncanonical download/ad route on every sampled listing
 // (50 OxTorrent + 20 Torrent9). The source-owned details page resolves
 // genuine BTIH magnets through the fixed-origin HTML gateway.
 // Owner's actual iPhone TheRarBg incident (#40085002856): the listing
 // exposed both details and magnetSource; magnetSource was the EXACT rejected
 // iPhone trace URL while the original same-result details URL resolved to a
 // verified magnet. Use the provider's validated details page first.
 // Exact original owner 0Magnet /!lxbV (read-only run #40133513283):
 // this card has an auxiliary magnetSource but its original details URL yields
 // a verified BTIH through the current production /api/resolve endpoint.
 // Choose this source-owned detail, not its alternate listing link.
 // Keep all remaining 42 providers' source precedence unchanged.
 const preferDetails=item.provider==="oxtorrent"||item.provider==="torrent9"||item.provider==="therarbag"||item.provider==="0magnet";
 const source=preferDetails ? item.details : item.magnetSource||item.details;
 if(!source)throw Error(tr("Provider has no supported magnet or details link."));
 const headers={"content-type":"application/json"};
 if(item.provider==="therarbag"&&theRarBgDiagnosticMode)
   headers["x-magnetra-resolve-diagnostic"]="owner-opt-in-20261024-v1";
 const res=await api("/api/resolve",{
  method:"POST",headers,
  body:JSON.stringify({provider:item.provider,details:source})
 });
 if(!res.magnet?.startsWith("magnet:?"))throw Error(tr("Provider did not return a valid magnet."));
 item.magnet=res.magnet;
 if(state.bookmarks[item.id]){state.bookmarks[item.id]=item;save(STORAGE.bookmarks,state.bookmarks);}
 return item.magnet;
}
async function verifyCompanionReceipt(commandId) {
 if(!commandId||!state.pairing)return tr("Queued ✓");
 // Relay acceptance, Shield acknowledgement, and torrent download are distinct states.
 for(let attempt=0;attempt<4;attempt++){
  await new Promise(resolve=>setTimeout(resolve,2000));
  try{
   const data=await api("/api/companion/status",{
    method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(state.pairing)
   });
   if(data.lastResult?.id===commandId){
    if(data.lastResult.ok){toast(tr("Shield acknowledged the magnet command."));return tr("Shield ✓");}
    toast(tr("Shield rejected magnet: {reason}",{reason:tr("Unknown error")}));
    return tr("Retry send");
   }
  }catch{return tr("Queued ✓");}
 }
 toast(tr("Queued; waiting for Shield confirmation."));
 return tr("Queued ✓");
}
async function sendMagnet(item,button){
 if(!state.pairing?.deviceId||!state.pairing?.token){openDialog("settingsDialog");toast(tr("Pair Flud Companion first."));return;}
 const itemKey=item.id||item.magnet;
 if(activeCompanionItems.has(itemKey)){toast(tr("This magnet is already being sent."));return;}
 const original=button.textContent;
 let activeKey=null;
 activeCompanionItems.add(itemKey);
 if(item.id)companionLabels.set(itemKey,tr("Sending…"));
 button.disabled=true;button.textContent=tr("Sending…");
 try{
   const magnet=await ensureMagnet(item);
   const key=magnetIdentity(magnet,state.pairing.deviceId);
   if(activeCompanionMagnets.has(key)){
     toast(tr("This magnet is already being sent."));return;
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
   if(!result.ok||result.queued!==true)throw Error(tr("Relay did not confirm a queued command."));
   if(typeof result.id!=="string"||!result.id)throw Error(tr("Relay returned no command receipt ID."));
   toast(tr(result.duplicate?"Already queued in Companion.":"Magnet queued; awaiting Shield acknowledgement."));
   button.textContent=tr("Queued ✓");
   if(item.id)companionLabels.set(itemKey,tr("Queued ✓"));
   const label=await verifyCompanionReceipt(result.id);
   button.textContent=label;
   if(item.id)companionLabels.set(itemKey,label);
 }catch(e){
   toast(magnetFailureText(item,e));button.title=magnetFailureText(item,e);
   if(item.id)companionLabels.set(itemKey,tr("Retry send"));
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
 const sorted=sortItems(items);$("resultCount").textContent=tr(state.bookmarksMode?"{n} SAVED":"{n} MATCHES",{n:sorted.length});
 $("resultsTitle").textContent=tr(state.bookmarksMode?"Saved bookmarks":"Search results");
 $("searchQuality").textContent=state.bookmarksMode?"":state.excludedOffTopic?
  tr("{n} unrelated source results excluded from this search. Only title-matching entries are shown.",{n:state.excludedOffTopic}):"";
 if(!sorted.length){
   if(state.bookmarksMode)$("notice").textContent=tr("No bookmarks saved yet.");
   else if(!state.searching && state.items.length===0 && $("query").value.trim())$("notice").textContent=tr("No matching titles. Try another title, fewer keywords or different indexers.");
   return;
 }
 $("notice").textContent="";
 for(const item of sorted.slice(0,400)){
   const card=el("article","result");
   const body=el("div"),title=el("h3","result-title",item.name),info=el("div","result-info");
   info.append(el("span","tag",state.providers.find(p=>p.id===item.provider)?.name||item.provider));
   for(const field of [item.size, item.seeders!==null&&item.seeders!==undefined?tr("{n} seeders",{n:item.seeders}):null,item.peers!==null&&item.peers!==undefined?tr("{n} peers",{n:item.peers}):null,item.date?String(item.date).slice(0,10):null]){
     if(!field)continue;info.append(el("span","meta-dot","·"),el("span","",field));
   }
   body.append(title,info);
   const actions=el("div","result-actions");
   const sendButton=addAction(actions,companionLabels.get(item.id)||tr("Send to Flud"),function(){sendMagnet(item,this)},"send");
   sendButton.disabled=activeCompanionItems.has(item.id);
   addAction(actions,tr("Copy"),async()=>{try{await copyMagnet(await ensureMagnet(item));}catch(e){toast(magnetFailureText(item,e));}});
   addAction(actions,tr("Share"),async()=>{
     try{
       const magnet=await ensureMagnet(item);
       if(navigator.share){
         try{await navigator.share({title:item.name,text:magnet});}
         catch(e){if(e?.name!=="AbortError")await copyMagnet(magnet);}
       }else await copyMagnet(magnet);
     }catch(e){toast(magnetFailureText(item,e));}
   });
   if(item.magnet){
     const magnet=el("a","action","Magnet");magnet.href=item.magnet;magnet.rel="noopener noreferrer";magnet.title=tr("Open in your installed torrent client");actions.append(magnet);
   }else{
     addAction(actions,tr("Resolve"),async function(){
       const old=this.textContent;this.disabled=true;this.textContent=tr("Resolving…");
       try{await ensureMagnet(item);toast(tr("Magnet resolved."));renderResults();}
       catch(e){toast(magnetFailureText(item,e));this.textContent=old;this.disabled=false;}
     });
   }
   if(item.torrentFile)downloadAction(actions,".torrent ↗",item.torrentFile);
   if(item.details)downloadAction(actions,tr("Details ↗"),item.details);
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
 // Hidden indexers never appear in the failure/alternative panel either.
 const visibleFailures=failures.filter(f=>!hiddenIndexerIds.has(f.provider));
 if(!visibleFailures.length)return;
 const details=el("details","failed-sources");
 if(visibleFailures.length<=2)details.open=true;
 const summary=el("summary","failed-sources-title",tr("{n} source(s) unavailable · See alternatives",{n:visibleFailures.length}));
 details.append(summary);
 const onlyBTDigg=visibleFailures.every(f=>f.provider==="btdigg");
 const message=el("p","failed-sources-note",tr(onlyBTDigg
  ?"BTDigg searches run from Rock64 at home, not from your phone. A temporary upstream limit, timeout or tunnel issue does not mean this indexer is permanently offline."
  :"Some external sites restrict searches from Cloudflare. Magnetra cannot bypass their verification. You can open a source directly or search independently through other indexers."));
 details.append(message);
 for(const failure of visibleFailures){
  const entry=el("div","source-failure");
  const line=el("div","source-failure-content");
  const provider=state.providers.find(p=>p.id===failure.provider);
  line.append(el("strong","",provider?.name||failure.provider));
  const message=failure.provider==="btdigg"&&failure.code==="RATE_LIMIT"
   ?tr("BTDigg is limiting requests. Wait a few seconds before another search.")
   :genericError(failure);
  const why=el("span","",message);
  line.append(why);
  entry.append(line);
  const link=failure.provider==="btdigg"?null:(failure.openUrl || provider?.url);
  if(/^https:\/\//.test(link||"")){
   const a=el("a","source-open",tr(failure.openUrl?"Open source search ↗":"Visit source ↗"));
   a.href=link;a.target="_blank";a.rel="noopener noreferrer";
   entry.append(a);
  }
  details.append(entry);
 }
 const alternatives=el("button","source-alt",tr("Search with available indexers →"));
 alternatives.type="button";
 alternatives.addEventListener("click",()=>{
  // Use successful observations from THIS session, not obsolete dated audit
  // or hardcoded providers that may currently be blocked.
  const live=orderedProviders(selectableProviders()).filter(p=>p.ported&&
   ["results","empty-unverified"].includes(state.sessionAudit[p.id]?.state)).map(p=>p.id);
  const ids=live.length?live:["knaben","torrentscsv","thepiratebay"].filter(id=>
   selectableProviders().some(p=>p.id===id));
  if(!ids.length){toast(tr("No alternative indexers are available."));return;}
  state.selected=new Set(ids);
  unpauseSources(ids);
  save(STORAGE.selected,ids);updateProviderCount();renderProviders();
  if(state.searching){
    state.pendingAlternativeSearch=true;
    state.searchAbort?.abort();
    toast(tr("Cancelling the current search and starting alternatives."));
  }else search();
 });
 details.append(alternatives);
 root.append(details);
}
async function search(){
 if(state.searching){
  state.searchAbort?.abort();
  $("notice").textContent=tr("Cancelling search; keeping results already found…");
  return;
 }
 const query=$("query").value.trim();
 if(query.length<2){toast(tr("Enter at least two characters"));return;}
 if(!state.selected.size){openDialog("providersDialog");toast(tr("Select at least one indexer."));return;}
 const ids=[...state.selected],category=$("category").value,failures=[];
 const controller=new AbortController();
 state.searchAbort=controller;state.searching=true;state.bookmarksMode=false;state.items=[];state.excludedOffTopic=0;
 $("searchButton").disabled=false;$("searchButton").textContent=tr("Cancel search ×");
 $("notice").textContent=tr("Searching {n} indexers…",{n:ids.length});$("providerErrors").replaceChildren();renderResults();
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
     if(id==="btdigg"){
      await waitForBTDigg(query,controller.signal);
      // Guard even a cancelled HTTP request: Rock64 may still be working.
      btdiggPacing.nextAllowedAt=Date.now()+BTDIGG_MIN_GAP_MS;
     }
     const data=await api(url.pathname+url.search,{signal:controller.signal});
     if(controller.signal.aborted)return;
     state.items.push(...(data.results||[]));
     // Source-side relevance exclusions are not provider transport errors.
     const quality=(data.stats||[]).find(s=>s.provider===id);
     state.excludedOffTopic+=Math.max(0,Number(quality?.excludedOffTopic)||0);
     for(const e of data.errors||[])failures.push(e);
     const observed=(data.stats||[]).find(s=>s.provider===id);
     if(observed)state.sessionAudit[id]={
      state:observed.ok?(observed.count>0?"results":"empty-unverified"):"error",
      count:observed.count||0,at:new Date().toLocaleString(currentLanguage())
     };
     if(id==="btdigg"){
      // Only a real positive result is reused by Rock64's 20-minute cache.
      if(observed?.ok&&observed.count>0){
       btdiggPacing.lastGoodQuery=query;
       btdiggPacing.lastGoodUntil=Date.now()+20*60*1000;
      }
      btdiggPacing.nextAllowedAt=Date.now()+BTDIGG_MIN_GAP_MS;
     }
    }catch(e){
     if(controller.signal.aborted){
      if(id==="btdigg")btdiggPacing.nextAllowedAt=
       Math.max(btdiggPacing.nextAllowedAt,Date.now()+BTDIGG_MIN_GAP_MS);
      return;
     }
     failures.push({provider:id,error:e.message,message:tr("Magnetra could not reach this provider through the API.")});
     state.sessionAudit[id]={state:"error",count:0,at:new Date().toLocaleString(currentLanguage())};
     if(id==="btdigg")btdiggPacing.nextAllowedAt=Date.now()+BTDIGG_MIN_GAP_MS;
    }
    if(controller.signal.aborted)return;
    completed++;
    renderResults();
    renderProviders(); // Update session-only observations; no extra provider calls.
    $("notice").textContent=tr("Searched {done}/{all} indexers · {n} relevant matches.",{done:completed,all:ids.length,n:state.items.length});
    renderProviderErrors(failures);
   }
  }));
  if(!controller.signal.aborted){
   const paused=pauseFailedSources(ids,failures);
   if(!state.items.length)$("notice").textContent=tr(failures.length?"No matching results; some indexers failed.":"No matching titles in selected indexers.");
   else $("notice").textContent="";
   if(paused)toast(tr("{n} failing indexer(s) paused for future searches.",{n:paused}));
  }
 }finally{
  const cancelled=controller.signal.aborted;
  state.searchAbort=null;state.searching=false;
  $("searchButton").disabled=false;$("searchButton").textContent=tr("Search →");
  renderResults();
  if(state.pendingAlternativeSearch){
   state.pendingAlternativeSearch=false;
   search();
   return;
  }
  if(cancelled)$("notice").textContent=tr("Search cancelled. Results already found are preserved.");
  else $("resultsTitle").scrollIntoView({block:"nearest",behavior:"smooth"});
 }
}
async function status(){
 if(!state.pairing){updatePairChip(tr("Flud Companion · Not paired"));return;}
 try{
   const data=await api("/api/companion/status",{
     method:"POST",headers:{"content-type":"application/json"},
     body:JSON.stringify(state.pairing)
   });
   const online=data.online===true;
   updatePairChip(tr(online?"Flud Companion · Online":"Flud Companion · Offline"),online);
   $("pairStatus").textContent=tr(online?(data.autoStartReady?"Shield online · Auto-start ready":"Shield online · Auto-start not ready"):"Shield offline");
   return online;
 }catch(e){updatePairChip(tr("Flud Companion · Unavailable"));$("pairStatus").textContent=genericError(e);return false;}
}
function switchLanguage(locale){
 if(!globalThis.MagnetraI18n?.set(locale))return;
 renderProviders();renderResults();savePausedSources();
 if(!state.searching)$("searchButton").textContent=tr("Search →");
 else $("searchButton").textContent=tr("Cancel search ×");
 const chip=$("companionChip");
 const online=chip.classList.contains?.("online")===true;
 updatePairChip(tr(!state.pairing?"Flud Companion · Not paired":online?"Flud Companion · Online":"Flud Companion · Offline"),online);
 if(state.pairing)$("pairStatus").textContent=tr(online?"Shield online.":"Shield offline");
 $("viewBookmarks").firstChild.textContent=state.bookmarksMode?tr("Back to search")+" ":tr("☆ Bookmarks")+" ";
 if(!state.items.length&&!state.bookmarksMode&&!state.searching)$("notice").textContent=tr("Ready. {n} sources available.",{n:selectableProviders().length});
}
function init(){
 // Previously shared import links may contain magnet URI metadata.
 // Retired BTDigg imports are never parsed; scrub their old URL fragments.
 if(location.hash.startsWith("#btdigg=")){
  try{history.replaceState(null,"",location.pathname+location.search);}
  catch{ /* Browser may prohibit history editing; no import processing occurs. */ }
 }
 state.bookmarks=load(STORAGE.bookmarks,{});
 state.pairing=load(STORAGE.pairing,null);
 if(state.pairing){
  $("companionDevice").value=state.pairing.deviceId||"";
  $("companionToken").value=state.pairing.token||"";
  $("companionAuto").checked=state.pairing.autoStart===true;
 }
 updateBookmarkCount();
 $("languageSelect").addEventListener("change",e=>switchLanguage(e.target.value));
 $("searchForm").addEventListener("submit",e=>{e.preventDefault();search();});
 $("sort").addEventListener("change",renderResults);
 $("settingsButton").addEventListener("click",()=>openDialog("settingsDialog"));
 $("companionChip").addEventListener("click",()=>openDialog("settingsDialog"));
 $("pasteMagnetButton").addEventListener("click",async function(){
  if(!state.pairing){openDialog("settingsDialog");toast(tr("Pair Flud Companion first."));return;}
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
    toast(tr("Paste a valid magnet link."));return;
  }
  closeDialog("manualMagnetDialog");
  sendMagnet({magnet},$("pasteMagnetButton"));
 });

 $("providersButton").addEventListener("click",()=>openDialog("providersDialog"));
 for(const button of document.querySelectorAll("[data-close]"))button.addEventListener("click",()=>closeDialog(button.dataset.close));
 $("viewBookmarks").addEventListener("click",()=>{
  state.bookmarksMode=!state.bookmarksMode;
  $("viewBookmarks").firstChild.textContent=state.bookmarksMode?tr("Back to search")+" ":tr("☆ Bookmarks")+" ";
  renderResults();
 });
 $("selectWorking").addEventListener("click",()=>{
  const ids=orderedProviders(selectableProviders()).filter(p=>p.ported&&p.lastAudit?.state==="results").map(p=>p.id);
  if(!ids.length){toast(tr("No tested sources with results in the saved audit."));return;}
  state.selected=new Set(ids);
  unpauseSources(ids);
  save(STORAGE.selected,ids);renderProviders();updateProviderCount();
  toast(tr("Selected {n} verified sources.",{n:ids.length}));
 });
 $("selectAllProviders").addEventListener("click",()=>{
  const ids=selectableProviders().map(p=>p.id);
  state.selected=new Set(ids);
  unpauseSources(ids);
  save(STORAGE.selected,ids);renderProviders();updateProviderCount();
  toast(tr("Selected all {n} visible indexers; hidden sources stay excluded.",{n:ids.length}));
 });
 $("importPairing").addEventListener("click",()=>{
  try{
   const u=new URL($("pairLink").value.trim());
   if(u.origin!=="https://flud-remote.alexlab.media")throw Error(tr("Only the approved Flud Companion relay is supported."));
   const params=new URLSearchParams(u.hash.replace(/^#/,""));
   const device=params.get("device")||"",token=params.get("token")||"";
   if(!/^[A-Za-z0-9_-]{16,128}$/.test(device)||token.length<20)throw Error(tr("Remote QR link has no valid pairing credentials."));
   $("companionDevice").value=device;$("companionToken").value=token;
   $("pairLink").value="";
   toast(tr("QR pairing imported. Tap Save pairing."));
  }catch(e){toast(tr("Invalid Remote QR URL"));}
 });
 $("companionForm").addEventListener("submit",e=>{
  e.preventDefault();
  const deviceId=$("companionDevice").value.trim(),token=$("companionToken").value.trim();
  if(!/^[A-Za-z0-9_-]{16,128}$/.test(deviceId)||token.length<20){toast(tr("Check Device ID and Remote token."));return;}
  state.pairing={deviceId,token,autoStart:$("companionAuto").checked};
  save(STORAGE.pairing,state.pairing);closeDialog("settingsDialog");toast(tr("Companion paired in this browser."));status();
 });
 $("checkCompanion").addEventListener("click",async function(){
   if(!state.pairing){toast(tr("Save Remote QR pairing first."));return;}
   this.disabled=true;const label=this.textContent;this.textContent=tr("Checking…");
   try{const online=await status();toast(tr(online?"Shield online.":"Shield offline or unavailable; see pairing status."));}
   finally{this.disabled=false;this.textContent=label;}
 });
 $("forgetCompanion").addEventListener("click",()=>{
   state.pairing=null;localStorage.removeItem(STORAGE.pairing);
   $("companionDevice").value="";$("companionToken").value="";$("companionAuto").checked=false;
   updatePairChip(tr("Flud Companion · Not paired"));toast(tr("Pairing removed from this browser."));
 });
 api("/api/providers").then(({providers,audit})=>{
  state.providers=providers;state.audit=audit||null;
  chooseProviders();renderProviders();
  $("notice").textContent=tr("Ready. {n} sources available.",{n:selectableProviders().length});
  if(state.items.length)renderResults();
 }).catch(e=>$("notice").textContent=tr("API unavailable"));
 status();
 if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
}
document.addEventListener("DOMContentLoaded",init);
