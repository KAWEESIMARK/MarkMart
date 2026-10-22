self.addEventListener('install', e => {
  e.waitUntil(caches.open('markmart-v1').then(c => c.addAll(['/','/reels','/trending','/static/logo.png'])));
});
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('/static/sw.js")}</script>