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
// Cloudflare's actual HTMLRewriter returns href attribute values with
// literal HTML entities (proven by the 2026-10-24 real-workerd fixture).
// Decode only ampersand delimiter entities on TheRarBg magnet links.
// Do NOT URL-decode other parameters, construct a new hash or touch others.
export function normalizedTheRarBgMagnetHref(href){
 if(typeof href!=="string"||href.length>12000||!href.startsWith("magnet:?"))return null;
 const clean=href.replace(/&(?:amp|#0*38|#x0*26);/gi,"&");
 if(clean.length>12000||
    !/^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)/i.test(clean))
   return null;
 return clean;
}

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
  const unique=new Set([...labelled,...cache]);
  return unique.size===1 ? "magnet:?xt=urn:btih:"+[...unique][0] : null;
}

// If the original TheRarBg HTML detail yields no usable magnet, consult
// the original provider's OWN exact per-detail JSON representation:
// same HTTPS origin, same detail id/slug, only ?format=json.
// Confirmed by the owner-approved real-source audit #40037986215:
// JSON.data.info_hash agrees with the visible original hash and magnet href.
// No alternate torrent indexer, tracker/cache request, title-based guess,
// third-party host, HTML challenge bypass, or .torrent download.
export async function theRarBgOriginalJsonHash(detailUrl,html,fetcher=fetch,diagnostic=null){
  // The optional trace stores finite stages only; it never retains torrent metadata.
  if(diagnostic)diagnostic.jsonStage="JSON_URL_REJECTED";
  let original;
  try {original=new URL(detailUrl);}catch{return null;}
  if(original.protocol!=="https:"||original.origin!=="https://therarbg.com"||
     original.username||original.password||original.hash||original.search||
     !/^\/post-detail\/[a-z0-9]{1,32}\/[a-z0-9][a-z0-9._%~-]{0,340}\/?$/i.test(original.pathname))
    return null;
  const jsonUrl=new URL(original);
  jsonUrl.searchParams.set("format","json");
  if(diagnostic)diagnostic.jsonStage="JSON_FETCHING";
  let response;
  try {
    response=await fetcher(jsonUrl.toString(),{
      method:"GET",redirect:"manual",signal:AbortSignal.timeout(TIMEOUT),
      headers:{...SOURCE_HEADERS,accept:"application/json"}
    });
  }catch{
    if(diagnostic)diagnostic.jsonStage="JSON_TRANSPORT_FAILED";
    return null;
  }
  // Do not follow even same-host redirects for source JSON. The exact detail
  // document is the only source for this fallback.
  if(response.status!==200){
    if(diagnostic)diagnostic.jsonStage=[403,404,429,500,502,503,504].includes(response.status)
      ?"JSON_HTTP_"+response.status:response.status>=300&&response.status<400
      ?"JSON_REDIRECT":"JSON_HTTP_OTHER";
    return null;
  }
  if(response.headers.get("cf-mitigated")==="challenge"){
    if(diagnostic)diagnostic.jsonStage="JSON_CHALLENGE";
    return null;
  }
  if(!/^application\/json(?:\s*;|$)/i.test(response.headers.get("content-type")||"")){
    if(diagnostic)diagnostic.jsonStage="JSON_NOT_JSON";
    return null;
  }
  if(Number(response.headers.get("content-length")||0)>MAX_HTML){
    if(diagnostic)diagnostic.jsonStage="JSON_TOO_LARGE";
    return null;
  }
  let payload;
  try {
    const raw=await response.text();
    if(raw.length>MAX_HTML)return null;
    payload=JSON.parse(raw);
  }catch{
    if(diagnostic)diagnostic.jsonStage="JSON_PARSE_REJECTED";
    return null;
  }
  // Axios 'res.data.info_hash' in TheRarBg's public frontend means the
  // HTTP response BODY has a top-level info_hash, not JSON.data.info_hash.
  // The original-source probe also permits a wrapped {data:{info_hash}} form.
  // Accept only those two exact forms, and refuse conflicting or malformed
  // values instead of searching names, nested recommendations or other URLs.
  const record=payload&&typeof payload==="object"&&!Array.isArray(payload)
    ?payload:null;
  if(!record||Object.hasOwn(record,"error")){
    if(diagnostic)diagnostic.jsonStage="JSON_SCHEMA_REJECTED";
    return null;
  }
  const wrapped=record.data&&typeof record.data==="object"&&!Array.isArray(record.data)
    ?record.data:null;
  const rawHashes=[
    ...(Object.hasOwn(record,"info_hash")?[record.info_hash]:[]),
    ...(wrapped&&Object.hasOwn(wrapped,"info_hash")?[wrapped.info_hash]:[])
  ];
  if(!rawHashes.length||rawHashes.some(h=>typeof h!=="string"||!/^[a-f0-9]{40}$/i.test(h))){
    if(diagnostic)diagnostic.jsonStage="JSON_HASH_MISSING_INVALID";
    return null;
  }
  const distinct=new Set(rawHashes.map(h=>h.toLowerCase()));
  if(distinct.size!==1){
    if(diagnostic)diagnostic.jsonStage="JSON_HASH_CONFLICT";
    return null;
  }
  const hash=[...distinct][0];
  // Refuse a JSON candidate if any independently labelled BTIH or magnet
  // anchor on the already-fetched original page contradicts this same item.
  const safe=html.replace(/<(script|style|noscript|template)\b[^>]*>[\s\S]*?<\/\1\s*>/gi," ")
    .replace(/<!--[\s\S]*?-->/g," ");
  const visible=safe.replace(/<[^>]*>/g," ")
    .replace(/&nbsp;|&#(?:160|xA0);/gi," ")
    .replace(/&colon;|&#(?:58|x3A);/gi,":").replace(/\s+/g," ");
  const ownHashes=[
    ...[...visible.matchAll(/\bInfo\s*Hash\s*:\s*([a-f0-9]{40})\b/gi)].map(x=>x[1]),
    ...[...safe.matchAll(/<a\b[^>]*\bhref\s*=\s*["']magnet:\?xt=urn:btih:([a-f0-9]{40})(?:&|["'])/gi)].map(x=>x[1])
  ];
  if(ownHashes.some(x=>x.toLowerCase()!==hash.toLowerCase())){
    if(diagnostic)diagnostic.jsonStage="JSON_HTML_CONFLICT";
    return null;
  }
  if(diagnostic)diagnostic.jsonStage="JSON_VALID";
  return "magnet:?xt=urn:btih:"+hash.toLowerCase();
}

export async function resolveLegacy(id,url,fetcher=fetch,diagnostic=null){
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
  if(id==="therarbag"&&diagnostic)diagnostic.htmlStage="HTML_FETCHED";
  if(typeof HTMLRewriter==="undefined")throw Error("Cloudflare HTMLRewriter runtime required");
  let magnet=null;
  const selector=spec.magnetDetails||"a[href^='magnet:']";
  const field=spec.resolution==="input"?"value":"href";
  const reader=new HTMLRewriter().on(selector,{element(e){
    const candidate=e.getAttribute(field);
    if(id==="therarbag"){
      const normalized=normalizedTheRarBgMagnetHref(candidate);
      if(normalized)magnet=normalized;
    }else if(candidate&&candidate.startsWith("magnet:?")&&candidate.length<=12000){
      magnet=candidate;
    }
  }});
  await reader.transform(new Response(html,{headers:{"content-type":"text/html"}})).text();
  if(id==="therarbag"&&diagnostic)diagnostic.htmlStage=magnet?"HTML_ANCHOR_VALID":"HTML_NO_ANCHOR";
  // Strict single-provider fallback; successful detail HTML was fetched via
  // its fixed-origin allowlisted URL with anti-bot and size guards above.
  if(!magnet&&id==="therarbag"){
    magnet=magnetFromTheRarBgSourceMetadata(html);
    if(magnet&&diagnostic)diagnostic.htmlStage="HTML_METADATA_VALID";
  }
  if(!magnet&&id==="therarbag"){
    if(diagnostic)diagnostic.htmlStage="HTML_NO_BTIH";
    magnet=await theRarBgOriginalJsonHash(safe,html,fetcher,diagnostic);
  }
  if(!magnet)throw Error("provider details page contains no supported magnet link");
  return {magnet};
}
