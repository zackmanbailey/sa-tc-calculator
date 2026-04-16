"""
TitanForge v3.0 — Progressive Web App (PWA) Support
====================================================
Complete offline support and PWA installation for TitanForge.

Includes:
  - Service Worker with cache-first/network-first strategies
  - Web App Manifest for home screen installation
  - Offline fallback page
  - Install banner with beforeinstallprompt handling
  - Background sync for failed QR scans
  - IndexedDB queue for offline POST requests

Usage in main template:
    from templates.pwa_support import (
        get_pwa_bundle, PWA_HEAD_TAGS, SERVICE_WORKER_JS
    )

    Then in <head>:
        {{ PWA_HEAD_TAGS }}

    And register service worker in JavaScript:
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/service-worker.js')
        }
"""

import json
import base64

# ─────────────────────────────────────────────
# PWA MANIFEST (Web App Config)
# ─────────────────────────────────────────────

PWA_MANIFEST = {
    "name": "TitanForge",
    "short_name": "TitanForge",
    "description": "Metal building fabrication management and production scheduling system",
    "start_url": "/shop-floor",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "theme_color": "#0F172A",
    "background_color": "#0F172A",
    "prefer_related_applications": False,
    "icons": [
        {
            "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIi8+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIiByeD0iNDUiLz4KPHR0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9Ijc2IiBmb250LXdlaWdodD0iODAwIiBmaWxsPSIjRjZBRTJEIiBmb250LWZhbWlseT0iQXJpYWwiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5URjwvdGV4dD4KPC9zdmc+Cg==",
            "sizes": "192x192",
            "type": "image/svg+xml",
            "purpose": "any"
        },
        {
            "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBmaWxsPSIjMEYxNzJBIi8+CjxyZWN0IHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiBmaWxsPSIjMEYxNzJBIiByeD0iMTIwIi8+Cjx0dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIyMjAiIGZvbnQtd2VpZ2h0PSI4MDAiIGZpbGw9IiNGNkFFMkQiIGZvbnQtZmFtaWx5PSJBcmlhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRGPC90dGV4dD4KPC9zdmc+Cg==",
            "sizes": "512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ],
    "categories": ["productivity", "business"],
    "screenshots": [
        {
            "src": "/static/screenshot-mobile.png",
            "sizes": "540x720",
            "type": "image/png",
            "form_factor": "narrow"
        }
    ]
}


# ─────────────────────────────────────────────
# SERVICE WORKER
# ─────────────────────────────────────────────

SERVICE_WORKER_JS = """
// TitanForge Service Worker
// Offline support with network-first for APIs, cache-first for static assets

const CACHE_VERSION = 'tf-cache-v2';
const API_CACHE = 'tf-api-cache-v2';
const OFFLINE_CACHE = 'tf-offline-cache-v2';
const QUEUE_DB = 'titanforge-queue';
const QUEUE_STORE = 'pending-requests';

// Pages to pre-cache for offline shop floor use
const PRECACHE_PAGES = [
    '/',
    '/shop-floor',
    '/work-orders',
    '/inventory',
    '/static/offline.html'
];

// API endpoints worth caching for offline reads
const PRECACHE_API = [
    '/api/inventory/summary',
    '/api/inventory/coils',
    '/api/inventory/alerts',
];

// POST endpoints to queue when offline (not just QR scans)
const QUEUEABLE_POSTS = [
    '/api/work-orders/qr-scan',
    '/api/work-orders/edit',
    '/api/inspections/',
    '/api/inventory/allocate',
];

// ─────────────────────────────────────────────
// INSTALLATION
// ─────────────────────────────────────────────

self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Installing v2...');
    event.waitUntil(
        Promise.all([
            // Cache pages for offline navigation
            caches.open(OFFLINE_CACHE).then((cache) => {
                return cache.addAll(PRECACHE_PAGES)
                    .catch(err => console.log('[ServiceWorker] Page cache error:', err));
            }),
            // Pre-warm API cache with key data
            caches.open(API_CACHE).then((cache) => {
                return Promise.all(
                    PRECACHE_API.map(url =>
                        fetch(url).then(resp => {
                            if (resp.ok) cache.put(url, resp);
                        }).catch(() => {})
                    )
                );
            })
        ])
    );
    self.skipWaiting();
});

// ─────────────────────────────────────────────
// ACTIVATION
// ─────────────────────────────────────────────

self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activating v2...');
    const VALID_CACHES = [CACHE_VERSION, API_CACHE, OFFLINE_CACHE];
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (!VALID_CACHES.includes(cacheName)) {
                        console.log('[ServiceWorker] Purging old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => initializeQueue())
    );
    self.clients.claim();
});

// ─────────────────────────────────────────────
// FETCH HANDLING
// ─────────────────────────────────────────────

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET requests (handled separately)
    if (event.request.method !== 'GET') {
        // Queue POST requests to known endpoints when offline
        if (event.request.method === 'POST' && QUEUEABLE_POSTS.some(p => event.request.url.includes(p))) {
            event.respondWith(handleQueuedPost(event.request));
        } else if (event.request.method === 'POST') {
            // Try to fetch; if offline, return a useful error
            event.respondWith(
                fetch(event.request).catch(() => handleOfflineRequest())
            );
        }
        return;
    }

    // Network-first for API calls
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirstStrategy(event.request));
        return;
    }

    // Cache-first for static assets
    if (isStaticAsset(url.pathname)) {
        event.respondWith(cacheFirstStrategy(event.request));
        return;
    }

    // Network-first for pages with offline fallback
    event.respondWith(networkFirstWithFallback(event.request));
});

// ─────────────────────────────────────────────
// STRATEGIES
// ─────────────────────────────────────────────

function networkFirstStrategy(request) {
    return fetch(request)
        .then(response => {
            if (!response || response.status !== 200) {
                return response;
            }
            // Clone and cache successful API responses
            const cloned = response.clone();
            caches.open(API_CACHE).then(cache => {
                cache.put(request, cloned);
            });
            return response;
        })
        .catch(err => {
            // Return cached API response if available
            return caches.match(request).then(cached => {
                return cached || createErrorResponse('API offline');
            });
        });
}

function cacheFirstStrategy(request) {
    return caches.match(request)
        .then(cached => {
            if (cached) return cached;
            return fetch(request).then(response => {
                if (!response || response.status !== 200) {
                    return response;
                }
                const cloned = response.clone();
                caches.open(CACHE_VERSION).then(cache => {
                    cache.put(request, cloned);
                });
                return response;
            });
        })
        .catch(err => {
            return createErrorResponse('Asset not available offline');
        });
}

function networkFirstWithFallback(request) {
    return fetch(request)
        .then(response => {
            if (!response || response.status !== 200) {
                return caches.match(request).then(cached => cached || getOfflinePage());
            }
            // Cache successful page loads
            const cloned = response.clone();
            caches.open(CACHE_VERSION).then(cache => {
                cache.put(request, cloned);
            });
            return response;
        })
        .catch(err => {
            return caches.match(request).then(cached => cached || getOfflinePage());
        });
}

// ─────────────────────────────────────────────
// OFFLINE QUEUE (IndexedDB)
// ─────────────────────────────────────────────

function initializeQueue() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(QUEUE_DB, 1);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(QUEUE_STORE)) {
                const store = db.createObjectStore(QUEUE_STORE, { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };
    });
}

function queueRequest(request) {
    return request.clone().json().then(body => {
        return initializeQueue().then(db => {
            return new Promise((resolve, reject) => {
                const tx = db.transaction([QUEUE_STORE], 'readwrite');
                const store = tx.objectStore(QUEUE_STORE);
                const payload = {
                    method: request.method,
                    url: request.url,
                    headers: Object.fromEntries(request.headers),
                    body: body,
                    timestamp: Date.now()
                };
                const req = store.add(payload);
                req.onerror = () => reject(req.error);
                req.onsuccess = () => resolve();
                tx.oncomplete = () => {
                    notifyClients({
                        type: 'QUEUE_UPDATED',
                        message: 'Your scan was queued and will sync when online'
                    });
                };
            });
        });
    });
}

function handleQueuedPost(request) {
    return fetch(request)
        .then(response => {
            if (response.ok) {
                // Clear queued items for this scan type
                clearQueuedItem(request.url);
                return response;
            }
            return queueRequest(request).then(() => {
                return createResponse(JSON.stringify({
                    success: true,
                    offline: true,
                    message: 'Scan queued for later sync'
                }), { status: 200, type: 'application/json' });
            });
        })
        .catch(err => {
            return queueRequest(request).then(() => {
                return createResponse(JSON.stringify({
                    success: true,
                    offline: true,
                    message: 'Scan queued for later sync'
                }), { status: 200, type: 'application/json' });
            });
        });
}

function syncQueue() {
    return initializeQueue().then(db => {
        return new Promise((resolve, reject) => {
            const tx = db.transaction([QUEUE_STORE], 'readonly');
            const store = tx.objectStore(QUEUE_STORE);
            const allRequests = store.getAll();
            allRequests.onerror = () => reject(allRequests.error);
            allRequests.onsuccess = () => {
                const requests = allRequests.result;
                if (requests.length === 0) {
                    resolve([]);
                    return;
                }

                Promise.all(
                    requests.map(req => {
                        return fetch(req.url, {
                            method: req.method,
                            headers: req.headers,
                            body: JSON.stringify(req.body)
                        })
                        .then(response => {
                            if (response.ok) {
                                // Remove from queue
                                return new Promise((res, rej) => {
                                    const delTx = db.transaction([QUEUE_STORE], 'readwrite');
                                    const delStore = delTx.objectStore(QUEUE_STORE);
                                    const delReq = delStore.delete(req.id);
                                    delReq.onerror = () => rej(delReq.error);
                                    delReq.onsuccess = () => res({ id: req.id, success: true });
                                });
                            }
                            return { id: req.id, success: false };
                        })
                        .catch(err => ({ id: req.id, success: false, error: err.message }));
                    })
                )
                .then(results => {
                    const synced = results.filter(r => r.success).length;
                    notifyClients({
                        type: 'SYNC_COMPLETE',
                        synced: synced,
                        failed: results.length - synced
                    });
                    resolve(results);
                });
            };
        });
    });
}

function clearQueuedItem(url) {
    initializeQueue().then(db => {
        const tx = db.transaction([QUEUE_STORE], 'readwrite');
        const store = tx.objectStore(QUEUE_STORE);
        const index = store.index('timestamp');
        index.openCursor().onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                if (cursor.value.url === url) {
                    store.delete(cursor.primaryKey);
                }
                cursor.continue();
            }
        };
    });
}

// ─────────────────────────────────────────────
// BACKGROUND SYNC
// ─────────────────────────────────────────────

self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-queue') {
        event.waitUntil(syncQueue());
    }
});

// ─────────────────────────────────────────────
// MESSAGE HANDLING (from clients)
// ─────────────────────────────────────────────

self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SYNC_QUEUE') {
        event.waitUntil(syncQueue());
    } else if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// ─────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────

function isStaticAsset(pathname) {
    return /\\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$/i.test(pathname) ||
           pathname.startsWith('/static/');
}

function getOfflinePage() {
    return caches.match('/static/offline.html').then(response => {
        return response || createErrorResponse('<h1>Offline</h1><p>You are offline. Some features are unavailable.</p>');
    });
}

function handleOfflineRequest() {
    return createResponse(JSON.stringify({
        success: false,
        message: 'Offline - request not available',
        offline: true
    }), { status: 503, type: 'application/json' });
}

function createResponse(body, options = {}) {
    return Promise.resolve(new Response(body, {
        status: options.status || 200,
        headers: {
            'Content-Type': options.type || 'text/html'
        }
    }));
}

function createErrorResponse(message) {
    return createResponse(JSON.stringify({
        success: false,
        message: message,
        offline: true
    }), { status: 503, type: 'application/json' });
}

function notifyClients(message) {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage(message);
        });
    });
}
"""


# ─────────────────────────────────────────────
# OFFLINE PAGE
# ─────────────────────────────────────────────

OFFLINE_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Offline — TitanForge</title>
<style>
:root {
    --tf-navy: #0F172A;
    --tf-navy-light: #1E293B;
    --tf-gray-100: #F1F5F9;
    --tf-gray-400: #94A3B8;
    --tf-amber: #F6AE2D;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--tf-navy);
    color: var(--tf-gray-100);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
}

.offline-container {
    background: var(--tf-navy-light);
    border: 2px solid var(--tf-amber);
    border-radius: 12px;
    padding: 40px;
    max-width: 500px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.offline-icon {
    font-size: 64px;
    margin-bottom: 20px;
}

h1 {
    font-size: 28px;
    font-weight: 800;
    color: var(--tf-amber);
    margin-bottom: 10px;
}

p {
    font-size: 14px;
    color: var(--tf-gray-400);
    margin-bottom: 20px;
    line-height: 1.6;
}

.offline-status {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--tf-navy);
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    font-size: 13px;
    text-align: left;
}

.status-label {
    color: var(--tf-amber);
    font-weight: 600;
    margin-bottom: 8px;
}

.last-sync {
    color: var(--tf-gray-400);
    margin: 10px 0 0 0;
    font-size: 12px;
}

.queue-items {
    max-height: 150px;
    overflow-y: auto;
    border-top: 1px solid var(--tf-navy);
    padding-top: 10px;
    margin-top: 10px;
    text-align: left;
}

.queue-item {
    padding: 6px 0;
    font-size: 12px;
    color: var(--tf-gray-400);
    border-bottom: 1px solid rgba(51, 65, 85, 0.3);
}

.queue-item:last-child {
    border-bottom: none;
}

.queue-item-mark {
    color: var(--tf-amber);
    font-weight: 600;
    margin-right: 6px;
}

.offline-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
}

button {
    flex: 1;
    padding: 12px 20px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-primary {
    background: var(--tf-amber);
    color: var(--tf-navy);
}

.btn-primary:hover {
    background: #FFB84D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(246, 174, 45, 0.3);
}

.btn-secondary {
    background: var(--tf-navy);
    color: var(--tf-gray-100);
    border: 1px solid var(--tf-amber);
}

.btn-secondary:hover {
    background: rgba(246, 174, 45, 0.1);
}

.connection-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #EF4444;
    border-radius: 6px;
    color: #FECACA;
    font-size: 12px;
    margin-top: 15px;
}

.indicator-dot {
    width: 8px;
    height: 8px;
    background: #EF4444;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.connection-indicator.online {
    background: rgba(34, 197, 94, 0.1);
    border-color: #22C55E;
    color: #BBFBDB;
}

.connection-indicator.online .indicator-dot {
    background: #22C55E;
    animation: none;
}

@media (max-width: 500px) {
    .offline-container {
        padding: 30px 20px;
    }

    h1 {
        font-size: 24px;
    }

    .offline-actions {
        flex-direction: column;
    }
}
</style>
</head>
<body>

<div class="offline-container">
    <div class="offline-icon">⚠️</div>
    <h1>You're Offline</h1>
    <p>TitanForge is running in offline mode. You can still view cached pages and queue actions.</p>

    <div class="offline-status">
        <div class="status-label">Connection Status</div>
        <div class="connection-indicator" id="connectionStatus">
            <span class="indicator-dot"></span>
            <span>Searching for connection...</span>
        </div>
        <div class="last-sync" id="lastSync">Last synced: —</div>
    </div>

    <div class="offline-status" id="queueStatus" style="display: none;">
        <div class="status-label">Queued Actions</div>
        <div class="queue-items" id="queueList"></div>
        <p style="margin-top: 10px; font-size: 12px; color: var(--tf-gray-400);">
            These actions will sync when you go online.
        </p>
    </div>

    <div class="offline-actions">
        <button class="btn-primary" id="retryBtn">Retry Connection</button>
        <button class="btn-secondary" id="backBtn">Go Back</button>
    </div>
</div>

<script>
// Update connection status
function updateConnectionStatus() {
    const status = navigator.onLine;
    const indicator = document.getElementById('connectionStatus');
    if (status) {
        indicator.className = 'connection-indicator online';
        indicator.innerHTML = '<span class="indicator-dot"></span><span>Back online!</span>';
        // Attempt to sync queue
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({ type: 'SYNC_QUEUE' });
        }
    } else {
        indicator.className = 'connection-indicator';
        indicator.innerHTML = '<span class="indicator-dot"></span><span>Offline</span>';
    }
}

