// -----------------------------------------------------------------
// Template Name: Suha - Multipurpose Ecommerce Mobile HTML Template
// Template Author: Designing World
// Template Author URL: https://themeforest.net/user/designing-world
// -----------------------------------------------------------------

importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

const CACHE = "pwabuilder-page";

// TODO: replace the following with the correct offline fallback page i.e.: const offlineFallbackPage = "offline.html";
const offlineFallbackPage = "offline.html";
// Pre Caching Assets
const precacheAssets = [
    '/',
    'css/bootstrap.min.css',
    'img/core-img/curve.png',
    'img/core-img/curve2.png',
    'img/core-img/dot-blue.png',
    'img/core-img/dot.png',
    'img/core-img/logo-small.png',
    'img/core-img/logo-white.png',
    'img/bg-img/no-internet.png',
    'js/jquery.min.js',
    'js/pwa.js',
    'js/dark-mode-switch.js',
    'js/active.js',
    'home.html',
    'manifest.json',
    'offline.html',
    'message.html',
    'cart.html',
    'pages.html',
    'settings.html',
    'style.css'
];

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener('install', async (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.add(offlineFallbackPage))
  );
});

if (workbox.navigationPreload.isSupported()) {
  workbox.navigationPreload.enable();
}

// Activate Event
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(keys
                .filter(key => key !== staticCacheName && key !== dynamicCacheName)
                .map(key => caches.delete(key))
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preloadResp = await event.preloadResponse;

        if (preloadResp) {
          return preloadResp;
        }

        const networkResp = await fetch(event.request);
        return networkResp;
      } catch (error) {

        const cache = await caches.open(CACHE);
        const cachedResp = await cache.match(offlineFallbackPage);
        return cachedResp;
      }
    })());
  }
});