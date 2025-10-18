import { initializeApp } from 'firebase/app';
import { getMessaging, Messaging } from 'firebase/messaging';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAWC8V0gXLw9X8PsUVnqhGtHBQtvpgkqV0",
  authDomain: "trafismart.firebaseapp.com",
  projectId: "trafismart",
  storageBucket: "trafismart.firebasestorage.app",
  messagingSenderId: "134462786929",
  appId: "1:134462786929:web:17c2c53227d113c0a53ad0",
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