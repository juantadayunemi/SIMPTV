import React, { useState } from 'react';
import { UserManagementSection, RoleManagementSection, SystemSettingsSection } from '../../components/settings';

type SettingsTab = 'users' | 'roles' | 'system';

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('users');

  const tabs = [
    {
      id: 'users' as const,
      name: 'Gestión de Usuarios',
      icon: '👥',
      description: 'Administrar usuarios del sistema'
    },
    {
      id: 'roles' as const,
      name: 'Roles y Permisos',
      icon: '🔐',
      description: 'Configurar roles y permisos'
    },
    {
      id: 'system' as const,
      name: 'Configuración Sistema',
      icon: '⚙️',
      description: 'Configuraciones generales'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'users':
        return <UserManagementSection />;
      case 'roles':
        return <RoleManagementSection />;
      case 'system':
        return <SystemSettingsSection />;
      default:
        return <UserManagementSection />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuraciones</h1>
        <p className="text-gray-600">Administra usuarios, roles y configuraciones del sistema</p>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="text-xl mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Description */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            {tabs.find(tab => tab.id === activeTab)?.description}
          </p>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;