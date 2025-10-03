import React from 'react';
import { useLocation } from 'react-router-dom';

export const Header: React.FC = () => {
  const location = useLocation();

  // Simulamos el número de notificaciones (esto vendrá de tu estado/API)
  const notificationCount = 1; // Cambia este valor para probar: 0, 1, 5, 99, 100, etc.

  // Get page title based on current route
  const getPageTitle = () => {
    const path = location.pathname;
    switch (path) {
      case '/dashboard':
        return {
          title: 'Inicio',
          subtitle: 'Resumen general del sistema de análisis de tráfico'
        };
      case '/traffic':
        return {
          title: 'Monitoreo de Tráfico',
          subtitle: 'Análisis y monitoreo en tiempo real del tráfico vehicular'
        };
      case '/plates':
        return {
          title: 'Detección de Placas',
          subtitle: 'Sistema de reconocimiento de placas vehiculares'
        };
      case '/predictions':
        return {
          title: 'Análisis de Predicciones',
          subtitle: 'Predicciones de tráfico basadas en Machine Learning'
        };
      case '/vehicles-reports':
        return {
          title: 'Vehículos con Denuncias',
          subtitle: 'Listado de vehículos reportados y bajo investigación'
        };
      case '/users':
        return {
          title: 'Gestión de Usuarios',
          subtitle: 'Administración de usuarios del sistema'
        };
      case '/settings':
        return {
          title: 'Configuraciones',
          subtitle: 'Configuración del sistema, usuarios y roles'
        };
      case '/notifications':
        return {
          title: 'Notificaciones',
          subtitle: 'Centro de notificaciones y alertas del sistema'
        };
      case '/profile':
        return {
          title: 'Mi Perfil',
          subtitle: 'Información personal y configuración de cuenta'
        };
      default:
        return {
          title: 'Sistema de Análisis de Tráfico',
          subtitle: 'Panel de control y monitoreo inteligente'
        };
    }
  };

  const pageInfo = getPageTitle();

  return (
    <header className="bg-primary-50 shadow-sm border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Dynamic Title Based on Route */}
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {pageInfo.title}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {pageInfo.subtitle}
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-4">
            {/* Badge y Última actualización */}
            <div className="flex items-center space-x-3">

             {/* Última actualización */}
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Última actualización: 9:53:19 p.m.</span>
              </div>

              {/* Badge de notificaciones */}
              {notificationCount > 0 ? (
                <button className="h-6 w-6 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-lg animate-pulse border-2 border-white relative cursor-pointer hover:from-red-600 hover:to-red-700 transition-colors">
                  <span className="relative z-10">
                    {notificationCount > 99 ? '99+' : notificationCount}
                  </span>
                  {/* Pulse ring effect */}
                  <span className="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75 animate-ping"></span>
                </button>
              ) : (
                <div className="h-6 w-6 bg-green-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              )}
              
        
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;