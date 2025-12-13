// const cacheName = "FORMS-FLOW-AI-WEB-CACHE-V2";

// const urlsToCache = [
//   "/manifest.json",
//   "/favicon.ico",
//   "/spinner.gif",
//   "/logo.svg"
// ];

// // Install a service worker
// self.addEventListener('install', event => {
//  // Perform install steps
//   event.waitUntil(
//     caches.open(cacheName)
//       .then(cache => cache.addAll(urlsToCache))
//   );
// });

// self.addEventListener('fetch', (event)=>{
//   event.respondWith(
//     caches.match(event.request)
//       .then((response)=>{
//       // Cache hit - return response
//         if (response) {
//           return response;
//         }
//         return fetch(event.request);
//       })
//   );
// });

// //Delete outdate cache
// self.addEventListener("activate", event => {
//   event.waitUntil(
//     caches.keys().then(cacheNames => {
//       return Promise.all(
//          cacheNames.filter((name)=>{
//           // Return true if you want to remove this cache,
//           // but remember that caches are shared across
//           // the whole origin
//           return cacheName!==name

//         }).map(name => {
//             return caches.delete(name);
//           })
//       );
//     })
//   );
// });

// self.addEventListener('message', (event)=>{
//   if(event.origin === self.location.origin){
//     if (event.data.action === 'skipWaiting') {
//       self.skipWaiting();
//     }
//   }
// });

// // --- No-op service worker (disables all caching and behavior safely) --- 

// self.addEventListener("install", () => {
//   // Ensure this SW activates immediately
//   self.skipWaiting();
// });

// self.addEventListener("activate", () => {
//   // Ensure pages immediately use this (non-caching) SW
//   clients.claim();
// });

//KILL SWITCH To remove old/cached service workers from client-side (users browsers)
self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    (async () => {
      const cacheNames = await caches.keys();
      await Promise.all(cacheNames.map(name => caches.delete(name)));
      await self.registration.unregister();
      await self.clients.claim();
    })()
  );
});