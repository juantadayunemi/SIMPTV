#!/usr/bin/env node

/**
 * Master script to test complete FCM setup (frontend + backend)
 * Run with: node scripts/test-fcm-complete.cjs
 */

const { spawn } = require('child_process');
const path = require('path');

// Load environment variables from .env file
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

console.log('🔥 Testing Complete Firebase Cloud Messaging Setup\n');
console.log('=' .repeat(60));

let frontendOk = false;
let backendOk = false;

// Test Frontend Configuration
console.log('📱 Testing Frontend Configuration...\n');

const frontendTest = spawn('node', ['scripts/test-fcm-config.cjs'], {
  cwd: __dirname + '/../',
  stdio: 'pipe'
});

let frontendOutput = '';
frontendTest.stdout.on('data', (data) => {
  frontendOutput += data.toString();
});

frontendTest.stderr.on('data', (data) => {
  console.error('Frontend test error:', data.toString());
});

frontendTest.on('close', (code) => {
  if (code === 0) {
    console.log('✅ Frontend configuration: PASSED\n');
    frontendOk = true;
  } else {
    console.log('❌ Frontend configuration: FAILED\n');
  }

  // Test Backend Configuration
  console.log('🔧 Testing Backend Configuration...\n');

  const backendTest = spawn('python', ['scripts/test_fcm_notifications.py', '--check-config'], {
    cwd: __dirname + '/../../backend',
    stdio: 'pipe'
  });

  let backendOutput = '';
  backendTest.stdout.on('data', (data) => {
    backendOutput += data.toString();
  });

  backendTest.stderr.on('data', (data) => {
    console.error('Backend test error:', data.toString());
  });

  backendTest.on('close', (backendCode) => {
    if (backendCode === 0) {
      console.log('✅ Backend configuration: PASSED\n');
      backendOk = true;
    } else {
      console.log('❌ Backend configuration: FAILED\n');
      console.log('Backend output:', backendOutput);
    }

    // Final Summary
    console.log('=' .repeat(60));
    console.log('📊 FINAL RESULTS:\n');

    if (frontendOk && backendOk) {
      console.log('🎉 COMPLETE FCM SETUP SUCCESSFUL!');
      console.log('\n✅ Frontend: Firebase environment variables configured');
      console.log('✅ Backend: Firebase service account configured');
      console.log('\n🚀 Next steps:');
      console.log('1. Start your development servers:');
      console.log('   - Backend: python manage.py runserver');
      console.log('   - Frontend: npm run dev');
      console.log('2. Go to http://localhost:5173/notifications');
      console.log('3. Enable push notifications in your browser');
      console.log('4. Test notifications: python backend/scripts/test_fcm_notifications.py');
    } else {
      console.log('⚠️  FCM SETUP INCOMPLETE');
      console.log('\nIssues found:');

      if (!frontendOk) {
        console.log('❌ Frontend: Check Firebase environment variables in .env file');
        console.log('   Run: npm run test-fcm');
      }

      if (!backendOk) {
        console.log('❌ Backend: Check Firebase service account configuration');
        console.log('   File: backend/config/firebase-service-account.json');
      }

      console.log('\n🔗 Firebase Console: https://console.firebase.google.com/');
      console.log('📚 Documentation: frontend/FCM_SETUP.md');
    }

    console.log('\n' + '=' .repeat(60));
  });
});