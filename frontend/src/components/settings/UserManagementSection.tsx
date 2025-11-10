import React, { useState, useEffect } from 'react';
import { UserWithRoles, userService } from '../../services/users.service';
import { UserRoleType } from '../../../../shared/src/types/roleTypes';

interface UserTableProps {
  users: UserWithRoles[];
  onToggleStatus: (userId: string, isActive: boolean) => void;
  onEditRoles: (user: UserWithRoles) => void;
  onDeleteUser: (userId: string) => void;
}

const UserTable: React.FC<UserTableProps> = ({
  users,
  onToggleStatus,
  onEditRoles,
  onDeleteUser,
}) => {


  
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Usuario
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Roles
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Último acceso
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10">
                    <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                      {user.email.charAt(0).toUpperCase()}
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">
                      {user.email}
                    </div>
                    <div className="text-sm text-gray-500">
                      ID: {user.id.substring(0, 8)}...
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-wrap gap-1">
                  {user.roles.map((role) => (
                    <span
                      key={role.id}
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        role.name === 'ADMIN'
                          ? 'bg-red-100 text-red-800'
                          : role.name === 'OPERATOR'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {role.name}
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user.isActive
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {user.isActive ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {user.updatedAt ? new Date(user.updatedAt).toLocaleDateString() : 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button
                  onClick={() => onEditRoles(user)}
                  className="text-indigo-600 hover:text-indigo-900"
                >
                  Editar Roles
                </button>
                <button
                  onClick={() => onToggleStatus(user.id, !user.isActive)}
                  className={`${
                    user.isActive
                      ? 'text-red-600 hover:text-red-900'
                      : 'text-green-600 hover:text-green-900'
                  }`}
                >
                  {user.isActive ? 'Inhabilitar' : 'Habilitar'}
                </button>
                <button
                  onClick={() => onDeleteUser(user.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};


interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (userData: { email: string; password: string; roleIds: string[] }) => void;
  availableRoles: Array<{ id: string; name: UserRoleType; permissions: string[] }>;
}

const CreateUserModal: React.FC<CreateUserModalProps> = ({
  isOpen,
  onClose,
  onSave,
  availableRoles,
}) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    roleIds: [] as string[]
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }

    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }

    if (formData.roleIds.length === 0) {
      newErrors.roles = 'Debe seleccionar al menos un rol';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSave({
        email: formData.email,
        password: formData.password,
        roleIds: formData.roleIds
      });
      setFormData({ email: '', password: '', confirmPassword: '', roleIds: [] });
      setErrors({});
    }
  };

  const handleRoleToggle = (roleId: string) => {
    setFormData(prev => ({
      ...prev,
      roleIds: prev.roleIds.includes(roleId)
        ? prev.roleIds.filter(id => id !== roleId)
        : [...prev.roleIds, roleId]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Crear Nuevo Usuario
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="usuario@email.com"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Contraseña
              </label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                  errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Roles
              </label>
              <div className="space-y-2">
                {availableRoles.map((role) => (
                  <label key={role.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.roleIds.includes(role.id)}
                      onChange={() => handleRoleToggle(role.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-3 text-sm font-medium text-gray-700">
                      {role.name}
                    </span>
                  </label>
                ))}
              </div>
              {errors.roles && <p className="text-red-500 text-xs mt-1">{errors.roles}</p>}
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Crear Usuario
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

interface RoleModalProps {
  user: UserWithRoles | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (userId: string, roleIds: string[]) => void;
  availableRoles: Array<{ id: string; name: UserRoleType; permissions: string[] }>;
}

const RoleModal: React.FC<RoleModalProps> = ({
  user,
  isOpen,
  onClose,
  onSave,
  availableRoles,
}) => {
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);

  useEffect(() => {
    if (user) {
      setSelectedRoles(user.roles.map((role: any) => role.id));
    }
  }, [user]);

  const handleSave = () => {
    if (user) {
      onSave(user.id, selectedRoles);
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Editar Roles de {user.email}
          </h3>
          
          <div className="space-y-3">
            {availableRoles.map((role: any) => (
              <label key={role.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedRoles.includes(role.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedRoles([...selectedRoles, role.id]);
                    } else {
                      setSelectedRoles(selectedRoles.filter(id => id !== role.id));
                    }
                  }}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-3 text-sm font-medium text-gray-700">
                  {role.name}
                </span>
              </label>
            ))}
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Guardar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const UserManagementSection: React.FC = () => {

//   export interface UserRole {
//   id: string;
//   name: 'ADMIN' | 'OPERATOR' | 'VIEWER';
//   permissions: string[];
// }
  const [users, setUsers] = useState<UserWithRoles[]>([

]);

  const [loading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [selectedUser, setSelectedUser] = useState<UserWithRoles | null>(null);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [availableRoles] = useState<Array<{ id: string; name: UserRoleType; permissions: string[] }>>([
    { id: 'r1', name: 'ADMIN', permissions: [] },
    { id: 'r2', name: 'OPERATOR', permissions: [] },
    { id: 'r3', name: 'VIEWER', permissions: [] },
  ]);

  const handleToggleStatus = (userId: string, isActive: boolean) => {
    setUsers(prev =>
      prev.map(u => (u.id === userId ? { ...u, isActive } : u))
    );
  };

  const handleEditRoles = (user: UserWithRoles) => {
    setSelectedUser(user);
    setIsRoleModalOpen(true);
  };

  const handleSaveRoles = (userId: string, roleIds: string[]) => {
    const updatedRoles = availableRoles.filter(r => roleIds.includes(r.id));
    setUsers(prev =>
      prev.map(u => (u.id === userId ? { ...u, roles: updatedRoles } : u))
    );
    setIsRoleModalOpen(false);
    setSelectedUser(null);
  };

  const handleCreateUser = (userData: { email: string; password: string; roleIds: string[] }) => {
    const newUser: UserWithRoles = {
      id: Math.random().toString(36).substring(2, 10),
      email: userData.email,
      isActive: true,
      updatedAt: new Date().toISOString(),
      roles: availableRoles.filter(r => userData.roleIds.includes(r.id)),
    };
    setUsers(prev => [...prev, newUser]);
    setIsCreateModalOpen(false);
  };

  const handleDeleteUser = (userId: string) => {
    setUsers(prev => prev.filter(u => u.id !== userId));
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = !filterRole || user.roles.some((role: any) => role.name === filterRole);
    const matchesStatus = !filterStatus || 
                         (filterStatus === 'active' && user.isActive) ||
                         (filterStatus === 'inactive' && !user.isActive);
    return matchesSearch && matchesRole && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900">Gestión de Usuarios</h2>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 flex items-center">
          <div className="text-blue-600 text-2xl mr-3">👥</div>
          <div>
            <div className="text-lg font-semibold text-blue-900">{users.length}</div>
            <div className="text-sm text-blue-600">Total Usuarios</div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4 flex items-center">
          <div className="text-green-600 text-2xl mr-3">✅</div>
          <div>
            <div className="text-lg font-semibold text-green-900">{users.filter(u => u.isActive).length}</div>
            <div className="text-sm text-green-600">Usuarios Activos</div>
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-4 flex items-center">
          <div className="text-red-600 text-2xl mr-3">❌</div>
          <div>
            <div className="text-lg font-semibold text-red-900">{users.filter(u => !u.isActive).length}</div>
            <div className="text-sm text-red-600">Usuarios Inactivos</div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 flex items-center">
          <div className="text-purple-600 text-2xl mr-3">🔐</div>
          <div>
            <div className="text-lg font-semibold text-purple-900">
              {users.filter(u => u.roles.some(r => r.name === 'ADMIN')).length}
            </div>
            <div className="text-sm text-purple-600">Administradores</div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Lista de Usuarios ({filteredUsers.length})
          </h3>
        </div>
        <UserTable
          users={filteredUsers}
          onToggleStatus={handleToggleStatus}
          onEditRoles={handleEditRoles}
          onDeleteUser={handleDeleteUser}
        />
      </div>

      {/* Modals */}
      <CreateUserModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSave={handleCreateUser}
        availableRoles={availableRoles}
      />
      <RoleModal
        user={selectedUser}
        isOpen={isRoleModalOpen}
        onClose={() => {
          setIsRoleModalOpen(false);
          setSelectedUser(null);
        }}
        onSave={handleSaveRoles}
        availableRoles={availableRoles}
      />
    </div>
  );
};
