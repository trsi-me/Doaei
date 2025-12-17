// Service Worker لمنصة دوائي
// إدارة التذكيرات والإشعارات

const CACHE_NAME = 'doaei-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js'
    // إزالة الملفات التي قد لا تكون موجودة
    // '/static/images/Logo.webp',
    // '/static/images/icon.png'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('تم فتح التخزين المؤقت');
                // إضافة الملفات واحداً تلو الآخر لتجنب الأخطاء
                return Promise.allSettled(
                    urlsToCache.map(url =>
                        cache.add(url).catch(error => {
                            console.warn(`فشل في إضافة ${url} إلى التخزين المؤقت:`, error);
                            return null;
                        })
                    )
                );
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('حذف التخزين المؤقت القديم:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// اعتراض الطلبات
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // إرجاع الملف من التخزين المؤقت إذا كان متوفراً
                if (response) {
                    return response;
                }

                // جلب الملف من الشبكة
                return fetch(event.request);
            }
            )
    );
});

// معالجة الإشعارات
self.addEventListener('notificationclick', event => {
    event.notification.close();

    // فتح التطبيق عند النقر على الإشعار
    event.waitUntil(
        clients.openWindow('/')
    );
});

// معالجة رسائل الخادم
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// إرسال إشعارات التذكيرات
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'تذكير دواء جديد',
        icon: '/static/images/Icon.ico',
        badge: '/static/images/Icon.ico',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'فتح التطبيق',
                icon: '/static/images/Icon.ico'
            },
            {
                action: 'close',
                title: 'إغلاق',
                icon: '/static/images/Icon.ico'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('دوائي - تذكير دواء', options)
    );
});