// Load queued items
function loadQueuedItems() {
    if (!window.indexedDB) return;

    const request = indexedDB.open('titanforge-queue', 1);
    request.onsuccess = (event) => {
        const db = event.target.result;
        const tx = db.transaction(['pending-requests'], 'readonly');
        const store = tx.objectStore('pending-requests');
        const allReqs = store.getAll();

        allReqs.onsuccess = () => {
            const items = allReqs.result;
            if (items.length > 0) {
                const queueStatus = document.getElementById('queueStatus');
                const queueList = document.getElementById('queueList');
                queueStatus.style.display = 'block';
                queueList.innerHTML = items.map(item => {
                    const body = item.body;
                    const mark = body.ship_mark || body.work_order_id || 'Unknown';
                    const time = new Date(item.timestamp).toLocaleTimeString();
                    return `<div class="queue-item">
                        <span class="queue-item-mark">${mark}</span> - ${time}
                    </div>`;
                }).join('');
            }
        };
    };
}

// Update last sync time from localStorage
function updateLastSync() {
    const lastSync = localStorage.getItem('lastSync');
    if (lastSync) {
        const date = new Date(parseInt(lastSync));
        document.getElementById('lastSync').textContent = `Last synced: ${date.toLocaleTimeString()}`;
    }
}

