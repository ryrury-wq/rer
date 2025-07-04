// static/sw.js
const CACHE_NAME = 'vkusvill-cache-v1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/script.js',
  '/static/icon-192x192.png',
  // Добавьте другие важные ресурсы
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
