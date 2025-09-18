import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const navigationItems = [
  {
    name: 'Panel de Control',
    href: '/dashboard',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
      </svg>
    ),
    roles: ['ADMIN', 'OPERATOR', 'VIEWER']
  },
  {
    name: 'Análisis de Tráfico',
    href: '/traffic',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    roles: ['ADMIN', 'OPERATOR', 'VIEWER']
  },
  {
    name: 'Detección de Placas',
    href: '/plates',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    roles: ['ADMIN', 'OPERATOR', 'VIEWER']
  },
  {
    name: 'Gestión de Usuarios',
    href: '/users',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
      </svg>
    ),
    roles: ['ADMIN']
  },
  {
    name: 'Notificaciones',
    href: '/notifications',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    roles: ['ADMIN', 'OPERATOR']
  }
];

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const userRoles = user?.userRoles?.map(ur => ur.role) || [];

  const hasAccess = (requiredRoles: string[]) => {
    return requiredRoles.some(role => userRoles.includes(role));
  };

  return (
    <div className={`bg-gradient-to-b from-gray-900 to-gray-800 text-white min-h-screen flex flex-col transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'} shadow-xl`}>
      {/* Logo */}
      <div className="p-6 border-b border-gray-700/50">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent">
                Urbia Analytics
              </h1>
              <p className="text-sm text-gray-400 mt-1">Sistema de Tráfico</p>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
          >
            <svg 
              className={`w-4 h-4 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-6 space-y-1">
        {navigationItems.map((item) => {
          if (!hasAccess(item.roles)) {
            return null;
          }

          const isActive = location.pathname === item.href;

          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={`
                group flex items-center px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200
                ${isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                  : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                }
              `}
              title={isCollapsed ? item.name : undefined}
            >
              <span className={`${isCollapsed ? '' : 'mr-3'} text-current`}>
                {item.icon}
              </span>
              {!isCollapsed && (
                <span className="truncate">{item.name}</span>
              )}
              {isActive && !isCollapsed && (
                <div className="ml-auto w-2 h-2 bg-white rounded-full"></div>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User Info */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-700/50 bg-gray-800/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold ring-2 ring-blue-400/20">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.email}
              </p>
              <p className="text-xs text-blue-300 capitalize">
                {userRoles[0]?.toLowerCase() || 'viewer'}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Collapsed User Avatar */}
      {isCollapsed && (
        <div className="p-3 border-t border-gray-700/50">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold ring-2 ring-blue-400/20 mx-auto">
            {user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;