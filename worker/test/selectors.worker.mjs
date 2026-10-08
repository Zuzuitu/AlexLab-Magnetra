import {LEGACY_SPECS} from "../src/legacy-specs.mjs";
import {HTML_PROVIDER_SPECS,runHtmlAdapter} from "../src/html-adapters.mjs";

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
   const sample='<div class="one_result"><div>'+
     '<div class="torrent_name"><a href="/torrent/'+hash+'">Ubuntu ISO fixture</a></div>'+
     '<div class="torrent_magnet"><div class="fa-magnet"><a href="'+magnet+'">Magnet</a></div></div>'+
     '<span class="torrent_size">1.2 GB</span><span class="torrent_age">found 2 days ago</span>'+
     '</div></div>';
   const rows=await runHtmlAdapter("btdigg","ubuntu","all",async(url,opts)=>{
    if(url!=="https://btdig.com/search?q=ubuntu"||opts.redirect!=="manual")
     throw Error("unexpected BTDigg fixture request");
    return new Response(sample,{headers:{"content-type":"text/html"}});
   });
   if(rows.length!==1||rows[0].name!=="Ubuntu ISO fixture"||rows[0].magnet!==magnet||
      rows[0].size!=="1.2 GB"||rows[0].details!=="https://btdig.com/torrent/"+hash||
      rows[0].seeders!==null||rows[0].peers!==null)
    invalid.push({id:"btdigg-fixture",error:"HTMLRewriter extracted incorrect BTDigg fields"});
  }catch(e){invalid.push({id:"btdigg-fixture",error:String(e).slice(0,250)});}
  return new Response(JSON.stringify({ok:invalid.length===0,checked:verified.length+invalid.length,verified,invalid}),{
    status:invalid.length?500:200,headers:{"content-type":"application/json"}
  });
 }
};
