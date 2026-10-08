import {SOURCE_HEADERS} from "./request-headers.mjs";
/**
 * HTML providers ported from Android Jsoup source selectors. Every provider has
 * explicit fixed URL construction, row selectors and field selectors. No
 * caller-controlled target URL is ever fetched. HTMLRewriter requires the
 * Cloudflare Workers runtime (not a generic browser DOM).
 *
 * Provider availability remains external: if Cloudflare challenges / upstream
 * layout changes break an adapter, fail explicitly rather than invent results.
 */
export const HTML_PROVIDER_SPECS = Object.freeze({
  btdigg: {
    host:"https://btdig.com",
    search:q=>"https://btdig.com/search?q="+encodeURIComponent(q),
    rows:"div.one_result > div",
    name:"div.torrent_name > a",
    magnet:"div.torrent_magnet > div.fa-magnet > a",
    size:"span.torrent_size",date:"span.torrent_age",
    details:"div.torrent_name > a",
  },
  dmhy: {
    host:"https://share.dmhy.org",
    search:q=>"https://share.dmhy.org/topics/list?keyword="+encodeURIComponent(q)+"&sort_id=0&team_id=0&order=date-desc",
    rows:"table#topic_list > tbody > tr",
    name:"td.title > a",
    magnet:'td:nth-child(4) > a[href^="magnet:?xt="]',
    size:"td:nth-child(5)",seeders:"td:nth-child(6)",
    peers:"td:nth-child(7)",date:"td:nth-child(1) > span",
    details:"td.title > a"
  },
  nekobt:{
    host:"https://nekobt.to",
    search:q=>"https://nekobt.to/search?query="+encodeURIComponent(q),
    rows:"table.table > tbody > tr",
    name:"td:nth-child(3) > div:nth-child(1) > div > a",
    magnet:"td:nth-child(4) > div > a:nth-child(1)",
    torrentFile:"td:nth-child(4) > div > a:nth-child(2)",
    size:"td:nth-child(5) > span",date:"td:nth-child(6) > span",
    seeders:"td:nth-child(7) > span",peers:"td:nth-child(8) > span",
    details:"td:nth-child(3) > div:nth-child(1) > div > a"
  },
  mikanproject:{
    host:"https://mikanani.me",
    search:q=>"https://mikanani.me/Home/Search?searchstr="+encodeURIComponent(q),
    rows:"tr.js-search-results-row",
    name:"td:nth-child(2) > a:nth-child(1)",
    magnet:"td:nth-child(2) > a[data-clipboard-text]",
    magnetAttribute:"data-clipboard-text",
    size:"td:nth-child(3)",date:"td:nth-child(4)",
    torrentFile:"td:nth-child(5) > a",
    details:"td:nth-child(2) > a:nth-child(1)"
  },
  torrentkitty:{
    host:"https://torrentkitty.tv",
    search:q=>"https://torrentkitty.tv/search/"+encodeURIComponent(q),
    rows:"table#archiveResult > tbody > tr",
    name:"td.name",
    magnet:"td.action > a:nth-child(2)",
    torrentFile:"td.action > a:nth-child(3)",
    details:"td.action > a:nth-child(1)",
    size:"td.size",date:"td.date"
  },
  rutorinfo:{
    host:"https://rutor.info",
    search:q=>"https://rutor.info/search/0/0/010/2/"+encodeURIComponent(q),
    rows:"div#index > table > tbody > tr",
    name:"td:nth-child(2) > a:nth-child(3)",
    magnet:"td:nth-child(2) > a:nth-child(2)",
    torrentFile:"td:nth-child(2) > a:nth-child(1)",
    details:"td:nth-child(2) > a:nth-child(3)",
    size:"td:nth-child(3)",
    seeders:"td:nth-child(4) > span:nth-child(1)",
    peers:"td:nth-child(4) > span:nth-child(3)",
    date:"td:nth-child(1)"
  },
  xxxtracker:{
    host:"https://xxxtor.com",
    search:q=>"https://xxxtor.com/b.php?search="+encodeURIComponent(q),
    rows:"table > tbody > tr",
    name:"td:nth-child(2) > a:nth-child(3)",
    magnet:"td:nth-child(2) > a:nth-child(1)",
    torrentFile:"td:nth-child(2) > a:nth-child(2)",
    details:"td:nth-child(2) > a:nth-child(3)",
    size:"td:nth-child(3)",seeders:"td:nth-child(4) > span.green",
    peers:"td:nth-child(4) > span.red",date:"td:nth-child(1)"
  },
  animetosho:{
    host:"https://animetosho.org",
    search:q=>"https://animetosho.org/search?q="+encodeURIComponent(q),
    rows:"div.home_list_entry",
    name:"div.link > a",details:"div.link > a",
    magnet:'div.links a[href^="magnet:"]',
    torrentFile:"div.links a.dllink",
    size:"div.size"
  },
  limetorrents:{
    host:"https://limetorrents.fun",
    search:q=>"https://limetorrents.fun/search/all/"+encodeURIComponent(q)+"/date/1/",
    rows:".table2 > tbody > tr",
    name:"td:nth-child(1) > div.tt-name > a:nth-child(2)",
    torrentFile:"td:nth-child(1) > div.tt-name > a:nth-child(1)",
    details:"td:nth-child(1) > div.tt-name > a:nth-child(2)",
    hashFromFile:true,
    size:"td:nth-child(3)",seeders:"td.tdseed",peers:"td.tdleech",
    date:"td:nth-child(2)"
  },
  torrentdownloadinfo:{
    host:"https://torrentdownload.info",
    search:q=>"https://torrentdownload.info/search?q="+encodeURIComponent(q),
    rows:"table.table2 > tbody > tr",
    name:"td:nth-child(1) > div.tt-name > a",
    details:"td:nth-child(1) > div.tt-name > a",
    hashFromDetails:true,
    size:"td:nth-child(3)",seeders:"td:nth-child(4)",
    peers:"td:nth-child(5)",date:"td:nth-child(2)"
  }
});
function fromHash(hash) {
 return /^(?:[a-f0-9]{40}|[a-z2-7]{32})$/i.test(hash||"")?"magnet:?xt=urn:btih:"+hash.toLowerCase():null;
}
function normalizeUrl(link,host) {
 if(!link)return null;
 try{
  const u=new URL(link,host);
  return u.protocol==="https:"?u.toString():null;
 } catch {return null;}
}
function extractHashFromTorrentUrl(link) {
 if(!link)return null;
 const result=link.match(/\/torrent\/([a-zA-Z0-9]{32,40})\.torrent/i);
 return result?result[1]:null;
}
function extractHashFromDetailsUrl(link) {
 if(!link)return null;
 const url=link.replace(/\/+$/,"");
 const parts=url.split("/");
 return parts.find(p=>/^[a-f0-9]{40}$/i.test(p))||null;
}
function collectHtml(html,spec){
 if(typeof HTMLRewriter==="undefined")throw Error("Cloudflare HTMLRewriter runtime unavailable");
 const rows=[];
 let current=-1;
 // HTMLRewriter invokes callbacks in document order. All subselectors are
 // anchored to a row, preventing cross-record field association.
 const rew=new HTMLRewriter().on(spec.rows,{
   element(){ current++; rows[current]={}; }
 });
 const callbacks=[
   ["name",spec.name,"text"],
   ["size",spec.size,"text"],
   ["seeders",spec.seeders,"text"],
   ["peers",spec.peers,"text"],
   ["date",spec.date,"text"],
   ["magnet",spec.magnet,"attribute"],
   ["torrentFile",spec.torrentFile,"attribute"],
   ["details",spec.details,"attribute"]
 ];
 for(const [field,selector,kind] of callbacks){
   if(!selector)continue;
   const full=spec.rows+" "+selector;
   if(kind==="text"){
     rew.on(full,{text(chunk){
       if(current<0||!rows[current])return;
       rows[current][field]=(rows[current][field]||"")+chunk.text;
     }});
   }else{
     rew.on(full,{element(node){
       if(current<0||!rows[current]||rows[current][field])return;
       rows[current][field]=node.getAttribute(field==="magnet"?(spec.magnetAttribute||"href"):"href")||null;
     }});
   }
 }
 return {rew,rows};
}
export async function runHtmlAdapter(id,q,category,fetcher=fetch) {
 const spec=HTML_PROVIDER_SPECS[id];
 if(!spec)throw Error("HTML provider not ported: "+id);
 const u=spec.search(q,category);
 // Never allow redirect to a user-controlled arbitrary URL.
 if(!u.startsWith(spec.host+"/")&&!u.startsWith(spec.host+"?"))throw Error("provider origin mismatch");
 const response=await fetcher(u,{
   method:"GET",headers:{...SOURCE_HEADERS,"accept":"text/html,application/xhtml+xml"},
   signal:AbortSignal.timeout(11000),redirect:"follow"
 });
 if(!response.ok)throw Error("provider HTTP "+response.status);
 if(response.headers.get("cf-mitigated")==="challenge")throw Error("provider Cloudflare challenge");
 const raw=await response.text();
 if(raw.length>3000000)throw Error("provider page too large");
 if(/<title>Just a moment|Checking your browser|Attention Required/i.test(raw.slice(0,1800)))throw Error("provider anti-bot challenge");
 const {rew,rows}=collectHtml(raw,spec);
 await rew.transform(new Response(raw,{headers:{"content-type":"text/html"}})).text();
 return rows.map((row,i)=>{
   const details=normalizeUrl(row.details,spec.host);
   const torrentFile=normalizeUrl(row.torrentFile,spec.host);
   const derivedHash=spec.hashFromFile?extractHashFromTorrentUrl(row.torrentFile):spec.hashFromDetails?extractHashFromDetailsUrl(row.details):null;
   return {
     id:derivedHash||row.details||i,
     name:(row.name||"").replace(/\s+/g," ").trim(),
     magnet:row.magnet||fromHash(derivedHash),
     size:(row.size||"").trim(),
     seeders:row.seeders?.trim().replace(/,/g,"")||null,
     peers:row.peers?.trim().replace(/,/g,"")||null,
     date:(row.date||"").trim()||null,
     torrentFile,details,category
   };
 }).filter(r=>r.name&&r.magnet?.startsWith("magnet:?")).slice(0,100);
}
