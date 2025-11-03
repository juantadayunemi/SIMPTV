import React, { useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useFCM } from '../../hooks/useFCM';
import { fcmService } from '../../services/fcm.service';

export const FCMInitializer: React.FC = () => {
  const { user } = useAuth();
  const { isSupported } = useFCM();

  useEffect(() => {
    if (!user || !isSupported) return;

    const initializeFCM = async () => {
      try {
        console.log('🔥 Initializing Firebase Cloud Messaging...');

        // Limpiar cache anterior si es necesario (debug)
        // localStorage.removeItem('fcm_registered_token');

        // Inicializar el servicio FCM
        // Esto ya incluye registerToken() internamente
        await fcmService.initialize();

        console.log('✅ FCM service initialized successfully');
      } catch (error: any) {
        console.error('Failed to initialize FCM:', error);
      }
    };

    initializeFCM();
  }, [user, isSupported]);

  return null;
};