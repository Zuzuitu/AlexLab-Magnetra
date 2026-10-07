const CACHE="alexlab-magnetra-v1";
const ASSETS=["/","/index.html","/styles.css","/app.js","/icon.svg","/manifest.webmanifest"];
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener("activate",e=>e.waitUntil(Promise.all([self.clients.claim(),caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith("alexlab-magnetra-")&&k!==CACHE).map(k=>caches.delete(k))))])));
self.addEventListener("fetch",e=>{const u=new URL(e.request.url);if(e.request.method!=="GET"||u.origin!==self.location.origin||u.pathname.startsWith("/api/"))return;if(e.request.mode==="navigate"){e.respondWith(fetch(e.request).catch(()=>caches.match("/")));return;}e.respondWith(caches.match(e.request).then(c=>c||fetch(e.request)));});