// Button handlers
document.getElementById('retryBtn').addEventListener('click', () => {
    window.location.reload();
});

document.getElementById('backBtn').addEventListener('click', () => {
    window.history.back();
});

// Event listeners
window.addEventListener('online', updateConnectionStatus);
window.addEventListener('offline', updateConnectionStatus);

// Initialize
updateConnectionStatus();
updateLastSync();
loadQueuedItems();

// Check status periodically
setInterval(updateConnectionStatus, 3000);
</script>

</body>
</html>
"""


# ─────────────────────────────────────────────
# PWA INSTALL BANNER
# ─────────────────────────────────────────────

PWA_INSTALL_BANNER_HTML = """
<!-- PWA Install Banner -->
<div id="pwaInstallBanner" class="pwa-install-banner" style="display: none;">
    <div class="pwa-banner-content">
        <div class="pwa-banner-icon">📱</div>
        <div class="pwa-banner-text">
            <h3>Install TitanForge</h3>
            <p>Get offline access and faster load times</p>
        </div>
        <button id="pwaInstallBtn" class="pwa-install-btn">Install</button>
        <button id="pwaDismissBtn" class="pwa-dismiss-btn">Not Now</button>
    </div>
</div>

<style id="pwaBannerStyles">
.pwa-install-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border-top: 2px solid #F6AE2D;
    padding: 16px 20px;
    z-index: 1000;
    box-shadow: 0 -4px 12px rgba(0,0,0,0.3);
    animation: slideUp 0.3s cubic-bezier(0.4,0,0.2,1);
}

