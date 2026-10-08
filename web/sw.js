const CACHE="alexlab-magnetra-v2";
const ASSETS=["/","/index.html","/styles.css","/app.js","/icon.svg","/manifest.webmanifest"];
const FRESH_ASSETS=new Set(["/app.js","/styles.css","/manifest.webmanifest"]);
self.addEventListener("install",event=>
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()))
);
self.addEventListener("activate",event=>event.waitUntil(Promise.all([
  self.clients.claim(),
  caches.keys().then(keys=>Promise.all(keys.filter(name=>name.startsWith("alexlab-magnetra-")&&name!==CACHE).map(name=>caches.delete(name))))
])));
self.addEventListener("fetch",event=>{
  const url=new URL(event.request.url);
  if(event.request.method!=="GET"||url.origin!==self.location.origin||url.pathname.startsWith("/api/"))return;

  if(event.request.mode==="navigate"){
    event.respondWith(fetch(event.request).catch(()=>caches.match("/") ));
    return;
  }

  if(FRESH_ASSETS.has(url.pathname)){
    event.respondWith(
      fetch(event.request,{cache:"no-store"}).then(response=>{
        if(response.ok){
          const copy=response.clone();
          event.waitUntil(caches.open(CACHE).then(cache=>cache.put(event.request,copy)));
        }
        return response;
      }).catch(()=>caches.match(event.request))
    );
    return;
  }

  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
