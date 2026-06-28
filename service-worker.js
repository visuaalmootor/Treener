const CACHE_NAME = 'tt-v0.8.5';
const STATIC = [
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// Paigalda: cache ainult staatilised varad (mitte app.html)
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(STATIC))
  );
  self.skipWaiting();
});

// Aktiveeri: kustuta vana cache
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch strateegia:
//   app.html      → network-first (alati värsked muutused kohe näha)
//   prices.json   → network-first (hinnad peavad olema värsked)
//   data/*.json   → network-first (andmed peavad olema värsked)
//   muu (ikoonid, manifest) → cache-first (muutuvad harva)
self.addEventListener('fetch', e => {
  const url = e.request.url;

  // app.html + kõik .json failid → network-first
  if (url.endsWith('app.html') || url.includes('.json')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // Kõik muu (ikoonid, manifest) — cache-first
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        if (!res || res.status !== 200 || res.type !== 'basic') return res;
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return res;
      });
    })
  );
});
</content>
</invoke>