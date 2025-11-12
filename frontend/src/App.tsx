import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast'; // Usamos Toaster para las notificaciones
import { useAuth } from './hooks/useAuth';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ConfirmEmailPage from './pages/auth/ConfirmEmailPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import TrafficAnalysisPage from './pages/traffic/TrafficAnalysisPage';
import RealTimeAnalysisPage from './pages/traffic/RealTimeAnalysisPage';
import CamerasPage from './pages/traffic/CamerasPage';
import PlateDetectionPage from './pages/plates/PlateDetectionPage';
import PredictionsPage from './pages/predictions/PredictionsPage';
import VehicleReportsPage from './pages/vehicles/VehicleReportsPage';
import UsersPage from './pages/users/UsersPage';
import SettingsPage from './pages/settings/SettingsPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import HistoryTrafficPage from './pages/historyTraffic/historyPage'; // Agregado de V1
import ProfilePage from './pages/profile/ProfilePage';
import { CameraLiveAnalysisPage } from './pages/traffic/CameraLiveAnalysisPage'; // Ruta dinámica de V2
import { LiveMonitoring } from './pages/monitoring/LiveMonitoring'; // Live Monitoring Page

// Components
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/ui/LoadingSpinner';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { FCMInitializer } from './components/notifications/FCMInitializer'; // Inicializador de FCM de V2

// Styles
import './App.css';
import { ToastProvider } from './components/ui/ToastContainer';

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Lógica de redirección basada en la autenticación (limpia, sin console.log de tokens)
  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const currentPath = window.location.pathname;
      const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/confirm-email'];
      const isPublicRoute = publicRoutes.some(route => currentPath.startsWith(route));

      if (!isPublicRoute) {
        console.log('⚠️ Usuario no autenticado, redirigiendo a login desde:', currentPath);
        window.location.href = '/login';
      }
    }
  }, [isAuthenticated, isLoading]);

  // Pantalla de carga global (usando el estilo de V2 con LoadingSpinner)
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <ToastProvider>
    <Router>
      <div className="App min-h-screen bg-gray-50">
        {/* FCM Initializer - Solo se activa cuando el usuario está autenticado */}
        <FCMInitializer />

        {/* React Hot Toast Container */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 8000,
            style: {
              background: 'transparent',
              boxShadow: 'none',
              padding: 0,
            },
            success: { duration: 4000, },
            error: { duration: 5000, },
          }}
        />

        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginPage />
              )
            } 
          />
          <Route 
            path="/register" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <RegisterPage />
              )
            } 
          />
          <Route 
            path="/forgot-password" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <ForgotPasswordPage />
              )
            } 
          />
          <Route 
            path="/reset-password" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <ResetPasswordPage />
              )
            } 
          />
          <Route 
            path="/confirm-email" 
            element={<ConfirmEmailPage />} 
          />

          {/* Protected Routes */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="traffic" element={<CamerasPage />} />
            <Route path="traffic/analysis" element={<TrafficAnalysisPage />} />
            <Route path="traffic/realtime" element={<RealTimeAnalysisPage />} />
            
            {/* Rutas de Tráfico Específicas */}
            <Route path="camera/:id" element={<CameraLiveAnalysisPage />} /> {/* Live Analysis */}
            <Route path="history-traffic" element={<HistoryTrafficPage />} /> {/* Historial de V1 */}

            <Route path="plates" element={<PlateDetectionPage />} />
            <Route path="predictions" element={<PredictionsPage />} />
            <Route path="vehicles-reports" element={<VehicleReportsPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="profile" element={<ProfilePage />} />
            
            {/* Live Monitoring Routes */}
            <Route path="monitoring/live" element={<LiveMonitoring />} />
          </Route>

          {/* Fallback Route */}
          <Route 
            path="*" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
    </ToastProvider>
  );
};

export default App;
