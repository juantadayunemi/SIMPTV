import React, { useState, useEffect, useRef } from 'react';
import { Camera, MapPin, Wifi, WifiOff, Settings, Plus } from 'lucide-react';
import { trafficService, type TrafficAnalysis } from '../../services/traffic.service';
import { getWebSocketService } from '../../services/websocket.service';
import TrafficStatusBadge from '../../components/traffic/TrafficStatusBadge';
import AddCameraModal, { type CameraFormData } from '../../components/traffic/AddCameraModal';
import EditCameraModal from '../../components/traffic/EditCameraModal';
import CameraMenuDropdown from '../../components/traffic/CameraMenuDropdown';
import ConnectPathModal from '../../components/traffic/ConnectPathModal';
import BoundingBoxDrawer from '../../components/traffic/BoundingBoxDrawer';
import { CameraEntity, StatusCameraKey } from '@traffic-analysis/shared';

interface CameraUIEntity extends CameraEntity {
  location?: string;
  lastAnalysis?: TrafficAnalysis;
  isPlaying?: boolean;
  videoUrl?: string;
}

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number];
  confidence: number;
}

interface LiveAnalysisData {
  vehicleCount: number;
  avgSpeed: number;
  congestion: number;
  lastUpdate: number;
}

// 🔥 BUFFER DE DETECCIONES CON TIMESTAMP
interface DetectionBuffer {
  [timestamp: number]: Detection[];
}

