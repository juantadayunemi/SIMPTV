import axios from 'axios';

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Check both localStorage and sessionStorage for token
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('📤 Request with auth:', config.method?.toUpperCase(), config.url);
    } else {
      console.log('📤 Request without auth:', config.method?.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // ⚠️ NO intentar refresh si es un error de login explícito
    // Los endpoints de login/register deben fallar normalmente
    const isAuthEndpoint = original.url?.includes('/api/auth/login') || 
                          original.url?.includes('/api/auth/register');

    // Handle 401 errors (unauthorized) - SOLO si NO es un endpoint de autenticación
    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      original._retry = true;
      
      // Check both localStorage and sessionStorage for refresh token
      const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
      const storage = localStorage.getItem('access_token') ? localStorage : sessionStorage;
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${api.defaults.baseURL}/api/auth/token/refresh/`, {
            refresh: refreshToken  // Django SimpleJWT espera "refresh" como campo
          });
          
          const { access } = response.data;  // Django SimpleJWT retorna "access" (no "access_token")
          storage.setItem('access_token', access);
          
          // Retry original request with new token
          original.headers.Authorization = `Bearer ${access}`;
          return api(original);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          sessionStorage.removeItem('access_token');
          sessionStorage.removeItem('refresh_token');
          sessionStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        sessionStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;