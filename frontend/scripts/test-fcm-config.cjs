#!/usr/bin/env node

/**
 * Script to test FCM configuration
 * Run with: node scripts/test-fcm-config.js
 */

const path = require('path');

// Load environment variables from .env file
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

console.log('🔥 Testing Firebase Cloud Messaging Configuration\n');

// Check if required environment variables are set
const requiredEnvVars = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_MESSAGING_SENDER_ID',
  'VITE_FIREBASE_APP_ID'
];

// Placeholder patterns to check for
const placeholderPatterns = [
  /your-.*-key/i,
  /your-.*-id/i,
  /your-.*-sender/i,
  /your-.*-app/i,
  /placeholder/i,
  /replace.*with/i,
  /get.*from.*console/i
];

let allSet = true;

console.log('📋 Checking Firebase environment variables:\n');

requiredEnvVars.forEach(varName => {
  const value = process.env[varName];
  if (!value) {
    console.log(`❌ ${varName}: NOT SET`);
    allSet = false;
  } else {
    // Check if value looks like a placeholder
    const isPlaceholder = placeholderPatterns.some(pattern => pattern.test(value));

    if (isPlaceholder) {
      console.log(`⚠️  ${varName}: SET but appears to be placeholder - ${value}`);
      allSet = false;
    } else {
      console.log(`✅ ${varName}: SET - ${value.substring(0, 20)}...`);
    }
  }
});

// Additional validation for specific formats
console.log('\n🔍 Additional format validation:\n');

// Check API Key format (Firebase API keys start with AIzaSy)
const apiKey = process.env.VITE_FIREBASE_API_KEY;
if (apiKey && !apiKey.startsWith('AIzaSy')) {
  console.log('⚠️  VITE_FIREBASE_API_KEY: Should start with "AIzaSy"');
  allSet = false;
} else if (apiKey) {
  console.log('✅ VITE_FIREBASE_API_KEY: Valid format');
}

// Check Sender ID format (should be numeric)
const senderId = process.env.VITE_FIREBASE_MESSAGING_SENDER_ID;
if (senderId && !/^\d+$/.test(senderId)) {
  console.log('⚠️  VITE_FIREBASE_MESSAGING_SENDER_ID: Should be numeric');
  allSet = false;
} else if (senderId) {
  console.log('✅ VITE_FIREBASE_MESSAGING_SENDER_ID: Valid format');
}

// Check App ID format (Firebase App IDs have specific format)
const appId = process.env.VITE_FIREBASE_APP_ID;
if (appId && !/^1:\d+:web:/.test(appId)) {
  console.log('⚠️  VITE_FIREBASE_APP_ID: Should match format "1:NUMBER:web:STRING"');
  allSet = false;
} else if (appId) {
  console.log('✅ VITE_FIREBASE_APP_ID: Valid format');
}

console.log('\n' + '='.repeat(50));

if (allSet) {
  console.log('🎉 All Firebase configuration variables are properly set!');
  console.log('\nNext steps:');
  console.log('1. Make sure your backend has the Firebase service account configured');
  console.log('2. Start your development servers');
  console.log('3. Go to /notifications in the frontend to enable push notifications');
  console.log('4. Test with: python backend/scripts/test_fcm_notifications.py');
} else {
  console.log('⚠️  Some Firebase configuration variables are not set or invalid.');
  console.log('Please update your .env file with the correct values from Firebase Console.');
  console.log('\nTo get these values:');
  console.log('1. Go to https://console.firebase.google.com/');
  console.log('2. Select your project (trafismart)');
  console.log('3. Go to Project Settings > General > Your apps');
  console.log('4. Copy the config values from your web app');
}

console.log('\n📚 For more information, see: frontend/FCM_SETUP.md');