const CACHE_NAME = 'tt-v0.8.0';
const STATIC = [
  './app.html',
  './manifest.json',
  './data/prices.json'
];

// Paigalda: cachimine
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

// Fetch: network-first prices.json (hinnad peavad olema värsked),
// cache-first kõik muu (app.html töötab offline)
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // prices.json — proovi võrku, kui ei saa kasuta cache
  if (url.pathname.endsWith('prices.json')) {
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

  // Kõik muu — cache-first
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
