import React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';
import { USER_ROLES, type UserRoleType } from '@traffic-analysis/shared';

const navigationItems = [
  {
    name: 'Inicio',
    href: '/dashboard',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR, USER_ROLES.VIEWER] as UserRoleType[]
  },
  {
    name: 'Cámaras',
    href: '/traffic',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR, USER_ROLES.VIEWER] as UserRoleType[]
  },
  {
    name: 'Predicción',
    href: '/predictions',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR, USER_ROLES.VIEWER] as UserRoleType[]
  },
  {
    name: 'Dashboard',
    href: '/plates',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR, USER_ROLES.VIEWER] as UserRoleType[]
  },
  {
    name: 'Historial',
    href: '/notifications',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR] as UserRoleType[]
  },
  {
    name: 'Vehículos con denuncias',
    href: '/vehicles-reports',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR] as UserRoleType[]
  },
  {
    name: 'Configuración',
    href: '/settings',
    icon: (
      <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
        <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
      </svg>
    ),
    roles: [USER_ROLES.ADMIN] as UserRoleType[]
  }
];

export const Sidebar: React.FC = () => {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      logout();
      // Force navigation to login immediately
      navigate('/login', { replace: true });
      // Also reload the page to ensure clean state
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      // Fallback: force navigation to login
      window.location.href = '/login';
    }
  };

  return (
    <div className="bg-primary-700 text-white min-h-screen flex flex-col w-64 shadow-xl">
      {/* Logo Section */}
      <div className="p-8 flex flex-col items-center">
        {/* Traffic Light Icon */}
        <div className="w-32 h-32 -mb-2">
           <img
              src={logoTraficSmart}
              alt="TrafiSmart Logo"
              className="mx-auto h-32 w-auto mb-2"
            />
        </div>
        
        {/* App Name */}
        <h1 className="text-xl -mb-2   -mt-0 font-bold text-white">
          {APP_NAME}
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.href;

          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={`
                group flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 relative
                ${isActive
                  ? 'bg-primary-800 text-white'
                  : 'text-white/80 hover:bg-primary-800/50 hover:text-white'
                }
              `}
            >
              {/* Barra indicadora izquierda redondeada */}
              {isActive && (
                <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-1 h-10 bg-white rounded-r-full"></div>
              )}
              
              <span className="mr-3 text-current">
                {item.icon}
              </span>
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Section - Admin & Logout */}
      <div className="border-t border-slice border-white/10 bg-primary-700/50">
        {/* Admin Section */}
        <div className="px-4 py-3 flex items-center text-white/80">
          <svg className="w-7 h-7 mr-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
          <span className="text-sm font-medium">Admin</span>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full px-4 py-3 flex items-center text-white/80 hover:bg-primary-600/50 hover:text-white transition-colors"
        >
          <svg className="w-7 h-7 mr-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
          </svg>
          <span className="text-sm font-medium">Cerrar Sesión</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;