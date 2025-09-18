import api from './api';
import { User } from './auth.service';

export interface UserRole {
  id: string;
  name: 'ADMIN' | 'OPERATOR' | 'VIEWER';
  permissions: string[];
}

export interface CreateUserData {
  email: string;
  password: string;
  fullName: string;
  roleIds: string[];
}

export interface UpdateUserData {
  email?: string;
  fullName?: string;
  roleIds?: string[];
  isActive?: boolean;
}

export interface UserWithRoles extends User {
  roles: UserRole[];
}

class UserService {
  // Get all users
  async getUsers(params?: {
    role?: string;
    isActive?: boolean;
    page?: number;
    limit?: number;
  }): Promise<UserWithRoles[]> {
    const response = await api.get('/api/users', { params });
    return response.data;
  }

  // Get specific user
  async getUser(userId: string): Promise<UserWithRoles> {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  }

  // Create new user
  async createUser(userData: CreateUserData): Promise<UserWithRoles> {
    const response = await api.post('/api/users', userData);
    return response.data;
  }

  // Update user
  async updateUser(userId: string, userData: UpdateUserData): Promise<UserWithRoles> {
    const response = await api.put(`/api/users/${userId}`, userData);
    return response.data;
  }

  // Delete user
  async deleteUser(userId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/users/${userId}`);
    return response.data;
  }

  // Activate/Deactivate user
  async toggleUserStatus(userId: string, isActive: boolean): Promise<UserWithRoles> {
    const response = await api.patch(`/api/users/${userId}/status`, { isActive });
    return response.data;
  }

  // Get all roles
  async getRoles(): Promise<UserRole[]> {
    const response = await api.get('/api/users/roles');
    return response.data;
  }

  // Get user permissions
  async getUserPermissions(userId: string): Promise<string[]> {
    const response = await api.get(`/api/users/${userId}/permissions`);
    return response.data;
  }

  // Update user roles
  async updateUserRoles(userId: string, roleIds: string[]): Promise<UserWithRoles> {
    const response = await api.put(`/api/users/${userId}/roles`, { roleIds });
    return response.data;
  }

  // Reset user password (Admin only)
  async resetUserPassword(userId: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post(`/api/users/${userId}/reset-password`, { newPassword });
    return response.data;
  }

  // Search users
  async searchUsers(query: string): Promise<UserWithRoles[]> {
    const response = await api.get('/api/users/search', {
      params: { q: query }
    });
    return response.data;
  }

  // Get user activity log
  async getUserActivity(userId: string, params?: {
    startDate?: string;
    endDate?: string;
    action?: string;
    page?: number;
    limit?: number;
  }): Promise<Array<{
    id: string;
    action: string;
    details: string;
    ipAddress: string;
    userAgent: string;
    createdAt: string;
  }>> {
    const response = await api.get(`/api/users/${userId}/activity`, { params });
    return response.data;
  }

  // Bulk user operations
  async bulkUpdateUsers(userIds: string[], action: 'activate' | 'deactivate' | 'delete' | 'assign-role', data?: any): Promise<{
    processed: number;
    failed: number;
    results: Array<{
      userId: string;
      success: boolean;
      error?: string;
    }>;
  }> {
    const response = await api.post('/api/users/bulk', {
      userIds,
      action,
      data
    });
    return response.data;
  }

  // Export users
  async exportUsers(params?: {
    role?: string;
    isActive?: boolean;
    format?: 'csv' | 'xlsx';
  }): Promise<Blob> {
    const response = await api.get('/api/users/export', {
      params,
      responseType: 'blob'
    });
    return response.data;
  }
}

export const userService = new UserService();
export default userService;