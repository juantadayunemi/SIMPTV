import { messaging } from '../config/firebase';
import { getToken, onMessage } from 'firebase/messaging';
import api from './api';
import toast from 'react-hot-toast';

export interface FCMTokenData {
  token: string;
  device_name?: string;
  device_type?: 'ios' | 'android' | 'web' | 'other';
}

export interface FCMDevice {
  id: number;
  device_name: string;
  device_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_used_at?: string;
}

export interface TestNotificationData {
  title?: string;
  body?: string;
}

class FCMService {
 private vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY; 

  /**
   * Check if FCM is supported in this browser
   */
  isSupported(): boolean {
    return !!messaging && 'serviceWorker' in navigator && 'Notification' in window;
  }

  /**
   * Request notification permission from the user
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      throw new Error('This browser does not support notifications');
    }

    const permission = await Notification.requestPermission();
    return permission;
  }

  /**
   * Get FCM token for this device
   */
  async getToken(): Promise<string | null> {
    if (!messaging) {
      console.warn('Firebase Messaging not initialized');
      return null;
    }

    try {
      const permission = await this.requestPermission();
      if (permission !== 'granted') {
        console.warn('Notification permission not granted');
        return null;
      }

      const token = await getToken(messaging, {
        vapidKey: this.vapidKey,
      });

      return token;
    } catch (error) {
      console.error('Error getting FCM token:', error);
      return null;
    }
  }

  /**
   * Register FCM token with the backend
   */
  async registerToken(deviceName?: string, deviceType?: 'ios' | 'android' | 'web' | 'other'): Promise<boolean> {
    try {
      const token = await this.getToken();
      if (!token) {
        return false;
      }

      const data: FCMTokenData = {
        token,
        device_name: deviceName || this.getDeviceName(),
        device_type: deviceType || this.getDeviceType(),
      };

      await api.post('/api/notifications/devices/register_token/', data);
      console.log('FCM token registered successfully');
      return true;
    } catch (error) {
      console.error('Error registering FCM token:', error);
      return false;
    }
  }

  /**
   * Listen for incoming messages when app is in foreground
   */
  onMessage(callback: (payload: any) => void): () => void {
    if (!messaging) {
      console.warn('Firebase Messaging not initialized');
      return () => {};
    }

    return onMessage(messaging, (payload) => {
      console.log('Message received in foreground:', payload);
      callback(payload);

      // Show toast notification
      if (payload.notification) {
        toast(payload.notification.title || 'Notificación', {
          duration: 5000,
        });
        // Also show the body as a separate toast or handle it differently
        if (payload.notification && payload.notification.body) {
          setTimeout(() => {
            toast(payload.notification.body, { duration: 4000 });
          }, 500);
        }
      }
    });
  }

  /**
   * Send test notification
   */
  async sendTestNotification(data: TestNotificationData = {}): Promise<any> {
    try {
      const response = await api.post('/api/notifications/notifications/send_test/', data);
      return response.data;
    } catch (error) {
      console.error('Error sending test notification:', error);
      throw error;
    }
  }

  /**
   * Get user's registered devices
   */
  async getDevices(): Promise<FCMDevice[]> {
    try {
      const response = await api.get('/api/notifications/devices/');
      return response.data;
    } catch (error) {
      console.error('Error getting devices:', error);
      return [];
    }
  }

  /**
   * Deactivate a device
   */
  async deactivateDevice(deviceId: number): Promise<void> {
    try {
      await api.delete(`/api/notifications/devices/${deviceId}/deactivate/`);
    } catch (error) {
      console.error('Error deactivating device:', error);
      throw error;
    }
  }

  /**
   * Get device name based on user agent
   */
  private getDeviceName(): string {
    const userAgent = navigator.userAgent;
    const platform = navigator.platform;

    if (userAgent.includes('Mobile')) {
      return 'Dispositivo Móvil';
    } else if (platform.includes('Mac')) {
      return 'Mac';
    } else if (platform.includes('Win')) {
      return 'Windows PC';
    } else if (platform.includes('Linux')) {
      return 'Linux PC';
    }

    return 'Dispositivo Desconocido';
  }

  /**
   * Get device type based on user agent
   */
  private getDeviceType(): 'ios' | 'android' | 'web' | 'other' {
    const userAgent = navigator.userAgent;

    if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      return 'ios';
    } else if (userAgent.includes('Android')) {
      return 'android';
    }

    return 'web';
  }

  /**
   * Initialize FCM service (call this when app starts)
   */
  async initialize(): Promise<void> {
    if (!this.isSupported()) {
      console.warn('FCM not supported in this browser');
      return;
    }

    try {
      // Register service worker for background messages
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
        console.log('Service Worker registered:', registration);
      }

      // Try to register token automatically
      await this.registerToken();

      // Listen for foreground messages
      this.onMessage((payload) => {
        // Handle foreground messages
        console.log('Foreground message:', payload);
      });

    } catch (error) {
      console.error('Error initializing FCM:', error);
    }
  }
}

export const fcmService = new FCMService();
export default fcmService;