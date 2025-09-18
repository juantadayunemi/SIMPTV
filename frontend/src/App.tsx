import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import TrafficAnalysisPage from './pages/traffic/TrafficAnalysisPage';
import PlateDetectionPage from './pages/plates/PlateDetectionPage';
import UsersPage from './pages/users/UsersPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import ProfilePage from './pages/profile/ProfilePage';

// Components
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/ui/LoadingSpinner';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Styles
import './App.css';

const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
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
            <Route path="traffic" element={<TrafficAnalysisPage />} />
            <Route path="plates" element={<PlateDetectionPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="profile" element={<ProfilePage />} />
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
  );
};

export default App;