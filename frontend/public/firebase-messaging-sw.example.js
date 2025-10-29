// Ejemplo de configuración para el service worker de Firebase Messaging
// Copia este archivo como 'firebase-messaging-sw.js' y coloca tus claves reales de Firebase
// NO subas el archivo con claves reales al repositorio (usa .gitignore)
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "TU_API_KEY_AQUI",
  authDomain: "trafismart.firebaseapp.com",
  projectId: "trafismart",
  storageBucket: "trafismart.firebasestorage.app",
  messagingSenderId: "TU_MESSAGING_SENDER_ID_AQUI",
  appId: "TU_APP_ID_AQUI",
  measurementId: "G-075GGFQXVL"
});

const messaging = firebase.messaging();
// ...resto del código igual...