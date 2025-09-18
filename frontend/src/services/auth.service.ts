import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  fullName: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  userRoles?: { role: string }[];
}

class AuthService {
  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login/', credentials);
    const { access_token, refresh_token, user } = response.data;
    
    // Store tokens and user
    localStorage.setItem('access_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  }

  // Register user
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await api.post('/api/auth/register/', userData);
    const { access_token, refresh_token, user } = response.data;
    
    // Store tokens and user
    localStorage.setItem('access_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  }

  // Get user profile
  async getProfile(): Promise<User> {
    const response = await api.get('/api/auth/profile/');
    return response.data;
  }

  // Update profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.put('/api/auth/profile/', userData);
    return response.data;
  }

  // Logout
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Get current user from storage or API
  async getCurrentUser(): Promise<User> {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        // Fall back to API call if stored user is corrupted
      }
    }
    
    const user = await this.getProfile();
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  }

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/api/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  // Get current user roles
  getUserRoles(): string[] {
    const userStr = localStorage.getItem('user');
    if (!userStr) return [];
    
    try {
      const user = JSON.parse(userStr);
      return user.userRoles?.map((ur: any) => ur.role) || [];
    } catch {
      return [];
    }
  }

  // Check if user has specific role
  hasRole(role: string): boolean {
    return this.getUserRoles().includes(role);
  }

  // Check if user has any of the specified roles
  hasAnyRole(roles: string[]): boolean {
    const userRoles = this.getUserRoles();
    return roles.some(role => userRoles.includes(role));
  }
}

export const authService = new AuthService();
export default authService;