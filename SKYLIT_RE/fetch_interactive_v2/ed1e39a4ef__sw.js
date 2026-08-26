// Service Worker for Skylit PWA
// Handles push notifications, caching, and offline support

// =============================================================================
// IndexedDB helpers for pending navigation (iOS PWA workaround)
// =============================================================================
const PENDING_NAV_DB_NAME = 'skylit-sw';
const PENDING_NAV_DB_VERSION = 1;
const PENDING_NAV_STORE_NAME = 'pending-navigation';

/**
 * Store pending navigation in IndexedDB before opening app.
 * This is needed for iOS PWA where clients.openWindow() doesn't reliably
 * pass URL parameters in standalone mode.
 */
async function storePendingNavigation(ticker, url) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(PENDING_NAV_DB_NAME, PENDING_NAV_DB_VERSION);

    request.onerror = () => {
      console.error('[Service Worker] Failed to open IndexedDB:', request.error);
      reject(request.error);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(PENDING_NAV_STORE_NAME)) {
        db.createObjectStore(PENDING_NAV_STORE_NAME, { keyPath: 'id' });
      }
    };

    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(PENDING_NAV_STORE_NAME, 'readwrite');
      const store = transaction.objectStore(PENDING_NAV_STORE_NAME);

      const putRequest = store.put({
        id: 'current',
        ticker: ticker,
        url: url,
        timestamp: Date.now(),
      });

      putRequest.onerror = () => {
        console.error('[Service Worker] Failed to store pending navigation:', putRequest.error);
        reject(putRequest.error);
      };

      putRequest.onsuccess = () => {
        console.log('[Service Worker] Stored pending navigation for ticker:', ticker);
        resolve();
      };
    };
  });
}

// =============================================================================
// Cache configuration
// =============================================================================

// Cache version is set at build time via environment variable injection
// Format: skylit-{GIT_SHA}-{TIMESTAMP} (e.g., skylit-abc123-1234567890)
const CACHE_VERSION = '04e79a3-1787634064';
const CACHE_NAME = `skylit-${CACHE_VERSION}`;
const ASSETS_TO_CACHE = [
  '/',
  '/offline.html',
];

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWithRetry(request, retryDelayMs = 750) {
  try {
    return await fetch(request);
  } catch (error) {
    console.warn('[Service Worker] Initial fetch failed, retrying once:', request.url, error);
    await sleep(retryDelayMs);
    return fetch(request);
  }
}

console.log('[Service Worker] Cache version:', CACHE_VERSION);

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching essential assets');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  // Don't skip waiting automatically - let user decide when to update
  // skipWaiting will be called when user clicks "Update Now" button
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        if ('navigationPreload' in self.registration) {
          return self.registration.navigationPreload.enable().catch((error) => {
            console.warn('[Service Worker] Failed to enable navigation preload:', error);
          });
        }
      })
      .then(() => {
        console.log('[Service Worker] Claiming clients...');
        return self.clients.claim();
      })
      .then(() => {
        console.log('[Service Worker] Clients claimed successfully');
      })
  );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip cross-origin requests (e.g., API calls to staging/production backend)
  if (url.origin !== self.location.origin) {
    return;
  }

  // Skip SSE/streaming requests — service worker fetch creates a duplicate connection
  if (url.pathname.startsWith('/api/stream')) {
    return;
  }

  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          const preloadResponse = await event.preloadResponse;
          if (preloadResponse) {
            return preloadResponse;
          }

          return await fetchWithRetry(event.request);
        } catch (error) {
          console.warn('[Service Worker] Navigation request failed, serving offline fallback:', event.request.url, error);
          return caches.match('/offline.html');
        }
      })()
    );
  } else if (url.pathname.startsWith('/_next/')) {
    // Next.js assets: network-first to ensure fresh code in dev
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  } else {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request).catch(() => {
          // Return empty response for failed fetches (e.g., API calls to non-existent endpoints)
          return new Response(null, { status: 503, statusText: 'Service Unavailable' });
        });
      })
    );
  }
});

