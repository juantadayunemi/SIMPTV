// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// SERVICE WORKER VERSION - Incrementa este número para forzar actualización
const SW_VERSION = 'v2.1.0';
console.log(`[SW] 🚀 Firebase Messaging Service Worker ${SW_VERSION} cargando...`);

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// ATENCIÓN: Este archivo debe ser ignorado por git y contener tus claves reales de Firebase
// Usa el archivo 'firebase-messaging-sw.example.js' como plantilla
firebase.initializeApp({
  apiKey: "AIzaSyDIwDVgzBPD_Eu7iQOmXfxXhPR-Asg5FDQ",
  authDomain: "trafismart.firebaseapp.com",
  projectId: "trafismart",
  storageBucket: "trafismart.firebasestorage.app",
  messagingSenderId: "1069945682048",
  appId: "1:1069945682048:web:7abe29e1b37b25959c43bc"
});

// Retrieve an instance of Firebase Messaging so that it can handle background messages.
const messaging = firebase.messaging();

console.log('[SW] 🚀 Firebase Messaging Service Worker cargado');

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[SW] 📩 Mensaje en background:', payload);
  
  const notificationTitle = payload.notification?.title || '🚨 TrafiSmart';
  
  // Generar TAG ÚNICO para evitar agrupación/deduplicación
  const uniqueTag = payload.data?.plate_number 
    ? `${payload.data.plate_number}-${Date.now()}` 
    : `notification-${Date.now()}`;
  
  // Determinar el sonido según la severidad
  const soundMapping = {
    'default': '/sounds/default.mp3',
    'alert': '/sounds/alert.mp3',
    'urgent': '/sounds/urgent.mp3',
    'alarm': '/sounds/alarm.mp3'
  };
  
  const requestedSound = payload.data?.sound || 'default';
  const soundUrl = soundMapping[requestedSound] || soundMapping['default'];
  
  console.log('[SW] 🔊 Sonido solicitado:', requestedSound, '→', soundUrl);
  
  const notificationOptions = {
    body: payload.notification?.body || 'Nueva notificación',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    tag: uniqueTag, // TAG ÚNICO con timestamp
    requireInteraction: true, // Mantener visible hasta cerrar manualmente
    data: {
      ...payload.data,
      soundUrl: soundUrl // Guardar URL del sonido para uso posterior si es necesario
    },
    vibrate: getVibrationPattern(requestedSound), // Vibración personalizada según severidad
    sound: soundUrl, // Algunos navegadores soportan esto
    actions: [
      {
        action: 'open',
        title: '👀 Ver'
      },
      {
        action: 'close',
        title: '✖️ Cerrar'
      }
    ]
  };

  console.log('[SW] 🔔 Mostrando notificación con tag:', uniqueTag);
  
  // Intentar reproducir sonido (algunos navegadores lo permiten)
  playNotificationSound(soundUrl);
  
  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Función para obtener patrón de vibración según severidad
function getVibrationPattern(sound) {
  const patterns = {
    'default': [200, 100, 200],
    'alert': [300, 100, 300, 100, 300],
    'urgent': [500, 100, 500, 100, 500, 100, 500],
    'alarm': [700, 100, 700, 100, 700, 100, 700, 100, 700]
  };
  return patterns[sound] || patterns['default'];
}

// Función para reproducir sonido personalizado
function playNotificationSound(soundUrl) {
  try {
    // Nota: En Service Workers, reproducir audio es limitado
    // Esta función está preparada para cuando los navegadores lo soporten mejor
    console.log('[SW] 🔊 Intento de reproducir:', soundUrl);
    
    // En el futuro, cuando los navegadores soporten Web Audio API en SW:
    // const audio = new Audio(soundUrl);
    // audio.play().catch(err => console.log('[SW] ⚠️ No se pudo reproducir audio:', err));
  } catch (error) {
    console.log('[SW] ⚠️ Error al reproducir sonido:', error);
  }
}

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] 👆 Click en notificación:', event.action);
  
  event.notification.close();
  
  if (event.action === 'close') {
    // Solo cerrar
    return;
  }
  
  // Abrir o enfocar la app
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Si ya hay ventana abierta, enfocarla
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus();
          }
        }
        // Si no, abrir nueva ventana
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});

console.log(`[SW] ✅ Service Worker ${SW_VERSION} - Handlers registrados correctamente`);