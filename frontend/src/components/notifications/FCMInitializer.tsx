import React, { useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useFCM } from '../../hooks/useFCM';
import toast from 'react-hot-toast';
import { AlertTriangle, Car, DollarSign, Bell, X } from 'lucide-react';

export const FCMInitializer: React.FC = () => {
  const { user } = useAuth();
  const { isSupported } = useFCM();

  useEffect(() => {
    // Only initialize FCM if user is logged in and FCM is supported
    if (user && isSupported) {
      console.log('🔥 Initializing Firebase Cloud Messaging...');

      // Import and initialize FCM dynamically
      import('../../services/fcm.service').then(({ fcmService }) => {
        fcmService.initialize().catch((error) => {
          console.error('Failed to initialize FCM:', error);
        });

        // Listen for foreground messages
        const unsubscribe = fcmService.onMessage((payload) => {
          console.log('📨 Nueva notificación recibida:', payload);
          
          // Show visual notification toast
          showNotificationToast(payload);

          // Play notification sound (optional)
          playNotificationSound();

          // Show browser notification if available
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(payload.notification?.title || 'TrafiSmart', {
              body: payload.notification?.body || 'Nueva notificación',
              icon: '/icon-192x192.png',
              badge: '/badge-72x72.png',
              tag: payload.data?.type || 'notification',
              requireInteraction: true,
              data: payload.data,
            });
          }
        });

        // Cleanup on unmount
        return () => {
          if (typeof unsubscribe === 'function') {
            unsubscribe();
          }
        };
      }).catch((error) => {
        console.error('Failed to load FCM service:', error);
      });
    }
  }, [user, isSupported]);

  const showNotificationToast = (payload: any) => {
    const type = payload.data?.type || 'general';
    const title = payload.notification?.title || 'Notificación';
    const body = payload.notification?.body || '';
    const data = payload.data || {};

    // Save notification to store
    notificationStore.addNotification({
      title,
      body,
      type: type as any,
      data,
    });

    // Get icon and color based on notification type
    const getNotificationConfig = (type: string) => {
      switch (type) {
        case 'stolen_vehicle':
          return {
            icon: <AlertTriangle className="text-red-500" size={28} />,
            bgColor: 'bg-red-50',
            borderColor: 'border-red-200',
            emoji: '🚨',
          };
        case 'traffic_violation':
          return {
            icon: <Car className="text-yellow-500" size={28} />,
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-200',
            emoji: '⚠️',
          };
        case 'payment_reminder':
          return {
            icon: <DollarSign className="text-blue-500" size={28} />,
            bgColor: 'bg-blue-50',
            borderColor: 'border-blue-200',
            emoji: '💳',
          };
        default:
          return {
            icon: <Bell className="text-gray-500" size={28} />,
            bgColor: 'bg-gray-50',
            borderColor: 'border-gray-200',
            emoji: '🔔',
          };
      }
    };

    const config = getNotificationConfig(type);

    toast.custom((t) => (
      <div
        className={`${
          t.visible ? 'animate-enter' : 'animate-leave'
        } max-w-md w-full ${config.bgColor} shadow-xl rounded-lg pointer-events-auto flex ring-2 ${config.borderColor}`}
      >
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 pt-1">
              {config.icon}
            </div>
            <div className="ml-3 flex-1">
              <p className="text-base font-bold text-gray-900 flex items-center gap-2">
                <span>{config.emoji}</span>
                {title}
              </p>
              <p className="mt-1 text-sm text-gray-700">
                {body}
              </p>
              {data.plate && (
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-white border border-gray-300">
                    <span className="font-semibold">Placa:</span>
                    <span className="ml-1 font-mono font-bold">{data.plate}</span>
                  </span>
                  {data.location && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-white border border-gray-300">
                      <span className="font-semibold">📍</span>
                      <span className="ml-1 text-xs">{data.location}</span>
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-gray-500 hover:text-gray-700 focus:outline-none transition"
          >
            <X size={20} />
          </button>
        </div>
      </div>
    ), {
      duration: 10000,
      position: 'top-right',
    });
  };

  const playNotificationSound = () => {
    try {
      // Create a simple notification beep
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
    } catch (error) {
      // Silently fail if audio context is not available
      console.log('Audio notification not available');
    }
  };

  // This component doesn't render anything
  return null;
};