@keyframes slideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.pwa-banner-content {
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 16px;
}

.pwa-banner-icon {
    font-size: 32px;
    flex-shrink: 0;
}

.pwa-banner-text {
    flex: 1;
    color: #F1F5F9;
}

.pwa-banner-text h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #F6AE2D;
}

.pwa-banner-text p {
    margin: 4px 0 0 0;
    font-size: 13px;
    color: #94A3B8;
}

.pwa-install-btn,
.pwa-dismiss-btn {
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
}

.pwa-install-btn {
    background: #F6AE2D;
    color: #0F172A;
}

.pwa-install-btn:hover {
    background: #FFB84D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(246, 174, 45, 0.3);
}

.pwa-install-btn:active {
    transform: translateY(0);
}

.pwa-dismiss-btn {
    background: transparent;
    color: #94A3B8;
    border: 1px solid #475569;
}

.pwa-dismiss-btn:hover {
    border-color: #F6AE2D;
    color: #F6AE2D;
}

@media (max-width: 640px) {
    .pwa-banner-content {
        gap: 12px;
    }

    .pwa-banner-text h3 {
        font-size: 15px;
    }

    .pwa-banner-text p {
        display: none;
    }

    .pwa-install-btn,
    .pwa-dismiss-btn {
        padding: 8px 12px;
        font-size: 12px;
    }
}
</style>

