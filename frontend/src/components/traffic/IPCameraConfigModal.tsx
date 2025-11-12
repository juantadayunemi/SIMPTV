/**
 * IPCameraConfigModal
 * Modal para configurar la dirección IP de cámaras móviles (DroidCam, IP Webcam, etc.)
 */
import React, { useState, useEffect } from 'react';
import { X, Wifi, AlertCircle, CheckCircle } from 'lucide-react';

interface IPCameraConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (ipUrl: string) => void;
  currentIp?: string;
}

export const IPCameraConfigModal: React.FC<IPCameraConfigModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  currentIp = ''
}) => {
  const [ipAddress, setIpAddress] = useState('');
  const [port, setPort] = useState('8080');
  const [error, setError] = useState('');
  const [testing, setTesting] = useState(false);
  const [testSuccess, setTestSuccess] = useState(false);

  // Inicializar campos si ya hay una IP configurada
  useEffect(() => {
    if (currentIp && isOpen) {
      try {
        const url = new URL(currentIp);
        setIpAddress(url.hostname);
        setPort(url.port || '8080');
      } catch (e) {
        // Si no se puede parsear, usar valores por defecto
        setIpAddress('');
        setPort('8080');
      }
    } else if (isOpen) {
      // Valores por defecto al abrir
      setIpAddress('');
      setPort('8080');
    }
  }, [currentIp, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validar formato de IP
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    if (!ipRegex.test(ipAddress)) {
      setError('Formato de IP inválido. Ejemplo: 192.168.1.3 o 10.10.111.112');
      return;
    }

    // Validar puerto
    const portNum = parseInt(port);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
      setError('Puerto inválido. Debe estar entre 1 y 65535');
      return;
    }

    const fullUrl = `http://${ipAddress}:${port}/video`;
    onConfirm(fullUrl);
  };

  const handleTest = async () => {
    setTesting(true);
    setError('');
    setTestSuccess(false);
    
    const testUrl = `http://${ipAddress}:${port}/video`;
    
    try {
      const testImg = new Image();
      
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Timeout: No se pudo conectar en 5 segundos'));
        }, 5000);
        
        testImg.onload = () => {
          clearTimeout(timeout);
          resolve();
        };
        
        testImg.onerror = () => {
          clearTimeout(timeout);
          reject(new Error('No se pudo conectar a la cámara'));
        };
        
        testImg.src = testUrl + '?t=' + Date.now();
      });
      
      setTestSuccess(true);
      setError('');
    } catch (err) {
      setTestSuccess(false);
      setError(`❌ No se pudo conectar. Verifica que:
1. IP Webcam esté en "Start server"
2. La IP y puerto sean correctos (IP: ${ipAddress}, Puerto: ${port})
3. Ambos dispositivos estén en la misma red WiFi`);
    } finally {
      setTesting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center space-x-2">
              <Wifi className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                Configurar Cámara IP
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Instrucciones */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                📱 <strong>Paso 1:</strong> Abre IP Webcam en tu celular<br />
                📱 <strong>Paso 2:</strong> Presiona "Start server"<br />
                📱 <strong>Paso 3:</strong> Ingresa la IP IPv4 que muestra (ej: 192.168.1.3:8080)
              </p>
            </div>

            {/* IP Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dirección IP *
              </label>
              <input
                type="text"
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                placeholder="192.168.1.3"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Ejemplo: 192.168.1.3 (la IP IPv4 que muestra IP Webcam)
              </p>
            </div>

            {/* Port */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Puerto *
              </label>
              <input
                type="text"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                placeholder="8080"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                IP Webcam usa por defecto el puerto 8080
              </p>
            </div>

            {/* Preview URL */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-xs text-gray-600 mb-1">URL completa:</p>
              <code className="text-sm text-gray-900 break-all">
                http://{ipAddress || '___.___.___.___ '}:{port}/video
              </code>
            </div>

            {/* Test Success Message */}
            {testSuccess && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <p className="text-sm text-green-700 font-medium">
                    ✅ Conexión exitosa! La cámara está respondiendo.
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
                </div>
              </div>
            )}

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={!ipAddress || !port}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ✅ Conectar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
