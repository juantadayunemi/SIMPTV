import { useEffect, useState, useCallback } from 'react';
import { fcmService, FCMDevice } from '../services/fcm.service';
import { useAuth } from './useAuth';
import toast from 'react-hot-toast';

export const useFCM = () => {
  const { user } = useAuth();
  const [isSupported, setIsSupported] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [devices, setDevices] = useState<FCMDevice[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Check if FCM is supported
  useEffect(() => {
    const checkSupport = () => {
      const supported = fcmService.isSupported();
      setIsSupported(supported);

      if (supported && 'Notification' in window) {
        setPermission(Notification.permission);
      }
    };

    checkSupport();
  }, []);

  // Initialize FCM when user is logged in
  useEffect(() => {
    if (user && isSupported) {
      const initializeFCM = async () => {
        try {
          await fcmService.initialize();
          await loadDevices();
        } catch (error) {
          console.error('Error initializing FCM:', error);
        }
      };

      initializeFCM();
    }
  }, [user, isSupported]);

  // Load user's registered devices
  const loadDevices = useCallback(async () => {
    if (!user) return;

    try {
      const userDevices = await fcmService.getDevices();
      setDevices(userDevices);
    } catch (error) {
      console.error('Error loading devices:', error);
    }
  }, [user]);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!isSupported) {
      toast.error('Las notificaciones no están soportadas en este navegador');
      return false;
    }

    try {
      setIsLoading(true);
      const newPermission = await fcmService.requestPermission();
      setPermission(newPermission);

      if (newPermission === 'granted') {
        toast.success('Permisos de notificación concedidos');
        // Register token automatically
        const registered = await fcmService.registerToken();
        if (registered) {
          await loadDevices();
          toast.success('Dispositivo registrado para notificaciones');
        }
        return true;
      } else {
        toast.error('Permisos de notificación denegados');
        return false;
      }
    } catch (error) {
      console.error('Error requesting permission:', error);
      toast.error('Error al solicitar permisos');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [isSupported, loadDevices]);

  // Register FCM token manually
  const registerToken = useCallback(async (deviceName?: string) => {
    try {
      setIsLoading(true);
      const registered = await fcmService.registerToken(deviceName);
      if (registered) {
        await loadDevices();
        toast.success('Token FCM registrado exitosamente');
        return true;
      } else {
        toast.error('Error al registrar el token FCM');
        return false;
      }
    } catch (error) {
      console.error('Error registering token:', error);
      toast.error('Error al registrar el token');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [loadDevices]);

  // Send test notification
  const sendTestNotification = useCallback(async (title?: string, body?: string) => {
    try {
      setIsLoading(true);
      const result = await fcmService.sendTestNotification({ title, body });
      toast.success('Notificación de prueba enviada');
      return result;
    } catch (error) {
      console.error('Error sending test notification:', error);
      toast.error('Error al enviar notificación de prueba');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Deactivate device
  const deactivateDevice = useCallback(async (deviceId: number) => {
    try {
      setIsLoading(true);
      await fcmService.deactivateDevice(deviceId);
      await loadDevices();
      toast.success('Dispositivo desactivado');
    } catch (error) {
      console.error('Error deactivating device:', error);
      toast.error('Error al desactivar dispositivo');
    } finally {
      setIsLoading(false);
    }
  }, [loadDevices]);

  return {
    // State
    isSupported,
    permission,
    devices,
    isLoading,

    // Actions
    requestPermission,
    registerToken,
    sendTestNotification,
    deactivateDevice,
    loadDevices,
  };
};