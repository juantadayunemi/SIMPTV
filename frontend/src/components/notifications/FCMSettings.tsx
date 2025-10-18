import React from 'react';
import { Bell, BellOff, Smartphone, Monitor, Trash2 } from 'lucide-react';
import { useFCM } from '../../hooks/useFCM';
import { Button } from '../ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export const FCMSettings: React.FC = () => {
  const {
    isSupported,
    permission,
    devices,
    isLoading,
    requestPermission,
    registerToken,
    sendTestNotification,
    deactivateDevice,
  } = useFCM();

  const handleRequestPermission = async () => {
    const granted = await requestPermission();
    if (granted) {
      await registerToken();
    }
  };

  const handleTestNotification = async () => {
    try {
      await sendTestNotification(
        'Notificación de Prueba',
        'Esta es una notificación de prueba del sistema TrafiSmart'
      );
    } catch (error) {
      // Error already handled in hook
    }
  };

  const handleDeactivateDevice = async (deviceId: number, deviceName: string) => {
    if (window.confirm(`¿Estás seguro de que quieres desactivar "${deviceName}"?`)) {
      await deactivateDevice(deviceId);
    }
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case 'ios':
      case 'android':
        return <Smartphone className="h-4 w-4" />;
      case 'web':
        return <Monitor className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };

  const getPermissionBadge = (permission: NotificationPermission) => {
    switch (permission) {
      case 'granted':
        return <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">Concedido</span>;
      case 'denied':
        return <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">Denegado</span>;
      default:
        return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">Pendiente</span>;
    }
  };

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="h-5 w-5" />
            Notificaciones Push
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Las notificaciones push no están soportadas en este navegador.
          </p>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Permission Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Estado de Notificaciones
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Gestiona los permisos y configuración de notificaciones push
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Permisos del navegador</p>
              <p className="text-sm text-muted-foreground">
                Estado actual: {getPermissionBadge(permission)}
              </p>
            </div>
            {permission !== 'granted' && (
              <Button
                onClick={handleRequestPermission}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <Bell className="h-4 w-4" />
                {isLoading ? 'Solicitando...' : 'Activar Notificaciones'}
              </Button>
            )}
          </div>

          {permission === 'granted' && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div>
                <p className="font-medium">Probar notificaciones</p>
                <p className="text-sm text-muted-foreground">
                  Envía una notificación de prueba a tus dispositivos
                </p>
              </div>
              <Button
                variant="secondary"
                onClick={handleTestNotification}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <Bell className="h-4 w-4" />
                {isLoading ? 'Enviando...' : 'Probar'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Registered Devices */}
      {devices.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Dispositivos Registrados</CardTitle>
            <p className="text-sm text-muted-foreground">
              Dispositivos que recibirán notificaciones push
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {devices.map((device) => (
                <div
                  key={device.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getDeviceIcon(device.device_type)}
                    <div>
                      <p className="font-medium">
                        {device.device_name || `Dispositivo ${device.id}`}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {device.device_type} • Registrado: {new Date(device.created_at).toLocaleDateString()}
                        {device.last_used_at && (
                          <> • Último uso: {new Date(device.last_used_at).toLocaleDateString()}</>
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      device.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {device.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleDeactivateDevice(device.id, device.device_name)}
                      disabled={isLoading}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Information */}
      <Card>
        <CardHeader>
          <CardTitle>Información</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            • Las notificaciones push te alertarán sobre vehículos robados detectados
          </p>
          <p>
            • Recibirás alertas de infracciones de tránsito en tiempo real
          </p>
          <p>
            • Los dispositivos se registran automáticamente al conceder permisos
          </p>
          <p>
            • Puedes desactivar dispositivos individuales si ya no los usas
          </p>
        </CardContent>
      </Card>
    </div>
  );
};