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
   // Real-source HTML may put individual fields directly under the
   // result root instead of under an extra wrapper div. Both forms must
   // preserve the one-title/one-magnet association in actual workerd.
   const direct=sample.replace('<div class="one_result"><div>','<div class="one_result">')
     .replace('</div></div>','</div>');
   const unwrapped=await runHtmlAdapter("btdigg","ubuntu","all",async()=>new Response(direct,{
     headers:{"content-type":"text/html"}
   }));
   if(unwrapped.length!==1||unwrapped[0].name!=="Ubuntu ISO fixture"||
      unwrapped[0].magnet!==fullMagnet||unwrapped[0].size!=="1.2 GB")
     invalid.push({id:"btdigg-unwrapped-fixture",error:"direct-sibling BTDigg result split or dropped"});
  }catch(e){invalid.push({id:"btdigg-fixture",error:String(e).slice(0,250)});}
  // Real Cloudflare workerd contract: href="...&amp;dn=..." must become
  // a usable magnet "&dn=..." for an original TheRarBg detail. This catches
  // the concrete fake-HTMLRewriter blind spot; no external fetch is made.
  try{
   const hash="a".repeat(40);
   const url="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
   const expected="magnet:?xt=urn:btih:"+hash+"&dn=Synthetic";
   const html="<html><body><table><tr><th>Torrent:</th><td>"+
     "<a href='"+expected.replaceAll("&","&amp;")+"'>Magnet Download</a>"+
     "<div>Info Hash: "+hash+"</div></td></tr></table></body></html>";
   let calls=0;
   const result=await resolveLegacy("therarbag",url,async(target,opts)=>{
    calls++;if(target!==url||opts.redirect!=="manual")throw Error("invalid fixture transport");
    return new Response(html,{status:200,headers:{"content-type":"text/html"}});
   });
   if(calls!==1||result.magnet!==expected)
    invalid.push({id:"therarbag-workerd-magnet-fixture",error:"HTML entity magnet normalization not verified"});
  }catch{
   invalid.push({id:"therarbag-workerd-magnet-fixture",error:"Cloudflare source fixture exception"});
  }
  // Real workerd regression for source-owned JSON fallback, with a local
  // transport fixture and no network. The HTTP 200 source HTML lacks BTIH;
  // the matching exact detail ?format=json supplies the owner's infohash.
  try{
   const hash="a".repeat(40);
   const original="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
   const json=original+"?format=json";
   const observed=[];
   const trace={htmlStage:"HTML_NOT_FETCHED",jsonStage:"JSON_NOT_STARTED"};
   const result=await resolveLegacy("therarbag",original,async(url,options)=>{
     observed.push(url);
     if(options.redirect!=="manual")throw Error("fixture redirect policy changed");
     if(url===original)return new Response(
       "<html><main><p>Magnet Download</p></main></html>",
       {status:200,headers:{"content-type":"text/html"}});
     if(url===json)return new Response(JSON.stringify({info_hash:hash}),
       {status:200,headers:{"content-type":"application/json"}});
     throw Error("unexpected source request");
   },trace);
   if(trace.htmlStage!=="HTML_NO_BTIH"||trace.jsonStage!=="JSON_VALID")
     invalid.push({id:"therarbag-runtime-stage-fixture",error:"workerd finite source trace does not match"});
   if(result.magnet!=="magnet:?xt=urn:btih:"+hash||
       JSON.stringify(observed)!==JSON.stringify([original,json])){
     invalid.push({id:"therarbag-official-json-runtime",error:"incorrect same-detail JSON resolution"});
   }
  }catch{
   invalid.push({id:"therarbag-official-json-runtime",error:"workerd JSON fallback exception"});
  }
  return new Response(JSON.stringify({ok:invalid.length===0,checked:verified.length+invalid.length,verified,invalid}),{
    status:invalid.length?500:200,headers:{"content-type":"application/json"}
  });
 }
};
