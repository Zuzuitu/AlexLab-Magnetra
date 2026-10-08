import {LEGACY_SPECS,legacySearchUrl} from "./legacy-specs.mjs";

const MAX_HTML = 3_000_000;
const TIMEOUT = 11_000;
function allowedExternal(url,host) {
  try {
    const u=new URL(url,host);
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
  const res=await fetcher(url,{
    ...options,redirect:"manual",
    signal:AbortSignal.timeout(TIMEOUT),
    headers:{"accept":"text/html,application/xhtml+xml",...(options.headers||{})}
  });
  if(res.status>=300&&res.status<400)throw Error("provider redirected request; explicit verification needed");
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
    const details=allowedExternal(row.details,spec.host);
    const magnetSource=allowedExternal(row.magnetSource,spec.host);
    const hash=fromHashUrl(row.details,spec.hashFromDetailsSuffix?"filemood":spec.magnetHashLink?"torrentdatabase":null);
    let magnet=String(row.magnet||"").trim();
    if(!magnet.startsWith("magnet:?"))magnet=hash||"";
    if(!magnet&&spec.magnetHashLink)magnet=fromHashUrl(row.magnetHashLink,"torrentdatabase")||"";
    const torrentFile=allowedExternal(row.torrentFile,spec.host);
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
  if(!magnet)throw Error("provider details page contains no supported magnet link");
  return {magnet};
}
