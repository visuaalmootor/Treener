const CACHE_NAME = 'tt-v0.9.6.1';
const STATIC = [
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// Paigalda: cache ainult staatilised varad (mitte HTML)
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(STATIC))
  );
  self.skipWaiting();
});

// Aktiveeri: kustuta vana cache (uus CACHE_NAME → vana app2.html visatakse minema)
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch strateegia:
//   HTML-dokumendid (app.html, app2.html, navigatsioon) → network-first (alati värske versioon kohe)
//   .json (hinnad, andmed)                              → network-first
//   muu (ikoonid, manifest)                             → cache-first (muutuvad harva)
// ⚠ v0.9.6.1 fix: varem oli network-first ainult `app.html`-le (endsWith) → app2.html
//   langes cache-first alla ja jäi vanasse versiooni kinni. Nüüd katab kõik HTML + navigatsiooni.
self.addEventListener('fetch', e => {
  const url = e.request.url;

  if (e.request.mode === 'navigate' || url.endsWith('.html') || url.includes('.json')) {
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
