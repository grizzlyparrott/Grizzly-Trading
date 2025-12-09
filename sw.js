// sw.js - basic offline support for Grizzly Parrot Trading

const CACHE_NAME = "gpt-cache-v1";

const CORE_ASSETS = [
  "/",
  "/index.html",
  "/style.css",
  "/search.js",
  "/site.webmanifest",
  "/web-app-manifest-192x192.png",
  "/web-app-manifest-512x512.png",
  "/favicon.ico"
];

// Install: cache core assets
self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(CORE_ASSETS);
    })
  );
});

// Activate: clean up old caches if you change CACHE_NAME later
self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.map(function (key) {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});

// Fetch: network-first for pages, cache-first for static files
self.addEventListener("fetch", function (event) {
  const request = event.request;

  // Only handle GET
  if (request.method !== "GET") {
    return;
  }

  // For navigation (HTML pages): network-first with cache fallback
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(request, copy);
          });
          return response;
        })
        .catch(function () {
          return caches.match(request).then(function (cached) {
            return cached || caches.match("/index.html");
          });
        })
    );
    return;
  }

  // For CSS/JS/images: cache-first with network fallback
  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) {
        return cached;
      }
      return fetch(request)
        .then(function (response) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(request, copy);
          });
          return response;
        })
        .catch(function () {
          return new Response("", { status: 504, statusText: "Offline" });
        });
    })
  );
});
