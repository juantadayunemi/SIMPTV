import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Camera, Play, Pause, RotateCcw } from 'lucide-react';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity } from '@traffic-analysis/shared';
import { getWebSocketService, cleanupWebSocketService } from '../../services/websocket.service';
import { DetectionLogPanel } from '../../components/traffic/DetectionLogPanel';
import type { RealtimeDetectionEvent } from '@traffic-analysis/shared';

interface CameraLiveData {
  vehicleCount: number;
  avgSpeed: number;
  congestion: number;
  lastUpdate: string;
  startTime: string;
  elapsedSeconds: number;
}

interface LocationState {
  analysisId?: number;
  videoPath?: string;
}

export const CameraLiveAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const locationState = useLocation().state as LocationState;
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [camera, setCamera] = useState<CameraEntity | null>(null);
  const [location, setLocation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analysisId, setAnalysisId] = useState<number | null>(locationState?.analysisId || null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [showProcessedFrames, setShowProcessedFrames] = useState(false);
  
  // Estado de análisis
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  // Progreso de carga (YOLOv8, PaddleOCR)
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [isLoadingModels, setIsLoadingModels] = useState<boolean>(false);
  
  // ✅ Métricas de rendimiento (FPS, latencia)
  const [fps, setFps] = useState<number>(0);
  const [latency, setLatency] = useState<number>(0);
  const [framesReceived, setFramesReceived] = useState<number>(0);
  const lastFrameTime = useRef<number>(Date.now());
  const frameTimestamps = useRef<number[]>([]);
  
  // Datos en tiempo real
  const [liveData, setLiveData] = useState<CameraLiveData>({
    vehicleCount: 0,
    avgSpeed: 0,
    congestion: 0,
    lastUpdate: new Date().toLocaleTimeString(),
    startTime: '',
    elapsedSeconds: 0,
  });

  const [detections, setDetections] = useState<RealtimeDetectionEvent[]>([]);

  // Cargar datos de la cámara
  useEffect(() => {
    if (id) {
      loadCameraData(parseInt(id));
    }
  }, [id]);

  // Conectar WebSocket para análisis en tiempo real
  useEffect(() => {
    if (!analysisId) return;

    // ✅ Obtener instancia específica para este análisis (no compartida)
    const wsService = getWebSocketService(analysisId);
    const unsubscribers: Array<() => void> = [];

    const connectWebSocket = async () => {
      try {
        await wsService.connect(analysisId);
        setIsConnected(true);
        console.log('✅ WebSocket conectado para análisis:', analysisId);

        // Suscribirse a frames procesados (con detecciones dibujadas)
        const unsubFrames = wsService.on('frame_update', (data: any) => {
          console.log('📸 Frame recibido:', data.frame_number, 'detecciones:', data.detections_count);
          
          // ✅ Calcular FPS y latencia
          const now = Date.now();
          const frameTime = data.timestamp ? new Date(data.timestamp).getTime() : now;
          const currentLatency = now - frameTime;
          
          // Actualizar latencia
          setLatency(currentLatency);
          
          // Calcular FPS (promedio de últimos 10 frames)
          frameTimestamps.current.push(now);
          if (frameTimestamps.current.length > 10) {
            frameTimestamps.current.shift();
          }
          
          if (frameTimestamps.current.length >= 2) {
            const timeDiff = (frameTimestamps.current[frameTimestamps.current.length - 1] - frameTimestamps.current[0]) / 1000;
            const calculatedFps = (frameTimestamps.current.length - 1) / timeDiff;
            setFps(Math.round(calculatedFps));
          }
          
          setFramesReceived(prev => prev + 1);
          lastFrameTime.current = now;
          
          // Dibujar frame en canvas
          if (canvasRef.current && data.frame_data) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            if (ctx) {
              const img = new Image();
              img.onload = () => {
                // Ajustar tamaño del canvas al frame
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
              };
              img.onerror = (e) => {
                console.error('❌ Error cargando imagen base64:', e);
                console.error('🔍 frame_data preview:', data.frame_data?.substring(0, 100));
              };
              // ✅ FIX: frame_data YA incluye el prefijo data:image/jpeg;base64,
              img.src = data.frame_data;
            }
          }
        });
        unsubscribers.push(unsubFrames);

        // Suscribirse a detecciones de vehículos
        const unsubVehicle = wsService.on('vehicle_detected', (data: any) => {
          console.log('🚗 Vehículo detectado (raw):', data);
          
          // ✅ OPTIMIZACIÓN: Solo agregar si es vehículo nuevo (is_new: true desde backend)
          // Esto evita duplicados ya que ByteTrack asigna IDs únicos
          const detection: RealtimeDetectionEvent = {
            timestamp: data.timestamp || new Date().toISOString(),
            vehicleType: data.vehicle_type || 'desconocido',
            plateNumber: data.plate_number || null,
            confidence: data.confidence || 0,
            bbox: data.bbox || null,
            frameNumber: data.frame_number || 0,
            trackId: data.track_id || '',
          };

          console.log('✅ Detección formateada:', detection);
          
          // Solo agregar a la lista de detecciones (sin duplicados por track_id)
          setDetections((prev) => {
            // Evitar duplicados por track_id
            const exists = prev.some(d => d.trackId === detection.trackId);
            if (!exists) {
              const newDetections = [...prev, detection];
              console.log('📋 Total detecciones ahora:', newDetections.length);
              return newDetections;
            }
            return prev;
          });
          
          // ✅ Incrementar contador SOLO para vehículos nuevos
          // El backend ya envía solo 1 evento por vehículo único
          setLiveData((prev) => ({
            ...prev,
            vehicleCount: prev.vehicleCount + 1,
            lastUpdate: new Date().toLocaleTimeString(),
          }));
        });
        unsubscribers.push(unsubVehicle);

        // Suscribirse a progreso de CARGA (YOLOv8, PaddleOCR)
        const unsubLoading = wsService.on('loading_progress', (data: any) => {
          console.log('⏳ Cargando modelos:', data.message, data.progress + '%');
          setIsLoadingModels(true);
          setLoadingProgress(data.progress || 0);
          setLoadingMessage(data.message || 'Cargando...');
          
          // Si llegó al 100%, ocultar después de 1 segundo
          if (data.progress >= 100) {
            setTimeout(() => {
              setIsLoadingModels(false);
            }, 1000);
          }
        });
        unsubscribers.push(unsubLoading);

        // Suscribirse a progreso de análisis (procesamiento de frames)
        const unsubProgress = wsService.on('progress_update', (data: any) => {
          console.log('📊 Progreso procesamiento:', data.percentage + '%');
        });
        unsubscribers.push(unsubProgress);

        // Suscribirse a completación
        const unsubComplete = wsService.on('processing_complete', (data: any) => {
          console.log('✅ Análisis completado:', data);
          setIsPlaying(false);
          setIsPaused(false);
          setShowProcessedFrames(false);
          setIsLoadingModels(false);
        });
        unsubscribers.push(unsubComplete);

        console.log('✅ WebSocket conectado para análisis:', analysisId);
      } catch (error) {
        console.error('❌ Error connecting WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    // ✅ Cleanup: desconectar y limpiar instancia al desmontar
    return () => {
      unsubscribers.forEach(unsub => unsub());
      wsService.disconnect();
      cleanupWebSocketService(analysisId); // ✅ Limpiar instancia del Map
    };
  }, [analysisId]);

  // Actualizar tiempo transcurrido cada segundo
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setLiveData((prev) => ({
        ...prev,
        elapsedSeconds: prev.elapsedSeconds + 1,
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [isPlaying]);

  // ✅ PAUSA AUTOMÁTICA: al desmontar componente
  useEffect(() => {
    return () => {
      if (isPlaying && analysisId) {
        console.log('🛑 Desmontando componente - pausando análisis');
        trafficService.pauseAnalysis(analysisId).catch(console.error);
      }
    };
  }, [isPlaying, analysisId]);

  // ✅ PAUSA AUTOMÁTICA: al cambiar de ventana/pestaña
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && isPlaying && analysisId) {
        console.log('🛑 Ventana oculta - pausando análisis automáticamente');
        trafficService.pauseAnalysis(analysisId)
          .then(() => {
            setIsPaused(true);
            setIsPlaying(false);
            setShowProcessedFrames(false);
          })
          .catch(console.error);
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isPlaying, analysisId]);

  const loadCameraData = async (cameraId: number) => {
    try {
      setLoading(true);
      
      // Cargar datos de la cámara
      const cameraData = await trafficService.getCamera(cameraId);
      setCamera(cameraData);
      
      // Cargar ubicación
      if (cameraData.locationId) {
        const locationData = await trafficService.getLocation(cameraData.locationId);
        setLocation(locationData);
      }

      // Si hay analysisId desde el state O desde la cámara, cargar el análisis
      const analysisToLoad = analysisId || cameraData.currentAnalysisId;
      
      if (analysisToLoad) {
        console.log('📥 Cargando análisis:', analysisToLoad);
        const analysisData = await trafficService.getAnalysis(analysisToLoad.toString());
        
        // Si no teníamos analysisId en el state, actualizarlo
        if (!analysisId && cameraData.currentAnalysisId) {
          setAnalysisId(cameraData.currentAnalysisId);
        }
        
        if (analysisData.videoPath) {
          // Construir URL del video desde el backend
          const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
          const videoUrl = `${baseUrl}/media/${analysisData.videoPath}`;
          console.log('🎥 Video URL:', videoUrl);
          setVideoUrl(videoUrl);
        }
      } else if (cameraData.currentVideoPath) {
        // Si la cámara tiene video pero no análisis activo, usar el videoPath directamente
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const videoUrl = `${baseUrl}/media/${cameraData.currentVideoPath}`;
        console.log('🎥 Video URL (desde cámara):', videoUrl);
        setVideoUrl(videoUrl);
      }
      
    } catch (error) {
      console.error('Error loading camera data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReconnect = async () => {
    if (!analysisId) {
      console.warn('No hay análisis activo para reconectar');
      return;
    }

    try {
      // ✅ Usar instancia específica para este análisis
      const wsService = getWebSocketService(analysisId);
      await wsService.connect(analysisId);
      setIsConnected(true);
      console.log('Reconectado a WebSocket');
    } catch (error) {
      console.error('Error al reconectar:', error);
      setIsConnected(false);
    }
  };

  const handlePause = async () => {
    if (!analysisId) return;

    try {
      const result = await trafficService.pauseAnalysis(analysisId);
      console.log('⏸️ Análisis pausado:', result);
      setIsPaused(true);
      setIsPlaying(false);
      setShowProcessedFrames(false); // ✅ Ocultar canvas procesado al pausar
    } catch (error) {
      console.error('Error al pausar análisis:', error);
    }
  };

  const handlePlay = async () => {
    if (!analysisId) {
      console.warn('No hay análisis disponible para iniciar');
      return;
    }

    try {
      if (isPaused) {
        // Reanudar
        const result = await trafficService.resumeAnalysis(analysisId);
        console.log('✅ Análisis reanudado:', result);
      } else {
        // Iniciar por primera vez
        setIsLoadingModels(true);
        setLoadingProgress(0);
        setLoadingMessage('Iniciando análisis...');
        
        const result = await trafficService.startAnalysis(analysisId);
        console.log('✅ Análisis iniciado:', result);
        setLiveData((prev) => ({
          ...prev,
          startTime: new Date().toLocaleTimeString(),
        }));
        
        // Mostrar canvas con frames procesados
        setShowProcessedFrames(true);
        console.log('▶️ Mostrando frames procesados con YOLOv8 + OCR');
      }
      setIsPlaying(true);
      setIsPaused(false);
    } catch (error) {
      console.error('Error al iniciar/reanudar análisis:', error);
      setIsLoadingModels(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando cámara...</p>
        </div>
      </div>
    );
  }

  if (!camera) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Cámara no encontrada</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {camera.name} - En Línea
              </h1>
              {location && (
                <p className="text-sm text-gray-600">
                  {location.description}, {location.city}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">En vivo</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Debug Info */}
          {analysisId && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-blue-900">
                <strong>Análisis ID:</strong> {analysisId}
              </p>
              {videoUrl && (
                <p className="text-sm text-blue-900 mt-1">
                  <strong>Video URL:</strong> {videoUrl}
                </p>
              )}
              <p className="text-sm text-blue-700 mt-1">
                {isConnected ? '✅ WebSocket conectado' : '⏳ Conectando WebSocket...'}
              </p>
            </div>
          )}

          {/* Video Player / Canvas Procesado */}
          <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg mb-6">
            <div className="relative aspect-video">
              {videoUrl ? (
                <>
                  {/* Canvas para frames procesados (visible cuando está analizando) */}
                  <canvas
                    ref={canvasRef}
                    className={`w-full h-full object-contain ${showProcessedFrames ? 'block' : 'hidden'}`}
                    style={{ backgroundColor: '#000' }}
                  />
                  
                  {/* Video original (SIN CONTROLES - solo primer frame) */}
                  <video
                    ref={videoRef}
                    src={videoUrl}
                    className={`w-full h-full object-cover ${showProcessedFrames ? 'hidden' : 'block'}`}
                    controls={false}
                    muted
                    preload="metadata"
                    onError={(e) => {
                      console.error('❌ Error cargando video:', e);
                      console.error('Video URL:', videoUrl);
                    }}
                    onLoadedMetadata={(e) => {
                      console.log('✅ Video cargado correctamente');
                      // Pausar el video en el primer frame
                      const video = e.target as HTMLVideoElement;
                      video.currentTime = 0;
                      video.pause();
                    }}
                  />
                  
                  {/* Overlay cuando NO está procesando (mostrar que está pausado) */}
                  {!showProcessedFrames && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                      <div className="text-center">
                        <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center mb-4 mx-auto">
                          <Play className="w-10 h-10 text-white" />
                        </div>
                        <p className="text-white text-xl font-semibold">Video Cargado</p>
                        <p className="text-gray-300 mt-2">Presiona "Iniciar" para comenzar el análisis</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Indicador de procesamiento */}
                  {showProcessedFrames && (
                    <div className="absolute top-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                      <span className="font-semibold">PROCESANDO EN TIEMPO REAL</span>
                    </div>
                  )}
                  
                  {/* ✅ Indicador de rendimiento (FPS y latencia) */}
                  {showProcessedFrames && isPlaying && (
                    <div className="absolute top-4 right-4 bg-black/80 text-white px-4 py-3 rounded-lg space-y-1">
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-sm font-medium">FPS:</span>
                        <span className="text-lg font-bold">{fps}</span>
                      </div>
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-sm font-medium">Latencia:</span>
                        <span className="text-lg font-bold">{latency}ms</span>
                      </div>
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-sm font-medium">Frames:</span>
                        <span className="text-lg font-bold">{framesReceived}</span>
                      </div>
                      {/* Indicador de color según latencia */}
                      <div className="flex items-center gap-2 mt-2">
                        <div className={`w-3 h-3 rounded-full ${
                          latency < 100 ? 'bg-green-500' : 
                          latency < 200 ? 'bg-yellow-500' : 
                          latency < 500 ? 'bg-orange-500' : 'bg-red-500'
                        }`} />
                        <span className="text-xs">
                          {latency < 100 ? 'Excelente' : 
                           latency < 200 ? 'Bueno' : 
                           latency < 500 ? 'Regular' : 'Lento'}
                        </span>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <Camera className="w-20 h-20 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">
                      {analysisId ? 'Cargando video...' : 'Sin video disponible'}
                    </p>
                    <p className="text-gray-500 text-sm mt-2">
                      {analysisId 
                        ? 'Por favor espera mientras se carga el video...' 
                        : 'Sube un video desde la página de cámaras'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="flex justify-center gap-4 mb-6">
            <button
              onClick={handleReconnect}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <RotateCcw className="w-5 h-5" />
              Reconectar
            </button>
            <button
              onClick={handlePause}
              disabled={!isPlaying}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <Pause className="w-5 h-5" />
              Pausa
            </button>
            <button
              onClick={handlePlay}
              disabled={isPlaying}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <Play className="w-5 h-5" />
              Iniciar
            </button>
          </div>

          {/* Info Panel */}
          <div className="bg-gray-900 text-white rounded-lg p-6 shadow-lg">
            {/* Camera Info - Compacto arriba */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 pb-6 border-b border-gray-700">
              <div className="flex flex-col">
                <span className="text-gray-400 text-xs mb-1">UBICACIÓN</span>
                <span className="font-mono text-sm">{location?.description || 'INSIV-001'}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-gray-400 text-xs mb-1">INICIO</span>
                <span className="font-mono text-sm">
                  {liveData.startTime || new Date().toLocaleString('es-EC', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  }).replace(',', ':')}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-gray-400 text-xs mb-1">TIEMPO</span>
                <span className="font-mono text-sm">
                  {(() => {
                    const hours = Math.floor(liveData.elapsedSeconds / 3600);
                    const minutes = Math.floor((liveData.elapsedSeconds % 3600) / 60);
                    const secs = liveData.elapsedSeconds % 60;
                    return `${hours}h${minutes}m${secs}s`;
                  })()}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-gray-400 text-xs mb-1">ELEM. CONTADO</span>
                <span className="font-mono text-sm">{liveData.vehicleCount}</span>
              </div>
            </div>

            {/* Logs en tiempo real - Panel más grande */}
            <div className="flex flex-col h-full">
              {/* Barra de progreso de carga */}
              {isLoadingModels && (
                <div className="mb-4 p-4 bg-blue-900 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-blue-200">⏳ {loadingMessage}</span>
                    <span className="text-sm font-mono text-blue-200">{loadingProgress}%</span>
                  </div>
                  <div className="w-full bg-blue-950 rounded-full h-2.5">
                    <div 
                      className="bg-blue-500 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${loadingProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-blue-300 mt-2">
                    {loadingProgress < 30 ? 'Cargando modelo YOLOv8...' : 
                     loadingProgress < 100 ? 'Cargando PaddleOCR (rápido - 5-10 seg)...' : 
                     'Listo para procesar ✓'}
                  </p>
                </div>
              )}
              
              <DetectionLogPanel detections={detections} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraLiveAnalysisPage;
