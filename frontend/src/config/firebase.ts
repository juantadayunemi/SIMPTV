import { initializeApp } from 'firebase/app';
import { getMessaging, Messaging } from 'firebase/messaging';

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: "trafismart.firebaseapp.com",
  projectId: "trafismart",
  storageBucket: "trafismart.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: "G-075GGFQXVL"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging
let messaging: Messaging | null = null;

try {
  // Check if messaging is supported
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    messaging = getMessaging(app);
  }
} catch (error) {
  console.warn('Firebase Messaging not supported:', error);
}

export { messaging };
export default app;