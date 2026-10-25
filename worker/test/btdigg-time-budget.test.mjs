import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {safeProviderHtml} from "../src/legacy-adapters.mjs";
test("BTDigg outer budget is 18s; original shared 11s remains for other legacy adapters",async()=>{
 const fetcher=async(url,opts)=>new Response("<html>ok</html>",{headers:{"content-type":"text/html"}});
 assert.equal(await safeProviderHtml("https://example.test",{},fetcher,18000),"<html>ok</html>");
 await assert.rejects(()=>safeProviderHtml("https://example.test",{},fetcher,18001),/Invalid bounded/);
 const source=fs.readFileSync(new URL("../src/legacy-adapters.mjs",import.meta.url),"utf8");
 assert.match(source,/const TIMEOUT = 11_000/);
 assert.match(source,/const BTDIGG_WORKER_TIMEOUT = 18_000/);
 assert.match(source,/id==="btdigg"\?BTDIGG_WORKER_TIMEOUT:TIMEOUT/);
});


test("real ThePirateBay official API call gets 16s, independent TorrentsCSV remains 11s",async()=>{
 const {searchProvider}=await import("../src/providers.mjs");
 const normal=AbortSignal.timeout,deadlines=[];
 try{
  AbortSignal.timeout=(ms)=>{deadlines.push(ms);return normal(ms);};
  const fetcher=async(url,opts)=>{
   if(url.startsWith("https://apibay.org/q.php"))
    return new Response('[{"name":"No results returned"}]',{headers:{"content-type":"application/json"}});
   if(url.startsWith("https://torrents-csv.com/service/search"))
    return new Response('{"torrents":[]}',{headers:{"content-type":"application/json"}});
   throw Error("Unapproved API endpoint");
  };
  const pirate=await searchProvider("thepiratebay","ubuntu","all",fetcher);
  const csv=await searchProvider("torrentscsv","ubuntu","all",fetcher);
  assert.deepEqual(pirate,[]);assert.deepEqual(csv,[]);
  assert.deepEqual(deadlines,[16000,11000]);
 }finally{AbortSignal.timeout=normal;}
});
