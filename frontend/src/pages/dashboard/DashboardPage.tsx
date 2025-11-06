import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { dashboardService, DashboardStats } from '../../services/dashboard.service';
import TrafficStatusBadge from '../../components/traffic/TrafficStatusBadge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div 
          className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 cursor-pointer hover:shadow-md transition-shadow" 
          onClick={() => navigate('/traffic')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cámaras Activas</p>
              <p className="text-3xl font-bold text-gray-900">{stats.activeCameras}</p>
            </div>
            <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
              <Camera className="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <CheckCircle className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-sm text-success-600">Click para ver cámaras</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Velocidad Promedio</p>
              <p className="text-3xl font-bold text-gray-900">
                {stats.avgSpeed} <span className="text-lg">km/h</span>
              </p>
            </div>
            <div className="w-12 h-12 bg-success-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-600">En toda la red</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/notifications')}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Alertas Críticas</p>
              <p className="text-3xl font-bold text-gray-900">{stats.criticalAlerts}</p>
            </div>
            <div className="w-12 h-12 bg-error-50 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-error-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-error-600">Denuncias activas - Click para ver</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Eficiencia Red</p>
              <p className="text-3xl font-bold text-gray-900">{stats.networkEfficiency}%</p>
            </div>
            <div className="w-12 h-12 bg-warning-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-warning-600">Buena performance</span>
          </div>
        </div>
      </div>

      {/* Current Traffic Status - Lista Mejorada */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Estado Actual del Tráfico</h2>
          <p className="text-sm text-gray-600">Últimos análisis de cada cámara activa</p>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {stats.currentTrafficData.slice(0, 6).map((data) => (
              <div 
                key={data.cameraId} 
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all"
              >
                {/* Información de la cámara */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900 text-base">{data.cameraName}</h3>
                    <TrafficStatusBadge level={data.congestionLevel} size="sm" />
                  </div>
                  <p className="text-sm text-gray-600">{data.location}</p>
                </div>

                {/* Métricas en columnas */}
                <div className="flex items-center gap-8 mr-4">
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Velocidad</p>
                    <p className="text-lg font-bold text-gray-900">{data.averageSpeed} <span className="text-sm font-normal">km/h</span></p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Vehículos</p>
                    <p className="text-lg font-bold text-gray-900">{data.vehicleCount}</p>
                  </div>
                  <div className="text-center min-w-[100px]">
                    <p className="text-xs text-gray-500 mb-1">Congestión</p>
                    <p className="text-lg font-bold text-gray-900">{data.congestionIndex}%</p>
                  </div>
                </div>

                {/* Barra de progreso vertical */}
                <div className="w-32">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${
                        data.congestionLevel === 'low' ? 'bg-success-500' :
                        data.congestionLevel === 'moderate' ? 'bg-warning-500' :
                        data.congestionLevel === 'high' ? 'bg-orange-500' : 'bg-error-500'
                      }`}
                      style={{ width: `${data.congestionIndex}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Mensaje si no hay datos */}
          {stats.currentTrafficData.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No hay datos de tráfico disponibles en este momento</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Monitoreo en Tiempo Real - Azul con gradiente */}
        <div className="bg-gradient-to-r from-blue-400 to-blue-600 rounded-lg p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
          <h3 className="text-lg font-semibold mb-2">Monitoreo en Tiempo Real</h3>
          <p className="text-blue-50 mb-4 text-sm">Visualiza el estado actual de todas las cámaras</p>
          <button 
            onClick={() => window.location.href = '/traffic/realtime'}
            className="bg-white text-blue-600 px-6 py-2.5 rounded-lg font-medium hover:bg-blue-50 transition-colors shadow-md"
          >
            Ver Tiempo Real
          </button>
        </div>

        {/* Análisis Histórico - Verde con gradiente */}
        <div className="bg-gradient-to-r from-green-400 to-green-600 rounded-lg p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
          <h3 className="text-lg font-semibold mb-2">Análisis Histórico</h3>
          <p className="text-green-50 mb-4 text-sm">Revisa patrones y tendencias de tráfico</p>
          <button 
            onClick={() => window.location.href = '/history-traffic'}
            className="bg-white text-green-600 px-6 py-2.5 rounded-lg font-medium hover:bg-green-50 transition-colors shadow-md"
          >
            Ver Historial
          </button>
        </div>

        {/* Pronósticos - Naranja con gradiente */}
        <div className="bg-gradient-to-r from-warning-500 to-warning-700 rounded-lg p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
          <h3 className="text-lg font-semibold mb-2">Pronósticos</h3>
          <p className="text-warning-50 mb-4 text-sm">Predice el tráfico futuro con IA</p>
          <button 
            onClick={() => window.location.href = '/predictions'}
            className="bg-white text-warning-700 px-6 py-2.5 rounded-lg font-medium hover:bg-warning-50 transition-colors shadow-md"
          >
            Ver Pronósticos
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