// =============================================================================
// Deep-link normalization
// =============================================================================

/**
 * Resolve a notification's deep link to a URL on THIS origin.
 *
 * The app is served from app.skylit.ai, but alert payloads have carried links
 * minted against a hardcoded https://skylit.ai (skylit-core's HEATMAP_URL is
 * unset in every environment, so its default was used). `new URL(link, base)`
 * IGNORES the base when `link` is absolute, so passing those straight through
 * navigated the user off the app to the marketing host.
 *
 * Keeping only pathname + search + hash is the same rule the web app applies to
 * the identical payload (`notificationHref`): the path is the part that means
 * anything, the host is whatever the reader is already on.
 *
 * skylit-core now mints a relative path, but this must keep normalizing anyway —
 * every notification already delivered still carries an absolute URL, and a
 * service worker outlives the deploy that changed the minting.
 */
function sameOriginURL(link) {
  try {
    const u = new URL(link, self.location.origin);
    return new URL(u.pathname + u.search + u.hash, self.location.origin).href;
  } catch (error) {
    console.warn('[Service Worker] Unparseable deep link, opening app root:', link, error);
    return new URL('/', self.location.origin).href;
  }
}

// Push event - handle incoming push notifications
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received:', event);

  let data = {
    title: 'Skylit Alert',
    body: 'A new alert was triggered',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    tag: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    requireInteraction: false,
  };

  if (event.data) {
    try {
      const payload = event.data.json();
      data = {
        title: payload.title || data.title,
        body: payload.body || payload.message || data.body,
        icon: payload.icon || data.icon,
        badge: payload.badge || data.badge,
        tag: `alert-${payload.alert_id || 'unknown'}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        data: payload.data || {
          url: payload.url || '/',
          alert_id: payload.alert_id,
          ticker: payload.ticker,
          node_type: payload.node_type,
        },
        requireInteraction: payload.requireInteraction || false,
      };
    } catch (error) {
      console.error('[Service Worker] Error parsing push payload:', error);
    }
  }

  const promiseChain = self.registration.showNotification(data.title, {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    tag: data.tag,
    data: data.data,
    requireInteraction: data.requireInteraction,
    vibrate: [200, 100, 200],
    actions: [
      {
        action: 'view',
        title: 'View Alert',
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
      },
    ],
  });

  event.waitUntil(promiseChain);
});

// Notification click event - handle notification interactions
//
// STRATEGY: Use WindowClient.navigate() as PRIMARY method (works in Chrome 49+, Edge, Firefox)
// with postMessage as FALLBACK for Safari (which doesn't support navigate())
//
// See: https://developer.mozilla.org/en-US/docs/Web/API/WindowClient/navigate
// See: https://googlechrome.github.io/samples/service-worker/windowclient-navigate/
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked:', event.action || 'default');

  const data = event.notification.data || {};

  // Handle "dismiss" action - acknowledge the event to backend
  if (event.action === 'dismiss') {
    event.notification.close();

    // Call public acknowledge API (no auth required)
    if (data.alert_id && data.triggered_at && data.user_id) {
      const timestamp = Math.floor(new Date(data.triggered_at).getTime() / 1000);
      const apiUrl = `${self.location.origin}/api/alert-events/acknowledge-public?alert_id=${data.alert_id}&timestamp=${timestamp}&user_id=${data.user_id}`;

      event.waitUntil(
        fetch(apiUrl, { method: 'POST' })
          .then(response => {
            if (response.ok) {
              console.log('[Service Worker] Event acknowledged successfully');
            } else {
              console.error('[Service Worker] Failed to acknowledge event:', response.status);
            }
          })
          .catch(err => {
            console.error('[Service Worker] Error acknowledging event:', err);
          })
      );
    }
    return;
  }

  // Handle "view" action or default click - open app and navigate to ticker
  event.notification.close();

  const ticker = data.ticker || '';
  // Prefer an explicit deep link (setup-alert pushes carry the cockpit URL in
  // data.heatmap_url); fall back to the legacy ticker heatmap for node alerts.
  const deepLink = data.heatmap_url || data.url || (ticker ? `/?symbol=${ticker}` : '/');
  // Always re-based onto THIS origin — a payload-supplied absolute url would
  // otherwise win over the base and navigate out of the app. See sameOriginURL.
  const urlToOpen = sameOriginURL(deepLink);
  console.log('[Service Worker] Target URL:', urlToOpen);

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(async (clientList) => {
      console.log('[Service Worker] Found', clientList.length, 'open window(s)');

      // Log all client URLs for debugging
      clientList.forEach((c, i) => {
        console.log(`[Service Worker] Client ${i}: ${c.url}`);
      });

      if (clientList.length > 0) {
        // Priority 1: Find a window already on the dashboard (/)
        let targetClient = clientList.find(c => {
          try {
            const url = new URL(c.url);
            return url.pathname === '/';
          } catch {
            return false;
          }
        });

        // Priority 2: Any window on our origin (not on config pages preferably)
        if (!targetClient) {
          targetClient = clientList.find(c => {
            try {
              const url = new URL(c.url);
              return !url.pathname.startsWith('/alerts') &&
                     !url.pathname.startsWith('/settings') &&
                     !url.pathname.startsWith('/accounts');
            } catch {
              return false;
            }
          });
        }

        // Priority 3: Any focusable window
        if (!targetClient) {
          targetClient = clientList.find(c => 'focus' in c);
        }

        if (targetClient) {
          console.log('[Service Worker] Focusing client:', targetClient.url);

          try {
            // Focus the window first
            const focusedClient = await targetClient.focus();
            console.log('[Service Worker] Client focused');

            // PRIMARY: Try navigate() - works in Chrome (since v49), Edge, Firefox
            // See: https://googlechrome.github.io/samples/service-worker/windowclient-navigate/
            if ('navigate' in focusedClient) {
              console.log('[Service Worker] Using navigate() method');
              try {
                await focusedClient.navigate(urlToOpen);
                console.log('[Service Worker] navigate() succeeded');
                return focusedClient;
              } catch (navError) {
                console.warn('[Service Worker] navigate() failed:', navError);
                // Fall through to postMessage
              }
            }

            // FALLBACK: postMessage for Safari or when navigate() fails
            // The NotificationNavigationProvider in the app will handle this message
            console.log('[Service Worker] Using postMessage fallback');
            focusedClient.postMessage({
              type: 'NAVIGATE_TO',
              url: urlToOpen,
              ticker: ticker
            });

            return focusedClient;
          } catch (focusError) {
            console.error('[Service Worker] Focus failed:', focusError);
            // Fall through to openWindow
          }
        }
      }

      // No existing window found or focus failed - open a new one
      // Store pending navigation for iOS PWA where openWindow URL params are ignored
      console.log('[Service Worker] No existing window, storing pending navigation and opening app');
      if (ticker) {
        try {
          await storePendingNavigation(ticker, urlToOpen);
        } catch (err) {
          console.warn('[Service Worker] Failed to store pending navigation:', err);
        }
      }
      return clients.openWindow(urlToOpen);
    })
  );
});

// Background sync event - for offline functionality
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);

  if (event.tag === 'sync-alerts') {
    event.waitUntil(
      // Fetch latest alerts when back online
      fetch('/api/alerts')
        .then((response) => response.json())
        .then((data) => {
          console.log('[Service Worker] Synced alerts:', data);
        })
        .catch((error) => {
          console.error('[Service Worker] Sync failed:', error);
        })
    );
  }
});

// Message event - handle messages from the main app
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[Service Worker] SKIP_WAITING - calling skipWaiting()');
    // Just call skipWaiting - don't wait for promise or call clients.claim()
    // The activate event will handle clients.claim() when this worker activates
    // This avoids Chrome bug where skipWaiting() hangs with pending fetch requests
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_CLEAR') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            return caches.delete(cacheName);
          })
        );
      })
    );
  }
});