const CamerasPage: React.FC = () => {
  const [cameras, setCameras] = useState<CameraUIEntity[]>([]);
  const [liveAnalysis, setLiveAnalysis] = useState<Record<number, LiveAnalysisData>>({});
  const [currentDetections, setCurrentDetections] = useState<Record<number, Detection[]>>({});
  
  // 🔥 Buffer de detecciones ordenado por timestamp
  const [detectionBuffer, setDetectionBuffer] = useState<Record<number, DetectionBuffer>>({});
  
  const [filterStatus, setFilterStatus] = useState<'all' | StatusCameraKey>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showConnectPathModal, setShowConnectPathModal] = useState(false);
  const [cameraToEdit, setCameraToEdit] = useState<CameraUIEntity | null>(null);
  const [cameraToConnect, setCameraToConnect] = useState<CameraUIEntity | null>(null);

  const wsRef = useRef<any>(null);
  const videoRefs = useRef<Record<number, HTMLVideoElement | null>>({});
  const [isBuffering, setIsBuffering] = useState<Record<number, boolean>>({});
  
  // 🔥 Ref para tracking de sincronización
  const syncInfoRef = useRef<Record<number, {
    videoStartTime: number;
    lastUpdateTime: number;
    bufferedDetections: DetectionBuffer;
  }>>({});

  useEffect(() => {
    console.log('📷 CamerasPage: Montando componente...');
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      setIsLoading(true);
      const camerasData = await trafficService.getCameras();
      let analyses: TrafficAnalysis[] = [];
      
      try {
        analyses = await trafficService.getAnalyses();
      } catch (analysisError) {
        console.warn('⚠️ No se pudieron cargar análisis:', analysisError);
      }
      
      const camerasUI: CameraUIEntity[] = camerasData.map((camera) => {
        const lastAnalysis = analyses.length > 0 ? analyses[0] : undefined;
        
        let status: StatusCameraKey = StatusCameraKey.INACTIVE;
        if (camera.status === 'ACTIVE') {
          status = StatusCameraKey.ACTIVE;
        } else if (camera.status === 'MAINTENANCE') {
          status = StatusCameraKey.MAINTENANCE;
        }
        
        return {
          id: camera.id,
          name: camera.name,
          brand: camera.brand,
          model: camera.model,
          resolution: camera.resolution,
          fps: camera.fps,
          locationId: camera.locationId,
          location: `Ubicación ID: ${camera.locationId}`,
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
    } catch (error: any) {
      console.error('🛑 Error loading cameras:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddCamera = async (cameraData: CameraFormData) => {
    try {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      if (!token) {
        throw new Error('No estás autenticado');
      }
      
      const location = await trafficService.createLocation({
        description: cameraData.locationDescription,
        latitude: cameraData.latitude,
        longitude: cameraData.longitude,
        city: cameraData.city,
        province: cameraData.province,
        country: cameraData.country,
        notes: `Ubicación creada para cámara: ${cameraData.name}`,
      });

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

      await loadCameras();
      alert(`Cámara "${cameraData.name}" creada exitosamente!`);
    } catch (error: any) {
      console.error('Error creating camera:', error);
      throw new Error(error.response?.data?.message || error.message);
    }
  };

  const handleEditCamera = (camera: CameraEntity) => {
    setCameraToEdit(camera);
    setShowEditModal(true);
  };

  const handleSaveCamera = async (updatedCamera: CameraEntity) => {
    try {
      const updateData: any = {
        name: updatedCamera.name,
        status: updatedCamera.status,
      };

      if (updatedCamera.locationId) {
        updateData.locationId = updatedCamera.locationId;
      }

      await trafficService.updateCamera(updatedCamera.id, updateData);
      await loadCameras();
    } catch (error: any) {
      console.error('🛑 Error al guardar cámara:', error);
      alert(`Error: ${error.response?.data?.message || error.message}`);
    }
  };

  const handleConnectPath = (camera: CameraEntity) => {
    setCameraToConnect(camera);
    setShowConnectPathModal(true);
  };

  const handleConnectUrl = (camera: CameraEntity) => {
    alert(`Conectar URL para: ${camera.name}\n(Por implementar)`);
  };

  const handleConnectCamera = (camera: CameraEntity) => {
    alert(`Conectar Cámara física para: ${camera.name}\n(Por implementar)`);
  };

  // 🔥 SINCRONIZACIÓN MEJORADA CON BUFFER INICIAL
const handlePlayVideo = (videoFile: File, analysisId: number) => {
  if (!cameraToConnect) return;

  console.log(`🎬 Iniciando reproducción sincronizada - Cámara ${cameraToConnect.id}`);

  const videoUrl = URL.createObjectURL(videoFile);
  const cameraId = cameraToConnect.id;

  // Inicializar buffer de detecciones
  syncInfoRef.current[cameraId] = {
    videoStartTime: Date.now(),
    lastUpdateTime: Date.now(),
    bufferedDetections: {},
  };

  setDetectionBuffer(prev => ({
    ...prev,
    [cameraId]: {}
  }));

  // ✅ Mostrar estado de buffering
  setIsBuffering(prev => ({ ...prev, [cameraId]: true }));

  const ws = getWebSocketService();
  wsRef.current = ws;
  
  ws.connect(analysisId).then(() => {
    console.log(`✅ WebSocket conectado - Análisis ${analysisId}`);
   
    // ✅ Contador para buffer inicial
    let detectionsReceived = 0;
    const MIN_DETECTIONS_TO_START = 3; // Esperar al menos 5 frames procesados

    // Evento: Progreso
    ws.on('progress_update', (data: any) => {
      setLiveAnalysis(prev => ({
        ...prev,
        [cameraId]: {
          vehicleCount: data.vehicles_detected || 0,
          avgSpeed: Math.max(10, 80 - (data.vehicles_detected || 0) * 1.2),
          congestion: Math.min(100, Math.round(((data.vehicles_detected || 0) / 100) * 100)),
          lastUpdate: Date.now(),
        }
      }));
    });

    // 🔥 Evento CRÍTICO: Frame procesado con buffer
    ws.on('frame_processed', (data: {
      frame_number: number;
      timestamp: number;
      detections: Detection[];
      real_time_offset?: number;
    }) => {
      console.log(`🎥 Frame ${data.frame_number} @ ${data.timestamp.toFixed(2)}s - ${data.detections.length} detecciones`);
      
      if (data.real_time_offset) {
        console.log(`⏱️ Offset de sincronización: ${(data.real_time_offset * 1000).toFixed(0)}ms`);
      }

      // Guardar en buffer con timestamp redondeado a centésimas
      const timeKey = Math.round(data.timestamp * 100) / 100;
      
      setDetectionBuffer(prev => ({
        ...prev,
        [cameraId]: {
          ...(prev[cameraId] || {}),
          [timeKey]: data.detections
        }
      }));

      // Actualizar info de sincronización
      if (syncInfoRef.current[cameraId]) {
        syncInfoRef.current[cameraId].lastUpdateTime = Date.now();
        syncInfoRef.current[cameraId].bufferedDetections[timeKey] = data.detections;
      }

      // ✅ Incrementar contador de detecciones recibidas
      detectionsReceived++;

      // ✅ INICIAR VIDEO SOLO DESPUÉS DE RECIBIR SUFICIENTE BUFFER
      if (detectionsReceived === MIN_DETECTIONS_TO_START) {
        console.log(`🎬 Buffer cargado (${detectionsReceived} frames), iniciando video...`);
        
        // Ocultar indicador de buffering
        setIsBuffering(prev => ({ ...prev, [cameraId]: false }));
        
        // Actualizar estado de la cámara
        setCameras(prev =>
          prev.map(cam =>
            cam.id === cameraId
              ? { ...cam, status: StatusCameraKey.ACTIVE, isPlaying: true, videoUrl }
              : cam
          )
        );

        // ✅ Iniciar video con delay adicional de 500ms
        setTimeout(() => {
          const video = videoRefs.current[cameraId];
          if (video) {
            video.play().then(() => {
              console.log('▶️ Video reproduciendo');
            }).catch((err) => {
              console.error('❌ Error iniciando video:', err);
            });
          }
        }, 500);
      }
    });

    // Evento: Vehículo detectado
    ws.on('vehicle_detected', (data: any) => {
      console.log(`🚗 Nuevo vehículo: ${data.vehicle_type} (ID: ${data.track_id})`);
    });

    // Evento: Análisis completado
    ws.on('processing_complete', (data: any) => {
      console.log(`✅ Análisis completado: ${data.total_vehicles} vehículos`);
      
      setLiveAnalysis(prev => ({
        ...prev,
        [cameraId]: {
          vehicleCount: data.total_vehicles || 0,
          avgSpeed: Math.max(10, 80 - (data.total_vehicles || 0) * 1.2),
          congestion: Math.min(100, Math.round(((data.total_vehicles || 0) / 100) * 100)),
          lastUpdate: Date.now(),
        }
      }));
      
      setTimeout(() => {
        ws.disconnect();
        console.log('🔌 WebSocket desconectado');
      }, 2000);
    });

    // Evento: Error
    ws.on('processing_error', (data: any) => {
      console.error(`❌ Error en análisis:`, data);
      setIsBuffering(prev => ({ ...prev, [cameraId]: false }));
      alert(`Error: ${data.error}`);
    });
    
  }).catch((err) => {
    console.error(`❌ WebSocket error:`, err);
    setIsBuffering(prev => ({ ...prev, [cameraId]: false }));
    alert('Error conectando WebSocket');
  });
};




  // 🔥 FUNCIÓN DE SINCRONIZACIÓN CON INTERPOLACIÓN
   const getDetectionsForTime = (cameraId: number, currentTime: number): Detection[] => {
      const buffer = detectionBuffer[cameraId];
      if (!buffer) return [];

      // 🔥 CLAVE: Buscar la última detección ANTES del tiempo actual
      const timestamps = Object.keys(buffer)
        .map(Number)
        .sort((a, b) => a - b);  // Ordenar ascendente

      // Filtrar solo timestamps que ya pasaron (antes o igual al tiempo actual)
      const pastTimestamps = timestamps.filter(t => t <= currentTime);

      if (pastTimestamps.length === 0) return [];

      // Tomar la última detección disponible
      const lastValidTimestamp = pastTimestamps[pastTimestamps.length - 1];
      
      // 🎯 Solo usar si no está muy antigua (máximo 1 segundo atrás)
      const timeDifference = currentTime - lastValidTimestamp;
      if (timeDifference > 1.0) return [];  // Detección muy antigua, descartarla

      return buffer[lastValidTimestamp];
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
      default:
        return <WifiOff className="w-4 h-4 text-error-500" />;
    }
  };

  const getStatusText = (status: StatusCameraKey) => {
    switch (status) {
      case StatusCameraKey.ACTIVE: return 'Activa';
      case StatusCameraKey.MAINTENANCE: return 'En Mantenimiento';
      default: return 'Inactiva';
    }
  };

  const getStatusColor = (status: StatusCameraKey) => {
    switch (status) {
      case StatusCameraKey.ACTIVE:
        return 'text-success-600 bg-success-50 border-success-200';
      case StatusCameraKey.MAINTENANCE:
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

  return (
    <div className="space-y-6">
      {/* Header y Controles */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Gestión de Cámaras</h2>
            <p className="text-sm text-gray-600">
              {filteredCameras.length} de {cameras.length} cámaras
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
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

      {/* Estadísticas */}
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

      {/* Grid de Cámaras */}
      {!isLoading && filteredCameras.length > 0 && (
        <div className="grid grid-cols-1 gap-6">
          {filteredCameras.map((camera) => {
            const live = liveAnalysis[camera.id];
            const vehicleCount = live?.vehicleCount ?? 0;
            const trafficLevel = getTrafficLevel(vehicleCount);
            const congestionPercentage = live?.congestion ?? 0;
            const averageSpeed = live?.avgSpeed ?? 0;
            
            return (
              <div
                key={camera.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Video Feed */}
                <div className="aspect-video bg-gray-900 relative">
                  {camera.isPlaying && camera.videoUrl ? (
                    <div className="relative w-full h-full bg-black">
                      <video
                        ref={(el) => { 
                          videoRefs.current[camera.id] = el;
                          if (el) {
                            el.playbackRate = 1;  // 100% velocidad
                            // el.playbackRate = 0.25;  // 25% velocidad (cuarto)
                            // el.playbackRate = 0.75;  // 75% velocidad
                          }
                        }}
                        src={camera.videoUrl}
                        autoPlay
                        loop={false}
                        muted
                        className="w-full h-full object-contain"

                        onTimeUpdate={(e) => {
                            const currentTime = e.currentTarget.currentTime;
                            
                            // 🔥 Obtener detecciones sincronizadas
                            const detections = getDetectionsForTime(camera.id, currentTime);
                            
                            setCurrentDetections(prev => ({
                              ...prev,
                              [camera.id]: detections
                            }));
                        }}

                        onEnded={() => {
                          console.log('🎬 Video finalizado');
                          setCurrentDetections(prev => {
                            const newDet = { ...prev };
                            delete newDet[camera.id];
                            return newDet;
                          });
                        }}
                      />

                      {/* Overlay de Bounding Boxes */}
                      {currentDetections[camera.id]?.length > 0 && (
                        <BoundingBoxDrawer
                          videoRef={{ current: videoRefs.current[camera.id] }}
                          detections={currentDetections[camera.id]}
                        />
                      )}
                      
                      {/* Contador de detecciones */}
                      <div className="absolute bottom-3 left-3 bg-black bg-opacity-70 text-white px-3 py-2 rounded-lg text-sm font-mono">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span>{currentDetections[camera.id]?.length || 0} vehículos</span>
                        </div>
                      </div>

                      {/* Indicador de sincronización */}
                      <div className="absolute bottom-3 right-3 bg-black bg-opacity-70 text-white px-3 py-2 rounded-lg text-xs font-mono">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span>Buffer: {Object.keys(detectionBuffer[camera.id] || {}).length} frames</span>
                        </div>
                      </div>
                    </div>
                  ) : (
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
                  {camera.isPlaying && camera.videoUrl && (
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

                  {camera.isPlaying && camera.videoUrl && (
                    <>
                      <div className="flex items-center justify-between mb-3">
                        <TrafficStatusBadge level={trafficLevel} size="sm" />
                        <span className="text-xs text-gray-600">
                          {new Date().toLocaleTimeString('es-MX', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-center">
                          <p className="text-gray-600">Velocidad</p>
                          <p className="font-semibold text-gray-900">{Math.round(averageSpeed)} km/h</p>
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

                  {!camera.isPlaying && camera.status !== StatusCameraKey.ACTIVE && (
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

      {/* Modales */}
      <AddCameraModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddCamera}
      />

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

      {cameraToConnect && (
        <ConnectPathModal
          isOpen={showConnectPathModal}
          onClose={() => {
            setShowConnectPathModal(false);
            setCameraToConnect(null);
          }}
          cameraName={cameraToConnect.name}
          cameraId={cameraToConnect.id}
          locationId={cameraToConnect.locationId}
          userId={1}
          onPlay={handlePlayVideo}
        />
      )}
    </div>
  );
};

export default CamerasPage;