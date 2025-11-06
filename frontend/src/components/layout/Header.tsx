import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell } from 'lucide-react';

export const Header: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [notificationCount, setNotificationCount] = useState(0);
  const [isBlinking, setIsBlinking] = useState(false);

  useEffect(() => {
    // 🔔 Manejar nuevas notificaciones en tiempo real desde WebSocket
    const handleNewNotification = (event: Event) => {
      const customEvent = event as CustomEvent;
      console.log('🔔 Header: Nueva notificación WebSocket recibida', customEvent.detail);
      
      // Incrementar contador
      setNotificationCount(prev => {
        const newCount = prev + 1;
        console.log(`� Contador de notificaciones: ${prev} → ${newCount}`);
        return newCount;
      });
      
      // Activar parpadeo
      setIsBlinking(true);
      
      // Detener parpadeo después de 5 segundos
      setTimeout(() => {
        setIsBlinking(false);
      }, 5000);
    };

    // Escuchar solo eventos de nuevas notificaciones WebSocket
    window.addEventListener('newNotification', handleNewNotification);

    return () => {
      window.removeEventListener('newNotification', handleNewNotification);
    };
  }, []);

  const handleNotificationClick = () => {
    // 🔄 Resetear contador al hacer click
    console.log('🔔 Usuario hizo click en campana, reseteando contador');
    setNotificationCount(0);
    setIsBlinking(false);
    
    // Navegar a la página de notificaciones
    navigate('/notifications');
  };

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
      case '/history-traffic':
        return {
          title: 'Historial de Tráfico',
          subtitle: 'Análisis del tráfico histórico y patrones de comportamiento'
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
                <span>Última actualización: {new Date().toLocaleTimeString()}</span>
              </div>

              {/* Badge de notificaciones */}
              <button 
                onClick={handleNotificationClick}
                className="relative group"
                aria-label={`${notificationCount} notificaciones sin leer`}
              >
                {notificationCount > 0 ? (
                  <div className="relative">
                    <div className={`h-10 w-10 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-lg border-2 border-white cursor-pointer hover:from-red-600 hover:to-red-700 transition-all hover:scale-110 ${isBlinking ? 'animate-bounce' : ''}`}>
                      <span className="relative z-10">
                        {notificationCount > 99 ? '99+' : notificationCount}
                      </span>
                      {/* Pulse ring effect - más intenso cuando parpadea */}
                      <span className={`absolute inline-flex h-full w-full rounded-full bg-red-400 ${isBlinking ? 'opacity-100 animate-ping' : 'opacity-75 animate-ping'}`}></span>
                    </div>
                    {/* Tooltip */}
                    <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block">
                      <div className="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                        {notificationCount} {notificationCount === 1 ? 'notificación' : 'notificaciones'} sin leer
                        <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center shadow-lg border-2 border-white cursor-pointer transition-all hover:scale-110 relative ${isBlinking ? 'animate-bounce bg-yellow-500' : 'bg-gray-400 hover:bg-gray-500'}`}>
                    <Bell className={`w-5 h-5 text-white ${isBlinking ? 'animate-pulse' : ''}`} />
                    {isBlinking && (
                      <span className="absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75 animate-ping"></span>
                    )}
                    {/* Tooltip */}
                    <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block">
                      <div className="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                        {isBlinking ? 'Nueva notificación' : 'Sin notificaciones'}
                        <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                      </div>
                    </div>
                  </div>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;