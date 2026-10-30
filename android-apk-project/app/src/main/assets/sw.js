// KAII Mobile Service Worker (v3.6 - Deep Dark AMOLED Quiz & Liquid Glass Sync)
const CACHE_NAME = 'wf-mobile-v3.6';
const STATIC_ASSETS = [
  '/mobile/',
  '/mobile/index.html',
  '/mobile/avatar_square.jpg',
  '/mobile/app.css',
  '/mobile/app.js',
  '/mobile/icons.js',
  '/mobile/manifest.json',
  '/icons/192.png',
  '/icons/512.png',
  '/words_final.json',
  '/conjugations.json',
  '/sentences_final.json',
  '/grammar_summary.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => console.warn('PWA prefetch note:', err));
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => {
          console.log('Purging old SW cache:', key);
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. NEVER cache TTS audio requests — always stream live from laptop
  if (url.pathname.startsWith('/api/tts')) {
    return;
  }

  // 2. NETWORK-FIRST for HTML, JS, CSS, and navigation so updates on laptop appear instantly on phone!
  const isCodeAsset = url.pathname.endsWith('.html') ||
                      url.pathname.endsWith('.js') ||
                      url.pathname.endsWith('.css') ||
                      url.pathname === '/m' ||
                      url.pathname === '/m/' ||
                      url.pathname.startsWith('/mobile');

  if (isCodeAsset) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (res && res.status === 200 && event.request.method === 'GET') {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 3. Network first with cache fallback for JSON data
  if (url.pathname.endsWith('.json')) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (res && res.status === 200) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 4. Cache-first for images/icons
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((res) => {
        if (res && res.status === 200 && event.request.method === 'GET') {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return res;
      });
    })
  );
});
