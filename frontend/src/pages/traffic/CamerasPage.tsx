import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, MapPin, Wifi, WifiOff, Settings, Plus } from 'lucide-react';
import { trafficService, type TrafficAnalysis } from '../../services/traffic.service';
import { getWebSocketService, ProgressUpdate,  ProcessingComplete } from '../../services/websocket.service';
import TrafficStatusBadge from '../../components/traffic/TrafficStatusBadge';
import AddCameraModal, { type CameraFormData } from '../../components/traffic/AddCameraModal';
import EditCameraModal from '../../components/traffic/EditCameraModal';
import CameraMenuDropdown from '../../components/traffic/CameraMenuDropdown';
import ConnectPathModal from '../../components/traffic/ConnectPathModal';
import { CameraEntity, StatusCameraKey } from '@traffic-analysis/shared';

// Tipo extendido para la UI que incluye propiedades adicionales
interface CameraUIEntity extends CameraEntity {
  location?: string; // Descripción de ubicación para mostrar
  lastAnalysis?: TrafficAnalysis; // Último análisis realizado
  isPlaying?: boolean; // Si está reproduciendo video
  videoUrl?: string; // URL del video en reproducción
}

const CamerasPage: React.FC = () => {
  const navigate = useNavigate();

  const [cameras, setCameras] = useState<CameraUIEntity[]>([]);
  // Para almacenar datos de análisis en tiempo real por cámara
  const [liveAnalysis, setLiveAnalysis] = useState<Record<number, {
    vehicleCount: number;
    avgSpeed: number;
    congestion: number;
    lastUpdate: number;
  }>>({});
  const wsRef = useRef<any>(null);
  // 'all' es solo para filtrado en UI, no está en la base de datos
  const [filterStatus, setFilterStatus] = useState<'all' | StatusCameraKey>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showConnectPathModal, setShowConnectPathModal] = useState(false);
  const [cameraToEdit, setCameraToEdit] = useState<CameraUIEntity | null>(null);
  const [cameraToConnect, setCameraToConnect] = useState<CameraUIEntity | null>(null);

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
      const camerasUI: CameraUIEntity[] = camerasData.map((camera) => {
        // Buscar el último análisis de esta cámara (por ahora no filtramos por cameraId porque TrafficAnalysis no lo tiene)
        const lastAnalysis = analyses.length > 0 ? analyses[0] : undefined;
        
        // Convertir status del backend (string) al tipo StatusCameraKey
        // El backend devuelve: 'ACTIVE', 'INACTIVE', 'MAINTENANCE'
        let status: StatusCameraKey = StatusCameraKey.INACTIVE;
        if (camera.status === 'ACTIVE') {
          status = StatusCameraKey.ACTIVE;
        } else if (camera.status === 'MAINTENANCE') {
          status = StatusCameraKey.MAINTENANCE;
        } else if (camera.status === 'INACTIVE') {
          status = StatusCameraKey.INACTIVE;
        }
        
        return {
          id: camera.id,
          name: camera.name,
          brand: camera.brand,
          model: camera.model,
          resolution: camera.resolution,
          fps: camera.fps,
          locationId: camera.locationId,
          location: `Ubicación ID: ${camera.locationId}`, // Descripción simple, luego podemos mejorar
          isActive: camera.isActive,
          status: status,
          lanes: camera.lanes,
          coversBothDirections: camera.coversBothDirections,
          notes: camera.notes,
          createdAt: new Date(camera.createdAt),
          updatedAt: new Date(camera.updatedAt),
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

  const handleEditCamera = (camera: CameraEntity) => {
    setCameraToEdit(camera);
    setShowEditModal(true);
  };

  const handleSaveCamera = async (updatedCamera: CameraEntity) => {
    try {
      console.log('💾 Guardando cambios de cámara:', updatedCamera);
      
      // Preparar datos para el API
      // El status ya viene en el formato correcto: 'ACTIVE', 'INACTIVE', 'MAINTENANCE'
      const updateData: any = {
        name: updatedCamera.name,
        status: updatedCamera.status, // Ya está en mayúsculas desde el enum
      };

      // Si se seleccionó una ubicación nueva, incluirla
      if (updatedCamera.locationId) {
        updateData.locationId = updatedCamera.locationId;
      }

      // Llamar al API para actualizar
      const updatedCameraFromApi = await trafficService.updateCamera(updatedCamera.id, updateData);
      console.log('✅ Cámara actualizada en el servidor:', updatedCameraFromApi);

      // Recargar la lista completa de cámaras para reflejar los cambios
      await loadCameras();
      
      console.log('✅ Lista de cámaras recargada');
    } catch (error: any) {
      console.error('❌ Error al guardar cámara:', error);
      console.error('❌ Detalles del error:', error.response?.data);
      // En caso de error, mostrar mensaje al usuario
      alert(`Error al guardar los cambios: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleConnectPath = (camera: CameraEntity) => {
    setCameraToConnect(camera);
    setShowConnectPathModal(true);
  };

  const handleConnectUrl = (camera: CameraEntity) => {
    // TODO: Implementar modal de URL
    alert(`Conectar URL para: ${camera.name}\n(Por implementar)`);
  };

  const handleConnectCamera = (camera: CameraEntity) => {
    // TODO: Implementar modal de conexión a cámara física
    alert(`Conectar Cámara física para: ${camera.name}\n(Por implementar)`);
  };

  const handlePlayVideo = (videoFile: File, analysisId: number, cameraId: number) => {
    if (!cameraToConnect) return;

    // Actualizar la cámara para mostrarla como "reproduciendo"
    setCameras(prev =>
      prev.map(cam =>
        cam.id === cameraToConnect.id
          ? {
              ...cam,
              status: StatusCameraKey.ACTIVE,
              isPlaying: true,
              videoUrl: URL.createObjectURL(videoFile)
            }
          : cam
      )
    );

    // Redirigir a la página de análisis en vivo con analysisId
    navigate(`/camera/${cameraId}`, {
      state: {
        analysisId, // El análisis contiene el videoPath
      }
    });

    // Usar analysisId real generado para la sesión de análisis
    const ws = getWebSocketService();
    wsRef.current = ws;
  ws.connect(analysisId).then(() => {
      // Escuchar progreso de análisis
      ws.on('progress_update', (data: ProgressUpdate) => {
        setLiveAnalysis(prev => ({
          ...prev,
          [cameraToConnect.id]: {
            vehicleCount: data.vehicles_detected,
            avgSpeed: Math.max(10, 80 - data.vehicles_detected * 1.2),
            congestion: Math.min(100, Math.round((data.vehicles_detected / 100) * 100)),
            lastUpdate: Date.now(),
          }
        }));
      });
      // Escuchar finalización
      ws.on('processing_complete', (data: ProcessingComplete) => {
        setLiveAnalysis(prev => ({
          ...prev,
          [cameraToConnect.id]: {
            vehicleCount: data.total_vehicles,
            avgSpeed: Math.max(10, 80 - data.total_vehicles * 1.2),
            congestion: Math.min(100, Math.round((data.total_vehicles / 100) * 100)),
            lastUpdate: Date.now(),
          }
        }));
        // Desconectar WebSocket tras finalizar
        setTimeout(() => ws.disconnect(), 2000);
      });
    }).catch((err) => {
      console.error('WebSocket error:', err);
    });
  };

  const filteredCameras = cameras.filter(camera => 
    filterStatus === 'all' || camera.status === filterStatus
  );

  const getStatusIcon = (status: StatusCameraKey) => {
    switch (status) {
      case StatusCameraKey.ACTIVE:
        return <Wifi className="w-4 h-4 text-success-500" />;
      case StatusCameraKey.MAINTENANCE:
        return <Settings className="w-4 h-4 text-warning-500" />;
      case StatusCameraKey.INACTIVE:
      default:
        return <WifiOff className="w-4 h-4 text-error-500" />;
    }
  };

  const getStatusText = (status: StatusCameraKey) => {
    switch (status) {
      case StatusCameraKey.ACTIVE:
        return 'Activa';
      case StatusCameraKey.MAINTENANCE:
        return 'En Mantenimiento';
      case StatusCameraKey.INACTIVE:
      default:
        return 'Inactiva';
    }
  };

  const getStatusColor = (status: StatusCameraKey) => {
    switch (status) {
      case StatusCameraKey.ACTIVE:
        return 'text-success-600 bg-success-50 border-success-200';
      case StatusCameraKey.MAINTENANCE:
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case StatusCameraKey.INACTIVE:
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
              onChange={(e) => setFilterStatus(e.target.value as 'all' | StatusCameraKey)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">Todas las cámaras</option>
              <option value={StatusCameraKey.ACTIVE}>Activas</option>
              <option value={StatusCameraKey.MAINTENANCE}>En Mantenimiento</option>
              <option value={StatusCameraKey.INACTIVE}>Inactivas</option>
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
                {cameras.filter(c => c.status === StatusCameraKey.ACTIVE).length}
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
                {cameras.filter(c => c.status === StatusCameraKey.MAINTENANCE).length}
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
                {cameras.filter(c => c.status === StatusCameraKey.INACTIVE).length}
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
            // Si hay datos en vivo, usarlos; si no, usar el último análisis
            const live = liveAnalysis[camera.id];
            const analysis = camera.lastAnalysis;
            const vehicleCount = live?.vehicleCount ?? analysis?.vehicleCount ?? 0;
            const trafficLevel = getTrafficLevel(vehicleCount);
            const congestionPercentage = live?.congestion ?? getCongestionPercentage(vehicleCount);
            const averageSpeed = live?.avgSpeed ?? getAverageSpeed(vehicleCount);
            
            return (
              <div
                key={camera.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
              >
                {/* Camera Feed Placeholder */}
                <div className="aspect-video bg-gray-900 relative">
                  {camera.isPlaying && camera.videoUrl ? (
                    /* Video Reproduciéndose */
                    <video
                      src={camera.videoUrl}
                      autoPlay
                      loop
                      muted
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    /* Placeholder */
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm opacity-75">
                          {camera.status === StatusCameraKey.ACTIVE ? 'Transmisión en vivo' : 'Sin señal'}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {/* Status Indicator */}
                  <div className="absolute top-3 left-3">
                    <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(camera.status)}`}>
                      {getStatusIcon(camera.status)}
                      <span>{getStatusText(camera.status)}</span>
                    </div>
                  </div>

                  {/* Live Indicator */}
                  {camera.status === StatusCameraKey.ACTIVE && camera.isPlaying && camera.videoUrl && (
                    <div className="absolute top-3 right-3">
                      <div className="flex items-center space-x-1 px-2 py-1 bg-red-600 text-white rounded-full text-xs font-medium">
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                        <span>ANÁLISIS EN VIVO</span>
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
                        {camera.isPlaying && (
                          <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded animate-pulse">
                            Analizando en tiempo real...
                          </span>
                        )}
                      </h3>
                      <p className="text-xs text-gray-600 flex items-center mt-1">
                        <MapPin className="w-3 h-3 mr-1" />
                        {camera.location}
                      </p>
                    </div>
                    <CameraMenuDropdown
                      onConnectPath={() => handleConnectPath(camera)}
                      onConnectUrl={() => handleConnectUrl(camera)}
                      onConnectCamera={() => handleConnectCamera(camera)}
                      onConfigure={() => handleEditCamera(camera)}
                    />
                  </div>

                  {/* Mostrar estadísticas solo para cámaras ACTIVAS */}
                  {camera.status === StatusCameraKey.ACTIVE && camera.isPlaying && camera.videoUrl && (
                    <>
                      <div className="flex items-center justify-between mb-3">
                        <TrafficStatusBadge level={trafficLevel} size="sm" />
                        <span className="text-xs text-gray-600">
                          {analysis 
                            ? new Date(analysis.createdAt).toLocaleTimeString('es-MX', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })
                            : 'Actualizando...'
                          }
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

                  {/* Mensajes para cámaras NO ACTIVAS */}
                  {camera.status !== StatusCameraKey.ACTIVE && (
                    <div className="text-center py-4">
                      <p className="text-sm text-gray-500">
                        {camera.status === StatusCameraKey.MAINTENANCE 
                          ? 'En Mantenimiento - Procesando análisis de tráfico...'
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

      {/* Add Camera Modal */}
      <AddCameraModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddCamera}
      />

      {/* Edit Camera Modal */}
      {cameraToEdit && (
        <EditCameraModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false);
            setCameraToEdit(null);
          }}
          onSave={handleSaveCamera}
          camera={cameraToEdit}
        />
      )}

      {/* Connect Path Modal */}
      {cameraToConnect && (
        <ConnectPathModal
          isOpen={showConnectPathModal}
          onClose={() => {
            setShowConnectPathModal(false);
            setCameraToConnect(null);
          }}
          cameraName={cameraToConnect.name}
          cameraId={cameraToConnect.id}
          onPlay={handlePlayVideo}
        />
      )}
    </div>
  );
};

export default CamerasPage;
