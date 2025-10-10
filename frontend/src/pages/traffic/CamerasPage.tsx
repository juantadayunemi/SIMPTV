import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, MapPin, Wifi, WifiOff, Settings, Eye, MoreVertical, Plus } from 'lucide-react';
import { trafficService, type TrafficAnalysis } from '../../services/traffic.service';
import TrafficStatusBadge from '../../components/traffic/TrafficStatusBadge';
import AddCameraModal, { type CameraFormData } from '../../components/traffic/AddCameraModal';

// Mock data para simular cámaras mientras no tengamos un endpoint específico
interface CameraData {
  id: string;
  name: string;
  location: string;
  status: 'active' | 'inactive' | 'maintenance';
  lastAnalysis?: TrafficAnalysis;
  videoUrl?: string;
}

const CamerasPage: React.FC = () => {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'maintenance'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Cargar análisis de tráfico y convertirlos a "cámaras"
  useEffect(() => {
    console.log('🎥 CamerasPage: Mounting component...');
    console.log('🔑 Token en localStorage:', localStorage.getItem('access_token') ? 'SÍ' : 'NO');
    console.log('🔑 Token en sessionStorage:', sessionStorage.getItem('access_token') ? 'SÍ' : 'NO');
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      setIsLoading(true);
      console.log('📡 Cargando cámaras desde el backend...');
      
      // Cargar cámaras reales del backend
      const camerasData = await trafficService.getCameras();
      console.log('✅ Cámaras recibidas:', camerasData.length);
      
      // Intentar cargar análisis (opcional, no bloquea si falla)
      let analyses: TrafficAnalysis[] = [];
      try {
        analyses = await trafficService.getAnalyses();
        console.log('✅ Análisis recibidos:', analyses.length);
      } catch (analysisError) {
        console.warn('⚠️ No se pudieron cargar análisis, continuando sin ellos:', analysisError);
      }
      
      // Convertir cámaras del backend al formato de la UI
      const camerasUI: CameraData[] = camerasData.map((camera) => {
        // Buscar el último análisis de esta cámara (por ahora no filtramos por cameraId porque TrafficAnalysis no lo tiene)
        const lastAnalysis = analyses.length > 0 ? analyses[0] : undefined;
        
        return {
          id: camera.id.toString(),
          name: camera.name,
          location: `Lat: ${camerasData.find(c => c.id === camera.id)?.locationId || 'N/A'}`,
          status: camera.isActive ? 'active' : 'inactive',
          lastAnalysis: lastAnalysis
        };
      });

      setCameras(camerasUI);
      console.log('✅ Cámaras creadas:', camerasUI.length);
    } catch (error: any) {
      console.error('❌ Error loading cameras:', error);
      console.error('❌ Error response:', error.response);
      
      // Si es un error 401, el interceptor ya manejará la redirección
      // No hacemos nada aquí para evitar loops
      if (error.response?.status === 401) {
        console.error('❌ Error de autenticación detectado');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddCamera = async (cameraData: CameraFormData) => {
    try {
      console.log('📸 Creating camera:', cameraData);
      
      // Verificar autenticación antes de crear
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      if (!token) {
        throw new Error('No estás autenticado. Por favor inicia sesión primero.');
      }
      
      // 1. Crear la ubicación
      const location = await trafficService.createLocation({
        description: cameraData.locationDescription,
        latitude: cameraData.latitude,
        longitude: cameraData.longitude,
        city: cameraData.city,
        province: cameraData.province,
        country: cameraData.country,
        notes: `Ubicación creada para cámara: ${cameraData.name}`,
      });
      
      console.log('✅ Location created:', location);
      
      // 2. Crear la cámara
      const camera = await trafficService.createCamera({
        name: cameraData.name,
        brand: cameraData.brand,
        model: cameraData.model,
        resolution: cameraData.resolution,
        fps: cameraData.fps,
        locationId: location.id,
        lanes: cameraData.lanes,
        coversBothDirections: cameraData.coversBothDirections,
        notes: cameraData.notes,
      });
      
      console.log('✅ Camera created:', camera);
      
      // 3. Recargar cámaras
      await loadCameras();
      
      alert(`Cámara "${cameraData.name}" creada exitosamente!`);
    } catch (error: any) {
      console.error('Error creating camera:', error);
      
      // Manejar error 401 específicamente
      if (error.response?.status === 401) {
        throw new Error('Sesión expirada. Por favor inicia sesión nuevamente.');
      }
      
      throw new Error(error.response?.data?.message || error.message || 'Error al crear la cámara');
    }
  };

  const filteredCameras = cameras.filter(camera => 
    filterStatus === 'all' || camera.status === filterStatus
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Wifi className="w-4 h-4 text-success-500" />;
      case 'maintenance':
        return <Settings className="w-4 h-4 text-warning-500" />;
      default:
        return <WifiOff className="w-4 h-4 text-error-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Activa';
      case 'maintenance':
        return 'Procesando';
      default:
        return 'Inactiva';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-success-600 bg-success-50 border-success-200';
      case 'maintenance':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      default:
        return 'text-error-600 bg-error-50 border-error-200';
    }
  };

  const getTrafficLevel = (vehicleCount: number): 'low' | 'moderate' | 'heavy' | 'congested' => {
    if (vehicleCount < 10) return 'low';
    if (vehicleCount < 30) return 'moderate';
    if (vehicleCount < 50) return 'heavy';
    return 'congested';
  };

  const getCongestionPercentage = (vehicleCount: number): number => {
    // Estimación simple: máximo 100 vehículos = 100%
    return Math.min(Math.round((vehicleCount / 100) * 100), 100);
  };

  const getAverageSpeed = (vehicleCount: number): number => {
    // Estimación inversa: más vehículos = menor velocidad
    if (vehicleCount < 10) return Math.floor(Math.random() * 20) + 60; // 60-80 km/h
    if (vehicleCount < 30) return Math.floor(Math.random() * 20) + 40; // 40-60 km/h
    if (vehicleCount < 50) return Math.floor(Math.random() * 20) + 20; // 20-40 km/h
    return Math.floor(Math.random() * 15) + 5; // 5-20 km/h
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Gestión de Cámaras</h2>
            <p className="text-sm text-gray-600">
              {filteredCameras.length} de {cameras.length} cámaras
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
            {/* Filter */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">Todas las cámaras</option>
              <option value="active">Activas</option>
              <option value="maintenance">Procesando</option>
              <option value="inactive">Inactivas</option>
            </select>

            {/* Add Camera Button */}
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 font-medium"
            >
              <Plus className="w-5 h-5 mr-2" />
              Agregar nueva cámara
            </button>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cámaras</p>
              <p className="text-2xl font-bold text-gray-900">{cameras.length}</p>
            </div>
            <Camera className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Activas</p>
              <p className="text-2xl font-bold text-success-600">
                {cameras.filter(c => c.status === 'active').length}
              </p>
            </div>
            <Wifi className="w-8 h-8 text-success-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Mantenimiento</p>
              <p className="text-2xl font-bold text-warning-600">
                {cameras.filter(c => c.status === 'maintenance').length}
              </p>
            </div>
            <Settings className="w-8 h-8 text-warning-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inactivas</p>
              <p className="text-2xl font-bold text-error-600">
                {cameras.filter(c => c.status === 'inactive').length}
              </p>
            </div>
            <WifiOff className="w-8 h-8 text-error-500" />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando cámaras...</p>
        </div>
      )}

      {/* Cameras Grid */}
      {!isLoading && filteredCameras.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCameras.map((camera) => {
            const analysis = camera.lastAnalysis;
            const vehicleCount = analysis?.vehicleCount || 0;
            const trafficLevel = getTrafficLevel(vehicleCount);
            const congestionPercentage = getCongestionPercentage(vehicleCount);
            const averageSpeed = getAverageSpeed(vehicleCount);
            
            return (
              <div
                key={camera.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedCamera(camera.id)}
              >
                {/* Camera Feed Placeholder */}
                <div className="aspect-video bg-gray-900 relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-white">
                      <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm opacity-75">
                        {camera.status === 'active' ? 'Transmisión en vivo' : 'Sin señal'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Status Indicator */}
                  <div className="absolute top-3 left-3">
                    <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(camera.status)}`}>
                      {getStatusIcon(camera.status)}
                      <span>{getStatusText(camera.status)}</span>
                    </div>
                  </div>

                  {/* Live Indicator */}
                  {camera.status === 'active' && (
                    <div className="absolute top-3 right-3">
                      <div className="flex items-center space-x-1 px-2 py-1 bg-red-600 text-white rounded-full text-xs font-medium">
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                        <span>EN VIVO</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Camera Info */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 text-sm leading-tight">
                        {camera.name}
                      </h3>
                      <p className="text-xs text-gray-600 flex items-center mt-1">
                        <MapPin className="w-3 h-3 mr-1" />
                        {camera.location}
                      </p>
                    </div>
                    <button 
                      className="p-1 hover:bg-gray-100 rounded"
                      onClick={(e) => {
                        e.stopPropagation();
                        // TODO: Menú de opciones
                      }}
                    >
                      <MoreVertical className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>

                  {analysis && camera.status === 'active' && (
                    <>
                      <div className="flex items-center justify-between mb-3">
                        <TrafficStatusBadge level={trafficLevel} size="sm" />
                        <span className="text-xs text-gray-600">
                          {new Date(analysis.createdAt).toLocaleTimeString('es-MX', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-center">
                          <p className="text-gray-600">Velocidad</p>
                          <p className="font-semibold text-gray-900">{averageSpeed} km/h</p>
                        </div>
                        <div className="text-center">
                          <p className="text-gray-600">Vehículos</p>
                          <p className="font-semibold text-gray-900">{vehicleCount}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-gray-600">Congestión</p>
                          <p className="font-semibold text-gray-900">{congestionPercentage}%</p>
                        </div>
                      </div>
                    </>
                  )}

                  {camera.status !== 'active' && (
                    <div className="text-center py-4">
                      <p className="text-sm text-gray-500">
                        {camera.status === 'maintenance' 
                          ? 'Procesando análisis de tráfico...'
                          : 'Cámara fuera de servicio'
                        }
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredCameras.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Camera className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {cameras.length === 0 ? 'No hay cámaras registradas' : 'No se encontraron cámaras'}
          </h3>
          <p className="text-gray-600 mb-4">
            {cameras.length === 0 
              ? 'Comienza agregando tu primera cámara para monitorear el tráfico.'
              : 'No hay cámaras que coincidan con el filtro seleccionado.'
            }
          </p>
          {cameras.length === 0 && (
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
            >
              <Plus className="w-5 h-5 mr-2" />
              Agregar primera cámara
            </button>
          )}
        </div>
      )}

      {/* Add Camera Modal (Placeholder) */}
      <AddCameraModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddCamera}
      />
    </div>
  );
};

export default CamerasPage;
