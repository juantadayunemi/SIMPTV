import React, { useState, useEffect } from 'react';
import { userService } from '../../services/users.service';
import { USER_ROLES, PERMISSIONS, ROLE_PERMISSIONS, UserRoleType } from '../../../../shared/src/types/roleTypes';

interface RoleInfo {
  id: string;
  name: UserRoleType;
  permissions: readonly string[];
  userCount?: number;
}

interface PermissionGroup {
  name: string;
  permissions: Array<{
    key: string;
    label: string;
    description: string;
  }>;
}

const permissionGroups: PermissionGroup[] = [
  {
    name: 'Análisis de Tráfico',
    permissions: [
      { key: PERMISSIONS.TRAFFIC_CREATE, label: 'Crear análisis', description: 'Iniciar nuevos análisis de tráfico' },
      { key: PERMISSIONS.TRAFFIC_READ, label: 'Ver análisis', description: 'Visualizar análisis existentes' },
      { key: PERMISSIONS.TRAFFIC_UPDATE, label: 'Editar análisis', description: 'Modificar análisis existentes' },
      { key: PERMISSIONS.TRAFFIC_DELETE, label: 'Eliminar análisis', description: 'Borrar análisis del sistema' },
    ]
  },
  {
    name: 'Detección de Placas',
    permissions: [
      { key: PERMISSIONS.PLATE_CREATE, label: 'Crear detección', description: 'Iniciar nuevas detecciones' },
      { key: PERMISSIONS.PLATE_READ, label: 'Ver detecciones', description: 'Visualizar detecciones de placas' },
      { key: PERMISSIONS.PLATE_UPDATE, label: 'Editar detecciones', description: 'Modificar datos de detección' },
      { key: PERMISSIONS.PLATE_DELETE, label: 'Eliminar detecciones', description: 'Borrar registros de detección' },
    ]
  },
  {
    name: 'Gestión de Usuarios',
    permissions: [
      { key: PERMISSIONS.USER_CREATE, label: 'Crear usuarios', description: 'Agregar nuevos usuarios al sistema' },
      { key: PERMISSIONS.USER_READ, label: 'Ver usuarios', description: 'Visualizar información de usuarios' },
      { key: PERMISSIONS.USER_UPDATE, label: 'Editar usuarios', description: 'Modificar datos de usuarios' },
      { key: PERMISSIONS.USER_DELETE, label: 'Eliminar usuarios', description: 'Remover usuarios del sistema' },
    ]
  },
  {
    name: 'Sistema',
    permissions: [
      { key: PERMISSIONS.SYSTEM_ADMIN, label: 'Administración del sistema', description: 'Acceso completo al sistema' },
      { key: PERMISSIONS.SETTINGS_MANAGE, label: 'Gestionar configuraciones', description: 'Modificar configuraciones del sistema' },
      { key: PERMISSIONS.NOTIFICATIONS_MANAGE, label: 'Gestionar notificaciones', description: 'Administrar sistema de notificaciones' },
    ]
  }
];

const roleDescriptions = {
  [USER_ROLES.ADMIN]: 'Acceso completo al sistema con todos los permisos',
  [USER_ROLES.OPERATOR]: 'Puede realizar operaciones de análisis y gestión limitada',
  [USER_ROLES.VIEWER]: 'Solo puede visualizar información sin realizar modificaciones'
};

const roleColors = {
  [USER_ROLES.ADMIN]: 'bg-red-100 text-red-800 border-red-200',
  [USER_ROLES.OPERATOR]: 'bg-blue-100 text-blue-800 border-blue-200',
  [USER_ROLES.VIEWER]: 'bg-green-100 text-green-800 border-green-200'
};

