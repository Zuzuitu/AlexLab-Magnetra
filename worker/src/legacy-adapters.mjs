import {SOURCE_HEADERS,fetchProviderSameOrigin} from "./request-headers.mjs";
import {LEGACY_SPECS,legacySearchUrl} from "./legacy-specs.mjs";

const MAX_HTML = 3_000_000;
const TIMEOUT = 11_000;
function allowedExternal(url,host,base=host) {
  try {
    const u=new URL(url,base);
    const expected=new URL(host);
    return u.protocol==="https:" && u.origin===expected.origin && !u.username && !u.password &&
      u.hash==="" && u.href.length<=1500 ? u.toString():null;
  } catch {return null;}
}
export function validateLegacyDetail(id,url) {
  const spec=LEGACY_SPECS[id];
  return spec ? allowedExternal(url,spec.host):null;
}
function magnetHash(hash) {
  return /^(?:[a-f0-9]{40}|[a-z2-7]{32})$/i.test(hash||"") ? "magnet:?xt=urn:btih:"+hash.toLowerCase():null;
}
function fromHashUrl(url,kind){
  if(!url)return null;
  if(kind==="filemood"){
    const m=url.match(/-([a-f0-9]{40})(?:\.html)?(?:[?#]|$)/i);
    return magnetHash(m?.[1]);
  }
  if(kind==="torrentdatabase"){
    const m=url.match(/\/track\/magnet\/([a-f0-9]{40})(?:[/?#]|$)/i);
    return magnetHash(m?.[1]);
  }
  return null;
}
export async function safeProviderHtml(url,options={},fetcher=fetch){
  const res=await fetchProviderSameOrigin(url,{
    ...options,redirect:"manual",
    signal:AbortSignal.timeout(TIMEOUT),
    headers:{...SOURCE_HEADERS,"accept":"text/html,application/xhtml+xml",...(options.headers||{})}
  },fetcher);
  if(!res.ok)throw Error("provider HTTP "+res.status);
  if(res.headers.get("cf-mitigated")==="challenge")throw Error("provider anti-bot challenge");
  if(Number(res.headers.get("content-length")||0)>MAX_HTML)throw Error("provider page too large");
  const html=await res.text();
  if(html.length>MAX_HTML)throw Error("provider page too large");
  if(/<title>\s*(?:Just a moment|Attention Required)|Checking your browser/i.test(html.slice(0,2000)))
    throw Error("provider challenge requires a browser session");
  return html;
}
async function collect(html,spec) {
  if(typeof HTMLRewriter==="undefined")throw Error("Cloudflare HTMLRewriter runtime required");
  const records=[];let current=-1;
  const reader=new HTMLRewriter().on(spec.rows,{element(){records.push({});current=records.length-1;}});
  const fields=["name","details","magnet","magnetSource","magnetHashLink","torrentFile","size","seeders","peers","date","swarm"];
  const links=new Set(["details","magnet","magnetSource","magnetHashLink","torrentFile"]);
  for(const field of fields){
    if(!spec[field])continue;
    const selector=spec.rows+" "+spec[field];
    if(links.has(field)){
      reader.on(selector,{element(node){
        if(current<0||records[current][field])return;
        records[current][field]=node.getAttribute(field==="magnet"?"href":"href");
      }});
    } else {
      reader.on(selector,{text(chunk){
        if(current<0)return;
        records[current][field]=(records[current][field]||"")+chunk.text;
      }});
    }
  }
  await reader.transform(new Response(html,{headers:{"content-type":"text/html"}})).text();
  return records;
}
export async function legacySearch(id,query,category,fetcher=fetch){
  const spec=LEGACY_SPECS[id];
  if(!spec)throw Error("unknown legacy indexer "+id);
  const q=query.trim();
  if(q.length<2||q.length>180)throw Error("invalid query");
  const url=legacySearchUrl(spec,q);
  if(!allowedExternal(url,spec.host))throw Error("legacy search URL outside provider allowlist");
  let options={method:"GET"};
  if(spec.method==="POST_FORM"){
    options={
      method:"POST",
      headers:{"content-type":"application/x-www-form-urlencoded"},
      body:new URLSearchParams([["f[]","-1"],["o","2"],["s","2"],["tm","-1"],
        ["shf","1"],["ta","-1"],["sns","-1"],["sds","4"],["nm",q],["submit","Поиск"]]).toString()
    };
  }
  if(spec.method==="POST_JSON_HTML"){
    options={method:"POST",headers:{"X-Requested-With":"XMLHttpRequest","accept":"application/json"}};
  }
  if(spec.headers)options.headers={...(options.headers||{}),...spec.headers};
  let html=await safeProviderHtml(url,options,fetcher);
  if(spec.method==="POST_JSON_HTML"){
    let obj;try{obj=JSON.parse(html);}catch{throw Error("provider returned invalid JSON");}
    if(typeof obj?.contenido!=="string")throw Error("provider JSON missing contenido HTML");
    html=obj.contenido;
  }
  const records=await collect(html,spec);
  const result=[];
  for(const [i,row] of records.entries()){
    const name=String(row.name||"").trim().replace(/\s+/g," ");
    if(!name)continue;
    const details=allowedExternal(row.details,spec.host,url);
    const magnetSource=allowedExternal(row.magnetSource,spec.host,url);
    const hash=fromHashUrl(row.details,spec.hashFromDetailsSuffix?"filemood":spec.magnetHashLink?"torrentdatabase":null);
    let magnet=String(row.magnet||"").trim();
    if(!magnet.startsWith("magnet:?"))magnet=hash||"";
    if(!magnet&&spec.magnetHashLink)magnet=fromHashUrl(row.magnetHashLink,"torrentdatabase")||"";
    const torrentFile=allowedExternal(row.torrentFile,spec.host,url);
    if(!magnet&&!details&&!magnetSource)continue;
    const swarm=(row.swarm||"").split("/");
    result.push({
      id:row.details||row.magnetSource||String(i),name,magnet:magnet||null,
      details:details||null,magnetSource:magnetSource||null,
      torrentFile:torrentFile||null,category,
      size:row.size||null,date:row.date||null,
      seeders:row.seeders||swarm[0]||null,peers:row.peers||swarm[1]||null
    });
    if(result.length===100)break;
  }
  return result;
}
// TheRarBg detail pages sometimes expose the torrent's own info hash as
// labelled text while rendering the "Magnet Download" action with JavaScript.
// Never infer this value from titles, linked related torrents, or other sites.
// A unique 40-char v1 hash adjacent to "Info Hash:" on the validated detail
// document is sufficient to form the canonical BTIH magnet URI offline.
export function magnetFromTheRarBgInfoHash(html){
  if(typeof html!=="string"||!html||html.length>MAX_HTML)return null;
  const clean=html
    .replace(/<(script|style|noscript)\b[^>]*>[\s\S]*?<\/\1\s*>/gi," ")
    .replace(/<!--[\s\S]*?-->/g," ")
    .replace(/<[^>]*>/g," ")
    .replace(/&nbsp;|&#(?:160|xA0);/gi," ")
    .replace(/&colon;|&#(?:58|x3A);/gi,":")
    .replace(/\s+/g," ");
  const matches=[...clean.matchAll(/\bInfo\s*Hash\s*:\s*([a-f0-9]{40})\b/gi)];
  // A page may render the same source-owned hash in both mobile/desktop
  // sections. Repeated identical hashes are unambiguous; different hashes
  // on one detail page remain unsafe and must never be guessed.
  const uniqueHashes=new Set(matches.map(match=>match[1].toLowerCase()));
  if(uniqueHashes.size!==1)return null;
  return "magnet:?xt=urn:btih:"+[...uniqueHashes][0];
}

// The .torrent File link on the SAME validated TheRarBg detail page can
// reference an iTorrents cache URL named after the v1 torrent infohash.
// This is a source-endorsed metadata pointer, NOT an alternate search indexer:
// no request to the cache and no .torrent download is ever made here.
// Only consider an exact HTTPS cache target in the main "Torrent:" action row,
// accompanied by the page's "Info Hash:" label; never harvest arbitrary
// .torrent links from description, similar posts, scripts, or comments.
export function magnetFromTheRarBgSourceMetadata(html){
  if(typeof html!=="string"||!html||html.length>MAX_HTML)return null;
  const safe=html
    .replace(/<(script|style|noscript|template)\b[^>]*>[\s\S]*?<\/\1\s*>/gi," ")
    .replace(/<!--[\s\S]*?-->/g," ");
  const cleanText=(value)=>value.replace(/<[^>]*>/g," ")
    .replace(/&nbsp;|&#(?:160|xA0);/gi," ")
    .replace(/&colon;|&#(?:58|x3A);/gi,":")
    .replace(/\s+/g," ").trim();
  const visible=cleanText(safe);
  const labelled=[...visible.matchAll(/\bInfo\s*Hash\s*:\s*([a-f0-9]{40})\b/gi)]
    .map(match=>match[1].toLowerCase());
  const cache=[];
  for(const match of safe.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a\s*>/gi)){
    if(!/^\.torrent\s+File$/i.test(cleanText(match[2])))continue;
    const attr=/\bhref\s*=\s*(?:"([^"]+)"|'([^']+)')/i.exec(match[1]);
    if(!attr)continue;
    const href=attr[1]||attr[2];
    let url;
    try{url=new URL(href);}catch{continue;}
    if(url.protocol!=="https:"||url.hostname!=="itorrents.org"||
      url.port||url.username||url.password||url.search||url.hash)continue;
    const path=/^\/torrent\/([a-f0-9]{40})\.torrent$/i.exec(url.pathname);
    if(!path)continue;
    const before=cleanText(safe.slice(Math.max(0,match.index-750),match.index));
    const after=cleanText(safe.slice(match.index+match[0].length,match.index+match[0].length+750));
    // Anchor must belong to this torrent's download controls, not a link
    // to another torrent found elsewhere on the detail page.
    if(!/\bTorrent\s*:\s*[^:]{0,220}$/i.test(before) ||
       !/\bInfo\s*Hash\s*:/i.test(after))continue;
    cache.push(path[1].toLowerCase());
  }
  // Some original TheRarBg detail views keep the torrent's own Info Hash
  // in an adjacent <input value="..."> rather than a visible text node.
  // Accept it ONLY in the page's main Torrent: download controls, with the
  // Info Hash: label immediately preceding the input in the same DOM block.
  // Never pick a hash from related results, comments or executable scripts.
  const inputs=[];
  for(const match of safe.matchAll(/<input\b([^>]*)>/gi)){
    const attribute=/(?:^|\s)value\s*=\s*(?:"([^"]*)"|'([^']*)')/i.exec(match[1]);
    const value=attribute?.[1]??attribute?.[2];
    if(!/^[a-f0-9]{40}$/i.test(value||""))continue;
    const rawBefore=safe.slice(Math.max(0,match.index-6500),match.index);
    const before=cleanText(rawBefore);
    const labelledAt=before.toLowerCase().lastIndexOf("info hash:");
    const rawLabelAt=rawBefore.toLowerCase().lastIndexOf("info hash:");
    if(labelledAt<0||rawLabelAt<0||
      !/^Info Hash:\s*$/i.test(before.slice(labelledAt)))continue;
    // Close of a table row/cell or article between label and value means
    // the input does not belong to this labelled torrent information field.
    const afterLabel=rawBefore.slice(rawLabelAt+"info hash:".length);
    if(/<\/(?:tr|td|table|section|article)\b/i.test(afterLabel)||
      cleanText(afterLabel))continue;
    const torrentAt=before.toLowerCase().lastIndexOf("torrent:");
    if(torrentAt<0||torrentAt>labelledAt||
      labelledAt-torrentAt>700)continue;
    const controls=before.slice(torrentAt,labelledAt);
    if(!/\bMagnet\s+Download\b/i.test(controls)||
      !/\.torrent\s+File/i.test(controls)||
      !/\bCopy\s+Magnet\b/i.test(controls)||
      /\b(?:Similar Posts|Discussion|Description|Thumbnail)\s*:/i.test(controls))
      continue;
    inputs.push(value.toLowerCase());
  }
  // All source-owned evidence must agree. A conflicting valid hash is NOT a
  // reason to choose the first candidate or search another provider.
  const unique=new Set([...labelled,...cache,...inputs]);
  return unique.size===1 ? "magnet:?xt=urn:btih:"+[...unique][0] : null;
}

export async function resolveLegacy(id,url,fetcher=fetch){
  const spec=LEGACY_SPECS[id];
  if(!spec)throw Error("provider not configured");
  const safe=validateLegacyDetail(id,url);
  if(!safe)throw Error("details URL not allowed for this provider");
  // Some indexers publish a same-origin HTTP 302 whose Location is the magnet URI.
  if(spec.resolution==="redirect"){
    const res=await fetcher(safe,{method:"GET",redirect:"manual",signal:AbortSignal.timeout(TIMEOUT)});
    if(res.status>=300&&res.status<400){
      const magnet=res.headers.get("location")||"";
      if(magnet.startsWith("magnet:?")&&magnet.length<=12000)return {magnet};
    }
    throw Error("provider did not return a magnet redirect");
  }
  const html=await safeProviderHtml(safe,{},fetcher);
  if(typeof HTMLRewriter==="undefined")throw Error("Cloudflare HTMLRewriter runtime required");
  let magnet=null;
  const selector=spec.magnetDetails||"a[href^='magnet:']";
  const field=spec.resolution==="input"?"value":"href";
  const reader=new HTMLRewriter().on(selector,{element(e){
    const candidate=e.getAttribute(field);
    if(candidate&&candidate.startsWith("magnet:?")&&candidate.length<=12000)magnet=candidate;
  }});
  await reader.transform(new Response(html,{headers:{"content-type":"text/html"}})).text();
  // Strict single-provider fallback; successful detail HTML was fetched via
  // its fixed-origin allowlisted URL with anti-bot and size guards above.
  if(!magnet&&id==="therarbag")magnet=magnetFromTheRarBgSourceMetadata(html);
  if(!magnet)throw Error("provider details page contains no supported magnet link");
  return {magnet};
}
