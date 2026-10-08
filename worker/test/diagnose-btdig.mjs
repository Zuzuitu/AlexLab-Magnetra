const urls=[
 "https://btdig.com/search?q=ubuntu",
 "https://www.btdig.com/search?q=ubuntu",
 "https://btdig.com/search?q=ubuntu&p=0",
 "https://btdig.com/"
];
const ua="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36";
await Promise.all(urls.map(async url=>{
 const start=Date.now();
 try {
  const result=await fetch(url,{redirect:"manual",signal:AbortSignal.timeout(12000),headers:{"user-agent":ua,"accept":"text/html","accept-language":"en-US,en;q=0.9"}});
  const body=await result.text();
  console.log(JSON.stringify({url,status:result.status,elapsedMs:Date.now()-start,size:body.length,challenge:body.includes("Just a moment"),location:result.headers.get("location")?.slice(0,100)}));
 }catch(e){console.log(JSON.stringify({url,error:e.message,elapsedMs:Date.now()-start}));}
}));