export const RoleManagementSection: React.FC = () => {
  const [roles, setRoles] = useState<RoleInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState<UserRoleType | null>(null);
  const [customPermissions, setCustomPermissions] = useState<string[]>([]);

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      setLoading(true);
      const rolesData = await userService.getRoles();
      
      // Get user count for each role (this would need to be implemented in the service)
      const rolesWithCount = await Promise.all(
        rolesData.map(async (role) => {
          try {
            const users = await userService.getUsers({ role: role.name });
            return { ...role, userCount: users.length };
          } catch {
            return { ...role, userCount: 0 };
          }
        })
      );
      
      setRoles(rolesWithCount);
    } catch (error) {
      console.error('Error loading roles:', error);
      // Fallback to predefined roles if service fails
      const fallbackRoles = Object.values(USER_ROLES).map(role => ({
        id: role,
        name: role,
        permissions: ROLE_PERMISSIONS[role],
        userCount: 0
      }));
      setRoles(fallbackRoles);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSelect = (role: UserRoleType) => {
    setSelectedRole(role);
    const rolePermissions = ROLE_PERMISSIONS[role] || [];
    setCustomPermissions([...rolePermissions]);
  };

  const handlePermissionToggle = (permission: string) => {
    setCustomPermissions(prev => 
      prev.includes(permission)
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    );
  };

  const handleSavePermissions = async () => {
    // This would save custom permissions for a role
    // Implementation depends on backend support for custom role permissions
    console.log('Saving permissions for role:', selectedRole, customPermissions);
    alert('Funcionalidad de permisos personalizados pendiente de implementación en el backend');
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
      {/* Roles Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {roles.map((role) => (
          <div
            key={role.id}
            className={`border rounded-lg p-6 cursor-pointer transition-all hover:shadow-md ${
              selectedRole === role.name ? 'ring-2 ring-blue-500' : ''
            } ${roleColors[role.name]}`}
            onClick={() => handleRoleSelect(role.name)}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">{role.name}</h3>
              <span className="bg-white px-2 py-1 rounded-full text-sm font-medium">
                {role.userCount} usuarios
              </span>
            </div>
            
            <p className="text-sm mb-4 opacity-90">
              {roleDescriptions[role.name]}
            </p>
            
            <div className="space-y-2">
              <div className="text-sm font-medium">Permisos ({role.permissions.length}):</div>
              <div className="flex flex-wrap gap-1">
                {role.permissions.slice(0, 3).map((permission) => (
                  <span
                    key={permission}
                    className="bg-white bg-opacity-60 px-2 py-1 rounded text-xs"
                  >
                    {permission.split(':')[1] || permission}
                  </span>
                ))}
                {role.permissions.length > 3 && (
                  <span className="bg-white bg-opacity-60 px-2 py-1 rounded text-xs">
                    +{role.permissions.length - 3} más
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Permission Details */}
      {selectedRole && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Permisos del Rol: {selectedRole}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {roleDescriptions[selectedRole]}
            </p>
          </div>
          
          <div className="p-6">
            <div className="space-y-6">
              {permissionGroups.map((group) => (
                <div key={group.name} className="border rounded-lg p-4">
                  <h4 className="text-md font-semibold text-gray-900 mb-3">
                    {group.name}
                  </h4>
                  
                  <div className="space-y-3">
                    {group.permissions.map((permission) => {
                      const isGranted = customPermissions.includes(permission.key);
                      const rolePermissions = ROLE_PERMISSIONS[selectedRole] || [];
                      const isDefault = rolePermissions.includes(permission.key as any);
                      
                      return (
                        <div
                          key={permission.key}
                          className="flex items-start space-x-3 p-3 bg-gray-50 rounded"
                        >
                          <input
                            type="checkbox"
                            id={permission.key}
                            checked={isGranted}
                            onChange={() => handlePermissionToggle(permission.key)}
                            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <div className="flex-1">
                            <label
                              htmlFor={permission.key}
                              className="text-sm font-medium text-gray-900 cursor-pointer"
                            >
                              {permission.label}
                              {isDefault && (
                                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  Por defecto
                                </span>
                              )}
                            </label>
                            <p className="text-sm text-gray-600 mt-1">
                              {permission.description}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setSelectedRole(null);
                  setCustomPermissions([]);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Cancelar
              </button>
              <button
                onClick={handleSavePermissions}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Guardar Cambios
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Role Statistics */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Estadísticas de Roles
          </h3>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {roles.map((role) => (
              <div key={role.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${
                    role.name === USER_ROLES.ADMIN ? 'bg-red-500' :
                    role.name === USER_ROLES.OPERATOR ? 'bg-blue-500' : 'bg-green-500'
                  }`}></div>
                  <span className="font-medium">{role.name}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    {role.userCount} usuarios
                  </span>
                  <span className="text-sm text-gray-600">
                    {role.permissions.length} permisos
                  </span>
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        role.name === USER_ROLES.ADMIN ? 'bg-red-500' :
                        role.name === USER_ROLES.OPERATOR ? 'bg-blue-500' : 'bg-green-500'
                      }`}
                      style={{ 
                        width: `${Math.max(10, (role.userCount || 0) * 10)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};