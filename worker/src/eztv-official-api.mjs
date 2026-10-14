// Original EZTV data only. TVmaze is used solely to map an exact TV-series
// name to an IMDb show ID; it never supplies torrents or synthetic results.
// Both APIs are free, HTTPS and fixed-origin. No retries, caches or proxying.
// TVmaze metadata: https://www.tvmaze.com/api (CC BY-SA; PWA credits TVmaze).
import {SOURCE_HEADERS,fetchProviderSameOrigin} from "./request-headers.mjs";

const EZTV_API="https://eztvx.to/api/get-torrents";
const TVMAZE_SEARCH="https://api.tvmaze.com/search/shows";
const MAX_JSON=1_000_000;
const MAX_ITEMS=100;

function normalizedTitle(text){
 return String(text||"").normalize("NFKC").toLowerCase()
  .replace(/[^a-z0-9]+/g," ").trim().replace(/\s+/g," ");
}
function imdbDigits(text){
 const match=/^tt(\d{5,12})$/i.exec(String(text||"").trim());
 return match ? String(BigInt(match[1])) : null;
}
async function getJson(url,fetcher){
 const origin=new URL(url);
 if(![new URL(EZTV_API).origin,new URL(TVMAZE_SEARCH).origin].includes(origin.origin))
  throw Error("EZTV metadata origin not allowed");
 const res=await fetchProviderSameOrigin(url,{
  method:"GET",
  headers:{...SOURCE_HEADERS,"accept":"application/json"},
  signal:AbortSignal.timeout(9000)
 },fetcher);
 if(!res.ok)throw Error("provider HTTP "+res.status);
 if(!/application\/json/i.test(res.headers.get("content-type")||""))
  throw Error("provider returned non-JSON data");
 if(Number(res.headers.get("content-length")||0)>MAX_JSON)
  throw Error("provider JSON too large");
 const body=await res.text();
 if(body.length>MAX_JSON)throw Error("provider JSON too large");
 try{return JSON.parse(body)}catch{throw Error("provider returned malformed JSON")}
}
async function findExactShowImdb(query,fetcher){
 const data=await getJson(TVMAZE_SEARCH+"?q="+encodeURIComponent(query),fetcher);
 if(!Array.isArray(data))throw Error("TVmaze show lookup malformed");
 const key=normalizedTitle(query);
 // Never let a fuzzy match silently impersonate another series or combine
 // ambiguous remakes under the same name. Users may enter an IMDb ID instead.
 const exact=data.filter(row=>normalizedTitle(row?.show?.name)===key);
 // An exact title is not necessarily a unique series: the live TVmaze API
 // currently returns two distinct IMDb IDs for "Supernatural".
 if(exact.length>1){
  const ids=new Set(exact.map(row=>imdbDigits(row?.show?.externals?.imdb)).filter(Boolean));
  if(ids.size>1)throw Error("EZTV series title ambiguous: search by IMDb ID");
 }
 if(exact.length!==1)return null;
 return imdbDigits(exact[0]?.show?.externals?.imdb);
}
function safeHttpsUrl(url,allowedOrigin){
 if(typeof url!=="string"||url.length>1500)return null;
 try{
  const parsed=new URL(url);
  return parsed.protocol==="https:" && parsed.origin===allowedOrigin &&
    !parsed.username && !parsed.password && !parsed.hash?parsed.href:null;
 }catch{return null;}
}
function sourceMagnet(row){
 const magnet=typeof row.magnet_url==="string"?row.magnet_url:"";
 if(/^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)/i.test(magnet)&&
    magnet.length<=12000)return magnet;
 const hash=String(row.hash||"");
 return /^(?:[a-f0-9]{40}|[a-z2-7]{32})$/i.test(hash)
  ?"magnet:?xt=urn:btih:"+hash.toLowerCase():null;
}

export async function searchEZTVOfficial(query,category="all",fetcher=fetch){
 // EZTV is exclusively TV-series releases. Do not use it for movies, books,
 // apps or other categories and misrepresent unrelated API releases.
 if(!["all","series"].includes(category))return [];
 const imdb=imdbDigits(query)||await findExactShowImdb(query,fetcher);
 if(!imdb)return [];
 const url=EZTV_API+"?imdb_id="+encodeURIComponent(imdb)+"&limit=100&page=1";
 const data=await getJson(url,fetcher);
 if(!data||typeof data!=="object"||Array.isArray(data))
  throw Error("EZTV API shape unexpected");
 if(Object.hasOwn(data,"error")||Object.hasOwn(data,"errors"))
  throw Error("EZTV API reported an error");
 // EZTV can return recent releases if no IMDb match. Never attribute them
 // to a searched series; require the response's explicit exact IMDb ID.
 const returned=String(data.imdb_id??"").replace(/^tt/i,"");
 if(!/^\d+$/.test(returned)||BigInt(returned)!==BigInt(imdb))return [];
 // Actual Rock64 API response (2026-10-14): a confirmed zero-hit search
 // has no "torrents" field, but does include torrents_count. Treat only an
 // explicit zero as empty; do not mask malformed/blocked/unexpected payloads.
 if(!Object.hasOwn(data,"torrents") &&
    (data.torrents_count===0||data.torrents_count==="0"))return [];
 if(!Array.isArray(data.torrents))throw Error("EZTV API shape unexpected");
 const results=[];
 for(const row of data.torrents.slice(0,MAX_ITEMS)){
  if(!row||typeof row!=="object")continue;
  const name=String(row.title||row.filename||"").trim();
  const magnet=sourceMagnet(row);
  if(!name||!magnet)continue;
  let date=null;
  const seconds=Number(row.date_released_unix);
  if(Number.isSafeInteger(seconds)&&seconds>0&&seconds<4102444800)
   date=new Date(seconds*1000).toISOString();
  const bytes=Number(row.size_bytes);
  const size=Number.isFinite(bytes)&&bytes>=0?bytes:null;
  results.push({
   id:String(row.id||row.hash||results.length),
   name,magnet,sizeBytes:size,seeders:row.seeds,
   peers:row.peers,date,category:"series",
   // Episode URLs from EZTV's JSON can be on different domains. Never
   // forward off-origin links just because the API supplied them.
   details:safeHttpsUrl(row.episode_url,new URL(EZTV_API).origin)
  });
 }
 return results;
}
