import React from 'react';
import { FCMSettings } from '../../components/notifications/FCMSettings';

export const NotificationsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notificaciones</h1>
        <p className="text-gray-600">Gestiona las notificaciones push y alertas del sistema</p>
      </div>

      <FCMSettings />
    </div>
  );
};

export default NotificationsPage;