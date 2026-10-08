import {LEGACY_SPECS} from "../src/legacy-specs.mjs";
import {HTML_PROVIDER_SPECS} from "../src/html-adapters.mjs";

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
  return new Response(JSON.stringify({ok:invalid.length===0,checked:verified.length+invalid.length,verified,invalid}),{
    status:invalid.length?500:200,headers:{"content-type":"application/json"}
  });
 }
};
