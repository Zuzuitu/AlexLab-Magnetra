const URLs=[
 ["anirena","https://anirena.com/?q=ubuntu&page=1"],
 ["bitsearch","https://bitsearch.to/search?q=ubuntu&page=1&sortBy=seeders"],
 ["limetorrents","https://limetorrents.fun/search/all/ubuntu/date/1/"],
 ["torrentdownloadinfo","https://torrentdownload.info/search?q=ubuntu"],
 ["btdigg","https://btdig.com/search?q=ubuntu"]
];
const ua="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36";
await Promise.all(URLs.map(async ([id,url])=>{
 const start=Date.now();
 try{
  const resp=await fetch(url,{redirect:"manual",signal:AbortSignal.timeout(9000),headers:{"user-agent":ua,"accept":"text/html"}});
  const target=resp.headers.get("location"); const text=await resp.text();
  console.log(JSON.stringify({id,status:resp.status,ms:Date.now()-start,redirectOrigin:target?new URL(target,url).origin:null,redirectPath:target?new URL(target,url).pathname.slice(0,65):null,bytes:text.length,mitigated:resp.headers.get("cf-mitigated"),rateLimited:resp.status===429}));
 }catch(e){console.log(JSON.stringify({id,error:e.message,ms:Date.now()-start}));}
}));