<script>
// PWA Install Prompt Handling
let deferredPrompt = null;
const INSTALL_DISMISSED_KEY = 'pwaInstallDismissed';
const INSTALL_DISMISSED_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallBanner();
});

function showInstallBanner() {
    // Check if user dismissed in last 7 days
    const lastDismissed = sessionStorage.getItem(INSTALL_DISMISSED_KEY);
    if (lastDismissed) {
        const dismissedTime = parseInt(lastDismissed);
        if (Date.now() - dismissedTime < INSTALL_DISMISSED_DURATION) {
            return;
        }
    }

    // Show banner
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) {
        banner.style.display = 'flex';
    }
}

document.getElementById('pwaInstallBtn')?.addEventListener('click', async () => {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log('User response to install prompt:', outcome);
        deferredPrompt = null;
        hideBanner();
        localStorage.setItem('titanforgeInstalled', 'true');
    }
});

document.getElementById('pwaDismissBtn')?.addEventListener('click', () => {
    sessionStorage.setItem(INSTALL_DISMISSED_KEY, Date.now().toString());
    hideBanner();
});

function hideBanner() {
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) {
        banner.style.animation = 'slideDown 0.3s cubic-bezier(0.4,0,0.2,1) forwards';
        setTimeout(() => {
            banner.style.display = 'none';
        }, 300);
    }
}

