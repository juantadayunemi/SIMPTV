import React, { useState, useEffect } from 'react';

interface SystemConfig {
  siteName: string;
  maxAnalysisTime: number;
  autoDeleteOldData: boolean;
  dataRetentionDays: number;
  enableNotifications: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  maxConcurrentAnalysis: number;
  debugMode: boolean;
  logLevel: 'ERROR' | 'WARN' | 'INFO' | 'DEBUG';
  maintenanceMode: boolean;
  allowRegistration: boolean;
  sessionTimeout: number;
}

const defaultConfig: SystemConfig = {
  siteName: 'TrafiSmart',
  maxAnalysisTime: 30,
  autoDeleteOldData: true,
  dataRetentionDays: 90,
  enableNotifications: true,
  emailNotifications: true,
  smsNotifications: false,
  maxConcurrentAnalysis: 5,
  debugMode: false,
  logLevel: 'INFO',
  maintenanceMode: false,
  allowRegistration: true,
  sessionTimeout: 60
};

export const SystemSettingsSection: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig>(defaultConfig);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      // Simulate API call - replace with actual service call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Load from localStorage as fallback
      const savedConfig = localStorage.getItem('systemConfig');
      if (savedConfig) {
        setConfig({ ...defaultConfig, ...JSON.parse(savedConfig) });
      }
    } catch (error) {
      console.error('Error loading config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (key: keyof SystemConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Simulate API call - replace with actual service call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Save to localStorage as fallback
      localStorage.setItem('systemConfig', JSON.stringify(config));
      
      setHasChanges(false);
      alert('Configuración guardada exitosamente');
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Error al guardar la configuración');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('¿Estás seguro de que quieres restablecer la configuración por defecto?')) {
      setConfig(defaultConfig);
      setHasChanges(true);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Save Changes Banner */}
      {hasChanges && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="text-yellow-600 mr-3">⚠️</div>
              <div>
                <h4 className="text-sm font-medium text-yellow-800">
                  Tienes cambios sin guardar
                </h4>
                <p className="text-sm text-yellow-700">
                  Asegúrate de guardar los cambios antes de salir de esta página.
                </p>
              </div>
            </div>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
            >
              {saving ? 'Guardando...' : 'Guardar Ahora'}
            </button>
          </div>
        </div>
      )}

      {/* General Settings */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Configuración General</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre del Sitio
              </label>
              <input
                type="text"
                value={config.siteName}
                onChange={(e) => handleConfigChange('siteName', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nivel de Log
              </label>
              <select
                value={config.logLevel}
                onChange={(e) => handleConfigChange('logLevel', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="ERROR">Error</option>
                <option value="WARN">Warning</option>
                <option value="INFO">Info</option>
                <option value="DEBUG">Debug</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tiempo máximo de análisis (minutos)
              </label>
              <input
                type="number"
                min="1"
                max="120"
                value={config.maxAnalysisTime}
                onChange={(e) => handleConfigChange('maxAnalysisTime', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Análisis concurrentes máximos
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={config.maxConcurrentAnalysis}
                onChange={(e) => handleConfigChange('maxConcurrentAnalysis', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tiempo de expiración de sesión (minutos)
            </label>
            <input
              type="number"
              min="5"
              max="480"
              value={config.sessionTimeout}
              onChange={(e) => handleConfigChange('sessionTimeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Gestión de Datos</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Eliminar datos antiguos automáticamente</h4>
              <p className="text-sm text-gray-600">Elimina automáticamente análisis y datos antiguos</p>
            </div>
            <button
              type="button"
              onClick={() => handleConfigChange('autoDeleteOldData', !config.autoDeleteOldData)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                config.autoDeleteOldData ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config.autoDeleteOldData ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {config.autoDeleteOldData && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Días de retención de datos
              </label>
              <input
                type="number"
                min="7"
                max="365"
                value={config.dataRetentionDays}
                onChange={(e) => handleConfigChange('dataRetentionDays', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-600 mt-1">
                Los datos más antiguos que {config.dataRetentionDays} días serán eliminados automáticamente
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Notificaciones</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Habilitar notificaciones</h4>
              <p className="text-sm text-gray-600">Activar sistema de notificaciones</p>
            </div>
            <button
              type="button"
              onClick={() => handleConfigChange('enableNotifications', !config.enableNotifications)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                config.enableNotifications ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config.enableNotifications ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {config.enableNotifications && (
            <div className="space-y-4 ml-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Notificaciones por email</h4>
                  <p className="text-sm text-gray-600">Enviar notificaciones por correo electrónico</p>
                </div>
                <button
                  type="button"
                  onClick={() => handleConfigChange('emailNotifications', !config.emailNotifications)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                    config.emailNotifications ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      config.emailNotifications ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Notificaciones por SMS</h4>
                  <p className="text-sm text-gray-600">Enviar notificaciones por mensaje de texto</p>
                </div>
                <button
                  type="button"
                  onClick={() => handleConfigChange('smsNotifications', !config.smsNotifications)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                    config.smsNotifications ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      config.smsNotifications ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Security & Access */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Seguridad y Acceso</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Permitir registro de nuevos usuarios</h4>
              <p className="text-sm text-gray-600">Los usuarios pueden registrarse por sí mismos</p>
            </div>
            <button
              type="button"
              onClick={() => handleConfigChange('allowRegistration', !config.allowRegistration)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                config.allowRegistration ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config.allowRegistration ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* System Maintenance */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Mantenimiento del Sistema</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Modo de mantenimiento</h4>
              <p className="text-sm text-gray-600">Bloquea el acceso al sistema para mantenimiento</p>
            </div>
            <button
              type="button"
              onClick={() => handleConfigChange('maintenanceMode', !config.maintenanceMode)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 ${
                config.maintenanceMode ? 'bg-red-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config.maintenanceMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Modo debug</h4>
              <p className="text-sm text-gray-600">Activar información de depuración detallada</p>
            </div>
            <button
              type="button"
              onClick={() => handleConfigChange('debugMode', !config.debugMode)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 ${
                config.debugMode ? 'bg-yellow-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config.debugMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleReset}
          className="px-6 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
        >
          Restablecer por Defecto
        </button>
        
        <div className="space-x-3">
          <button
            onClick={loadConfig}
            className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Recargar
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !hasChanges}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </div>
    </div>
  );
};