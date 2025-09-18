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
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${api.defaults.baseURL}/api/auth/token/refresh/`, {
            refresh: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          original.headers.Authorization = `Bearer ${access_token}`;
          return api(original);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;