// Listen for successful installation
window.addEventListener('appinstalled', () => {
    console.log('TitanForge installed as app');
    localStorage.setItem('titanforgeInstalled', 'true');
    localStorage.setItem('lastSync', Date.now().toString());
});

// Hide banner on app launch (if running as PWA)
if (window.navigator.standalone === true) {
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) banner.style.display = 'none';
}

// Add slideDown animation
const style = document.createElement('style');
style.textContent = `
@keyframes slideDown {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(100%); }
}
`;
document.head.appendChild(style);
</script>
"""


# ─────────────────────────────────────────────
# PWA HEAD TAGS
# ─────────────────────────────────────────────

PWA_HEAD_TAGS = """
<meta name="theme-color" content="#0F172A">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="TitanForge">
<link rel="apple-touch-icon" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIi8+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIiByeD0iNDUiLz4KPHR0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9Ijc2IiBmb250LXdlaWdodD0iODAwIiBmaWxsPSIjRjZBRTJEIiBmb250LWZhbWlseT0iQXJpYWwiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5URjwvdGV4dD4KPC9zdmc+Cg==">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIi8+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiBmaWxsPSIjMEYxNzJBIiByeD0iNDUiLz4KPHR0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9Ijc2IiBmb250LXdlaWdodD0iODAwIiBmaWxsPSIjRjZBRTJEIiBmb250LWZhbWlseT0iQXJpYWwiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5URjwvdGV4dD4KPC9zdmc+Cg==">
<link rel="manifest" href="/static/manifest.json">
"""


# ─────────────────────────────────────────────
# SERVICE WORKER REGISTRATION
# ─────────────────────────────────────────────

SERVICE_WORKER_REGISTRATION_JS = """
// Service Worker Registration and Management
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => {
                console.log('[App] Service Worker registered:', registration);

                // Update check every 6 hours
                setInterval(() => {
                    registration.update();
                }, 6 * 60 * 60 * 1000);

                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            console.log('[App] Service Worker update available');
                            // Show update notification
                            if (window.updateServiceWorkerCallback) {
                                window.updateServiceWorkerCallback();
                            }
                        }
                    });
                });
            })
            .catch(error => {
                console.error('[App] Service Worker registration failed:', error);
            });
    });

    // Handle messages from service worker
    navigator.serviceWorker.addEventListener('message', (event) => {
        const data = event.data;
        if (data.type === 'QUEUE_UPDATED') {
            console.log('[App]', data.message);
            if (window.onQueueUpdated) {
                window.onQueueUpdated(data);
            }
        } else if (data.type === 'SYNC_COMPLETE') {
            console.log('[App] Queue synced:', data);
            if (window.onSyncComplete) {
                window.onSyncComplete(data);
            }
            // Update last sync time
            localStorage.setItem('lastSync', Date.now().toString());
        }
    });
}

// Global function to trigger offline queue sync
window.syncQueue = function() {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SYNC_QUEUE' });
        return true;
    }
    return false;
};

// Global function to skip waiting (for updates)
window.skipWaiting = function() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistration().then(reg => {
            if (reg && reg.waiting) {
                reg.waiting.postMessage({ type: 'SKIP_WAITING' });
                window.location.reload();
            }
        });
    }
};
"""


# ─────────────────────────────────────────────
# GET_PWA_BUNDLE
# ─────────────────────────────────────────────

def get_pwa_bundle() -> dict:
    """
    Returns a complete bundle of PWA assets for easy integration.

    Returns:
    {
        "manifest_json": dict (web app manifest),
        "service_worker_js": str (service worker code),
        "install_banner_html": str (install UI),
        "offline_html": str (offline fallback page),
        "pwa_head_tags": str (meta tags for <head>),
        "service_worker_registration_js": str (registration code),
    }
    """
    return {
        "manifest_json": PWA_MANIFEST,
        "manifest_json_str": json.dumps(PWA_MANIFEST, indent=2),
        "service_worker_js": SERVICE_WORKER_JS,
        "install_banner_html": PWA_INSTALL_BANNER_HTML,
        "offline_html": OFFLINE_PAGE_HTML,
        "pwa_head_tags": PWA_HEAD_TAGS,
        "service_worker_registration_js": SERVICE_WORKER_REGISTRATION_JS,
    }
