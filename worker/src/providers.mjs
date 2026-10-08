import {LEGACY_SPECS} from "./legacy-specs.mjs";
import {legacySearch,validateLegacyDetail} from "./legacy-adapters.mjs";
import {HTML_PROVIDER_SPECS,runHtmlAdapter} from "./html-adapters.mjs";
// Source-specific ports of the upstream Kotlin provider contracts.
// These adapters intentionally use fixed endpoints, never a user-selected proxy URL.
const MAX_RESULTS = 100;
const REQUEST_TIMEOUT_MS = 11000;
const KNABEN_CATEGORIES = { music:1000000,series:2000000,movies:3000000,apps:4000000,porn:5000000,anime:6000000,games:7000000,books:9000000,other:10000000 };

function clean(value) { return String(value ?? "").trim(); }
function numeric(value) { if(value===null||value===undefined||String(value).trim()==="")return null; const n=Number(String(value).trim().replace(/,/g,"")); return Number.isFinite(n)&&n>=0 ? Math.floor(n) : null; }
function bytes(value) {
  const n=Number(value);
  if (!Number.isFinite(n)||n<0) return null;
  if (!n) return "0 B";
  const u=["B","KB","MB","GB","TB","PB"],i=Math.min(u.length-1,Math.floor(Math.log(n)/Math.log(1024)));
  return (n/1024**i).toFixed(i===0?0:2).replace(/\.00$/,"")+" "+u[i];
}
export function magnetFromHash(hash) {
  const h=clean(hash);
  // infohashes can be 40-character hex (v1) or 32-character base32 (v1).
  return /^(?:[0-9a-f]{40}|[a-z2-7]{32})$/i.test(h) ? "magnet:?xt=urn:btih:"+h.toLowerCase() : null;
}
function normalize(item,provider) {
  if (!item || !clean(item.name)) return null;
  const magnet=clean(item.magnet);
  if (magnet && (!magnet.toLowerCase().startsWith("magnet:?") || magnet.length > 12000)) return null;
  const details=clean(item.details),torrentFile=clean(item.torrentFile),source=clean(item.magnetSource);
  const allowedDetails=provider in LEGACY_SPECS ? validateLegacyDetail(provider,details) : /^https:\/\//.test(details)?details:null;
  const allowedSource=provider in LEGACY_SPECS ? validateLegacyDetail(provider,source) : null;
  if (!magnet && !allowedDetails && !allowedSource) return null;
  return {
    id:provider+":"+(clean(item.id)||magnet.slice(0,180)),
    provider,name:clean(item.name).slice(0,600),
    size: clean(item.size)||null,
    seeders:numeric(item.seeders),peers:numeric(item.peers),
    date:clean(item.date)||null,category:clean(item.category)||"all",
    magnet:magnet||null,details:allowedDetails,magnetSource:allowedSource,
    torrentFile:/^https:\/\//.test(torrentFile)?torrentFile:null
  };
}
const parsed=(xs,id)=>xs.map(x=>normalize(x,id)).filter(Boolean).slice(0,MAX_RESULTS);
async function requestJson(url, options={}, fetcher=fetch) {
  const response=await fetcher(url,{
    ...options,redirect:"follow",
    signal:AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    headers:{"accept":"application/json",...(options.headers||{})}
  });
  if(!response.ok)throw Error("provider HTTP "+response.status);
  const length=Number(response.headers.get("content-length")||0);
  if(length>4_000_000)throw Error("provider response too large");
  const text=await response.text();
  if(text.length>4_000_000)throw Error("provider response too large");
  return JSON.parse(text);
}
async function requestHtml(url,fetcher=fetch) {
  const response=await fetcher(url,{signal:AbortSignal.timeout(REQUEST_TIMEOUT_MS),headers:{"accept":"text/html"}});
  if(!response.ok)throw Error("provider HTTP "+response.status);
  const body=await response.text();
  if(body.length>3_000_000)throw Error("provider response too large");
  if(/cf-mitigated|Just a moment|Checking your browser/i.test(body.slice(0,1200)))throw Error("provider challenge requires browser verification");
  return body;
}
function catFromKnaben(values) {
  const n=Math.min(...(Array.isArray(values)?values:[]).map(Number).filter(Number.isFinite));
  return Object.entries(KNABEN_CATEGORIES).find(([,num])=>n>=num&&n<num+1000000)?.[0]||"all";
}
export const adapters=Object.freeze({
  ...Object.fromEntries(Object.keys(LEGACY_SPECS).map(id=>[id,async(q,category,fetcher)=>parsed(await legacySearch(id,q,category,fetcher),id)])),
  ...Object.fromEntries(Object.keys(HTML_PROVIDER_SPECS).map(id=>[id,async(q,category,fetcher)=>parsed(await runHtmlAdapter(id,q,category,fetcher),id)])),
  async anilibria(q,_category,fetcher) {
    const base="https://anilibria.top/api/v1";
    const releases=await requestJson(base+"/app/search/releases?query="+encodeURIComponent(q),{},fetcher);
    if(!Array.isArray(releases))throw Error("unexpected AniLibria releases payload");
    const ids=releases.slice(0,15).map(x=>Number(x.id)).filter(x=>Number.isSafeInteger(x)&&x>0);
    const items=[];
    for(let i=0;i<ids.length;i+=3) {
      const fetched=await Promise.all(ids.slice(i,i+3).map(async id=>{
        const d=await requestJson(base+"/anime/torrents/release/"+id,{},fetcher);
        return Array.isArray(d)?d:[];
      }));
      for(const releasesTorrents of fetched) {
        for(const x of releasesTorrents) {
          const name=x.label||x.release?.name?.english||x.release?.name?.main;
          const alias=x.release?.alias;
          items.push({id:x.id||x.hash,name,magnet:x.magnet||magnetFromHash(x.hash),
            size:bytes(x.size),seeders:x.seeders,peers:x.leechers,date:x.created_at,category:"anime",
            details:alias?"https://www.anilibria.top/anime/releases/release/"+encodeURIComponent(alias):null
          });
        }
      }
    }
    return parsed(items,"anilibria");
  },
  async knaben(q,category,fetcher) {
    const body={query:q,size:100,order_by:"seeders",order_direction:"desc",hide_unsafe:true,hide_xxx:category!=="porn"};
    if(KNABEN_CATEGORIES[category])body.categories=[KNABEN_CATEGORIES[category]];
    const d=await requestJson("https://api.knaben.org/v1",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)},fetcher);
    return parsed((d.hits||[]).map(x=>({id:x.id,name:x.title,magnet:x.magnetUrl,size:bytes(x.bytes),seeders:x.seeders,peers:x.peers,date:x.date,details:x.details,category:catFromKnaben(x.categoryId)})),"knaben");
  },
  async torrentscsv(q,_category,fetcher) {
    const d=await requestJson("https://torrents-csv.com/service/search?q="+encodeURIComponent(q),{},fetcher);
    return parsed((d.torrents||[]).map(x=>({id:x.id,name:x.name,magnet:magnetFromHash(x.infohash),size:bytes(x.size_bytes),seeders:x.seeders,peers:x.leechers,date:x.created_unix?new Date(Number(x.created_unix)*1000).toISOString():null,category:"other"})),"torrentscsv");
  },
  async thepiratebay(q,category,fetcher) {
    const t={apps:300,books:601,games:400,movies:200,series:200,music:101,porn:500,other:600};
    const d=await requestJson("https://apibay.org/q.php?q="+encodeURIComponent(q)+"&cat="+(t[category]||0),{},fetcher);
    if(!Array.isArray(d))throw Error("unexpected TPB response shape");
    return parsed(d.filter(x=>x.name!=="No results returned").map(x=>({id:x.id,name:x.name,magnet:magnetFromHash(x.info_hash),size:bytes(x.size),seeders:x.seeders,peers:x.leechers,date:x.added?new Date(Number(x.added)*1000).toISOString():null,details:"https://thepiratebay.org/description.php?id="+encodeURIComponent(x.id)})),"thepiratebay");
  },
  async ytsmx(q,_category,fetcher) {
    const d=await requestJson("https://movies-api.accel.li/api/v2/list_movies.json?query_term="+encodeURIComponent(q)+"&limit=50",{},fetcher);
    const movies=d?.data?.movies||[];
    return parsed(movies.flatMap(m=>(m.torrents||[]).map(x=>({
      id:x.hash,name:[m.title_long||m.title,x.quality,x.type,x.video_codec].filter(Boolean).join(" • "),
      magnet:magnetFromHash(x.hash),size:x.size||bytes(x.size_bytes),
      seeders:x.seeds,peers:x.peers,date:x.date_uploaded,category:"movies",
      details:m.url,torrentFile:x.url
    }))),"ytsmx");
  },
  async internetarchive(q,category,fetcher) {
    const cat={apps:"software",books:"texts",movies:"movies"};
    const filter=cat[category]?" AND mediatype:("+cat[category]+")":"";
    const u=new URL("https://archive.org/advancedsearch.php");
    u.searchParams.set("q","title:("+q+")"+filter);
    u.searchParams.set("fl[]","title,item_size,publicdate,mediatype,identifier,btih");
    u.searchParams.set("rows","100");u.searchParams.set("page","1");u.searchParams.set("output","json");
    const d=await requestJson(u.toString(),{},fetcher);
    return parsed((d?.response?.docs||[]).map(x=>({
      id:x.identifier,name:x.title,magnet:magnetFromHash(x.btih),
      size:bytes(x.item_size),date:x.publicdate,category:x.mediatype,
      details:x.identifier?"https://archive.org/details/"+encodeURIComponent(x.identifier):null,
      torrentFile:x.identifier?"https://archive.org/download/"+encodeURIComponent(x.identifier)+"/"+encodeURIComponent(x.identifier)+"_archive.torrent":null
    })),"internetarchive");
  },
  async bangumimoe(q,_category,fetcher) {
    const d=await requestJson("https://bangumi.moe/api/v2/torrent/search",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({query:q})},fetcher);
    return parsed((d.torrents||[]).map(x=>({
      id:x._id,name:x.title,magnet:x.magnet,size:x.size,
      seeders:x.seeders,peers:x.leechers,date:x.publish_time,category:"anime",
      details:x._id?"https://bangumi.moe/torrent/"+encodeURIComponent(x._id):null
    })),"bangumimoe");
  },
  async subsplease(q,_category,fetcher) {
    const u=new URL("https://subsplease.org/api/");
    u.searchParams.set("f","search");u.searchParams.set("tz","");u.searchParams.set("s",q);
    const d=await requestJson(u.toString(),{},fetcher);
    const items=(!d||Array.isArray(d))?[]:Object.entries(d).flatMap(([name,ep])=>
      (ep?.downloads||[]).map(x=>({name:name+" ["+x.res+"p]",id:name+":"+x.res,magnet:x.magnet,
      torrentFile:x.torrent,date:ep.release_date,category:"anime",
      details:ep.page?"https://subsplease.org/"+String(ep.page).replace(/^\//,""):null}))
    );
    return parsed(items,"subsplease");
  },
  async btsow(q,_category,fetcher) {
    const d=await requestJson("https://btsow.live/bts/data/api/search",{
      method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify([{search:q},30,1])
    },fetcher);
    return parsed((d.data||[]).map(x=>({
      id:x.hash,name:String(x.name||"").replace(/<\/?em>/g,""),
      magnet:magnetFromHash(x.hash),size:bytes(x.size),
      details:x.hash?"https://btsow.live/magnet/detail/"+encodeURIComponent(x.hash):null
    })),"btsow");
  },
  async nyaasi(q,category,fetcher) { return searchNyaa("https://nyaa.si",q,category,"nyaasi",fetcher); },
  async sukebeinyaa(q,category,fetcher) { return searchNyaa("https://sukebei.nyaa.si",q,category,"sukebeinyaa",fetcher); }
});
async function searchNyaa(host,q,category,id,fetcher) {
  const cats={anime:"1_2",music:"2_0",books:"3_0",series:"4_0",apps:"6_0",games:"6_2"};
  const u=host+"/?f=0&c="+(id==="sukebeinyaa"?"0_0":cats[category]||"0_0")+"&q="+encodeURIComponent(q);
  const html=await requestHtml(u,fetcher);
  if(typeof HTMLRewriter==="undefined")throw Error("HTMLRewriter requires Cloudflare Workers runtime");
  const rows=[];let index=-1;
  const rewriter=new HTMLRewriter()
    .on("table.torrent-list > tbody > tr",{element(){index++;rows[index]={};}})
    .on("table.torrent-list > tbody > tr td:nth-child(2) a:not(.comments)",{
      element(e){rows[index].details=e.getAttribute("href")?new URL(e.getAttribute("href"),host).toString():null;},
      text(t){rows[index].name=(rows[index].name||"")+t.text;}
    })
    .on('table.torrent-list > tbody > tr td:nth-child(3) a[href^="magnet:"]',{
      element(e){rows[index].magnet=e.getAttribute("href");}
    })
    .on("table.torrent-list > tbody > tr td:nth-child(3) a[href^='/download']",{
      element(e){rows[index].torrentFile=new URL(e.getAttribute("href"),host).toString();}
    })
    .on("table.torrent-list > tbody > tr td:nth-child(4)",{text(t){rows[index].size=(rows[index].size||"")+t.text;}})
    .on("table.torrent-list > tbody > tr td:nth-child(5)",{element(e){const unix=e.getAttribute("data-timestamp");if(unix)rows[index].date=new Date(Number(unix)*1000).toISOString();}})
    .on("table.torrent-list > tbody > tr td:nth-child(6)",{text(t){rows[index].seeders=(rows[index].seeders||"")+t.text;}})
    .on("table.torrent-list > tbody > tr td:nth-child(7)",{text(t){rows[index].peers=(rows[index].peers||"")+t.text;}});
  await rewriter.transform(new Response(html,{headers:{"content-type":"text/html"}})).text();
  return parsed(rows,id);
}
export function hasAdapter(id) { return Object.prototype.hasOwnProperty.call(adapters,id); }
export async function searchProvider(id,q,category="all",fetcher=fetch) {
  if(!hasAdapter(id))throw Error("provider not ported yet: "+id);
  if(typeof q!=="string"||q.trim().length<2||q.length>180)throw Error("query must be 2–180 characters");
  return adapters[id](q.trim(),category,fetcher);
}
