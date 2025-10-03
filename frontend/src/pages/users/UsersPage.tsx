import React from 'react';
import { UserManagementSection } from '../../components/settings';

export const UsersPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
        <p className="text-gray-600">Administra usuarios del sistema, roles y permisos</p>
      </div>
      
      <UserManagementSection />
    </div>
  );
};

export default UsersPage;