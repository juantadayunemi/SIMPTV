import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  user?: User;
  emailSent?: boolean;
  warning?: string;
  error?: string;
  suggestion?: string;
  code?: string;
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
  firstName?: string;
  lastName?: string;
  phoneNumber?: string;
  profileImage?: string;
  profileImageUrl?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  userRoles?: { role: string }[];
}

class AuthService {
  // Login user
  async login(credentials: LoginCredentials, rememberMe: boolean = false): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login/', credentials);
    const { access_token, refresh_token, user, expires_at } = response.data;
    // Siempre usar localStorage para guardar tokens y usuario
    localStorage.setItem('access_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('user', JSON.stringify(user));
    if (expires_at) {
      localStorage.setItem('token_expires_at', expires_at);
    }
    localStorage.setItem('remember_me', rememberMe.toString());
    return response.data;
  }

  // Register user
  async register(userData: RegisterData): Promise<RegisterResponse> {
    const response = await api.post('/api/auth/register/', userData);
    return response.data;
  }

  // Confirm email with token
  async confirmEmail(token: string): Promise<{ message: string; user: User }> {
    const response = await api.post('/api/auth/confirm-email/', { token });
    return response.data;
  }

  // Resend confirmation email
  async resendConfirmation(email: string): Promise<{ message: string; emailSent: boolean }> {
    const response = await api.post('/api/auth/resend-confirmation/', { email });
    return response.data;
  }

  // Forgot password - request reset link
  async forgotPassword(email: string): Promise<{ message: string; emailSent: boolean }> {
    const response = await api.post('/api/auth/forgot-password/', { email });
    return response.data;
  }

  // Reset password with token
  async resetPassword(token: string, password: string, confirmPassword: string): Promise<{ message: string }> {
    const response = await api.post('/api/auth/reset-password/', {
      token,
      password,
      confirmPassword
    });
    return response.data;
  }

  // Get user profile
  async getProfile(): Promise<User> {
    const response = await api.get('/api/auth/profile/');
    return response.data;
  }

  // Update profile (supports both JSON and FormData)
  async updateProfile(userData: Partial<User> | FormData): Promise<User> {
    const response = await api.put('/api/auth/profile/', userData, {
      headers: userData instanceof FormData 
        ? { 'Content-Type': 'multipart/form-data' }
        : { 'Content-Type': 'application/json' }
    });
    return response.data.user || response.data;
  }

  // Logout
  async logout(): Promise<void> {
    // Limpiar localStorage PRIMERO para evitar que otras peticiones usen el token
    const token = localStorage.getItem('access_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_expires_at');
    localStorage.removeItem('remember_me');
    
    // Luego intentar desactivar dispositivos FCM (sin bloquear si falla)
    if (token) {
      try {
        await api.post('/api/auth/logout/', {}, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log('✓ Logout exitoso - dispositivos FCM desactivados');
      } catch (error) {
        // No fallar el logout si hay error en el backend
        console.warn('⚠️ Error al desactivar dispositivos FCM:', error);
      }
    }
  }

  // Get stored token (solo localStorage)
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Check if token is still valid
  isTokenValid(): boolean {
    const token = this.getToken();
    if (!token) return false;
    const expiresAt = localStorage.getItem('token_expires_at');
    if (!expiresAt) return true; // If no expiration date, assume valid
    const now = new Date();
    const expiration = new Date(expiresAt);
    return now < expiration;
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
    return !!this.getToken() && this.isTokenValid();
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