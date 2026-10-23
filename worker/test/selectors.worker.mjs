import {LEGACY_SPECS} from "../src/legacy-specs.mjs";
import {HTML_PROVIDER_SPECS,runHtmlAdapter} from "../src/html-adapters.mjs";
import {resolveLegacy} from "../src/legacy-adapters.mjs";

/** CI-only workerd endpoint: validates actual Cloudflare HTMLRewriter syntax. */
export default {
 async fetch(){
  const invalid=[],verified=[];
  const text="<html><body><table><tbody><tr><td>Example</td></tr></tbody></table></body></html>";
  for(const [id,spec] of Object.entries({...HTML_PROVIDER_SPECS,...LEGACY_SPECS})){
   const elements=spec.rows.split(/\s*,\s*/);
   const fields=["name","size","seeders","peers","date","details","magnet","torrentFile","magnetSource","magnetHashLink","swarm"];
   const selectors=[spec.rows,...fields.filter(key=>spec[key]).map(key=>spec.rows+" "+spec[key])];
   try{
    let rewriter=new HTMLRewriter();
    for(const selector of selectors)rewriter=rewriter.on(selector,{element(){},text(){}});
    await rewriter.transform(new Response(text,{headers:{"content-type":"text/html"}})).text();
    verified.push(id);
   }catch(e){invalid.push({id,error:String(e).slice(0,250)});}
  }
  // Behavioral fixture, not just selector syntax: verify BTDigg's real row shape
  // in workerd. This test does not access the rate-limited external website.
  try{
   const hash="0123456789abcdef0123456789abcdef01234567";
   const magnet="magnet:?xt=urn:btih:"+hash;
   // Reproduce the HTML attribute &amp; separators observed in real BTDigg JSON.
   // The BTDigg adapter must produce actual magnet URL parameter delimiters.
   const fullMagnet=magnet+"&dn=Ubuntu+ISO&tr=udp%3A%2F%2Ftracker.example%3A80";
   const htmlMagnet=fullMagnet.replaceAll("&","&amp;");
   const sample='<div class="one_result"><div>'+
     '<div class="torrent_name"><a href="/torrent/'+hash+'">Ubuntu ISO fixture</a></div>'+
     '<div class="torrent_magnet"><div class="fa-magnet"><a href="'+htmlMagnet+'">Magnet</a></div></div>'+
     '<span class="torrent_size">1.2 GB</span><span class="torrent_age">found 2 days ago</span>'+
     '</div></div>';
   const rows=await runHtmlAdapter("btdigg","ubuntu","all",async(url,opts)=>{
    if(url!=="https://btdig.com/search?q=ubuntu"||opts.redirect!=="manual")
     throw Error("unexpected BTDigg fixture request");
    return new Response(sample,{headers:{"content-type":"text/html"}});
   });
   if(rows.length!==1||rows[0].name!=="Ubuntu ISO fixture"||rows[0].magnet!==fullMagnet||
      rows[0].size!=="1.2 GB"||rows[0].details!=="https://btdig.com/torrent/"+hash||
      rows[0].seeders!==null||rows[0].peers!==null)
    invalid.push({id:"btdigg-fixture",error:"HTMLRewriter extracted incorrect BTDigg fields",extractedMagnet:rows[0]?.magnet||null});
  }catch(e){invalid.push({id:"btdigg-fixture",error:String(e).slice(0,250)});}
  // True workerd behavioral regression: prior Node tests used a stub for
  // HTMLRewriter. This fixture exercises the actual Cloudflare parser and
  // the same exact original details route as the reported iPhone failure.
  // No remote provider request, torrent download or real infohash.
  try{
   const hash="a".repeat(40);
   const detail="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
   const expected="magnet:?xt=urn:btih:"+hash+"&dn=Synthetic";
   const html="<html><body><table><tr><th>Torrent:</th><td>"+
     "<a href='"+expected.replaceAll("&","&amp;")+"'>Magnet Download</a>"+
     "<a href='https://example.invalid/fictional.torrent'>.torrent File</a>"+
     "<button>Copy Magnet</button><div>Info Hash: "+hash+"</div>"+
     "</td></tr></table></body></html>";
   let sourceCalls=0;
   const source=async(url,options)=>{
    sourceCalls++;
    if(url!==detail||options.redirect!=="manual")throw Error("unexpected fixture request");
    return new Response(html,{status:200,headers:{"content-type":"text/html"}});
   };
   const direct=await resolveLegacy("therarbag",detail,source);
   if(direct.magnet!==expected||sourceCalls!==1)
    invalid.push({id:"therarbag-workerd-magnet-fixture",error:"Original magnet anchor not extracted"});
   const noAnchor="<html><main><p>Info Hash: "+hash+"</p></main></html>";
   const fallback=await resolveLegacy("therarbag",detail,async()=>new Response(noAnchor,{status:200,headers:{"content-type":"text/html"}}));
   if(fallback.magnet!=="magnet:?xt=urn:btih:"+hash)
    invalid.push({id:"therarbag-workerd-hash-fixture",error:"Source label fallback not extracted"});
  }catch{
   invalid.push({id:"therarbag-workerd-real-parser",error:"Cloudflare HTMLRewriter fixture failed"});
  }
  return new Response(JSON.stringify({ok:invalid.length===0,checked:verified.length+invalid.length,verified,invalid}),{
    status:invalid.length?500:200,headers:{"content-type":"application/json"}
  });
 }
};
