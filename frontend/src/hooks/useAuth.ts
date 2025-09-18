import { useState, useEffect } from 'react';
import { authService, User } from '../services/auth.service';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const token = authService.getToken();
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }));
        return;
      }

      const user = await authService.getCurrentUser();
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      console.error('Auth check failed:', error);
      authService.logout();
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const response = await authService.login({ email, password });
      
      setState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const response = await authService.register({ email, password, fullName });
      
      setState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  };

  const updateProfile = async (data: { fullName?: string; email?: string }) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const updatedUser = await authService.updateProfile(data);
      
      setState(prev => ({
        ...prev,
        user: updatedUser,
        isLoading: false,
        error: null,
      }));

      return updatedUser;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Profile update failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      await authService.changePassword(currentPassword, newPassword);
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: null,
      }));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Password change failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  return {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError,
    checkAuth,
  };
};