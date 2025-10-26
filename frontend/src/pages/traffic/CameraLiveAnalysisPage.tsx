import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Camera, Play, Pause, RotateCcw } from 'lucide-react';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity } from '@traffic-analysis/shared';
import { getWebSocketService, cleanupWebSocketService } from '../../services/websocket.service';
import { DetectionLogPanel } from '../../components/traffic/DetectionLogPanel';
import BoundingBoxDrawer from '../../components/traffic/BoundingBoxDrawer';
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

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number];
  confidence: number;
}

interface DetectionBuffer {
  [timestamp: number]: Detection[];
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
  const [thumbnailUrl, setThumbnailUrl] = useState<string>('');
  const [showProcessedFrames, setShowProcessedFrames] = useState(false);
  
  // Estado de análisis
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  // Estado de buffering
  const [isBuffering, setIsBuffering] = useState(false);
  const [bufferingProgress, setBufferingProgress] = useState(0);
  const MIN_FRAMES_TO_START = 5;
  
  // Progreso de carga (YOLOv8, PaddleOCR)
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [isLoadingModels, setIsLoadingModels] = useState<boolean>(false);
  
  // Métricas de rendimiento (FPS, latencia)
  const [fps, setFps] = useState<number>(0);
  const [latency, setLatency] = useState<number>(0);
  const [framesReceived, setFramesReceived] = useState<number>(0);
  const lastFrameTime = useRef<number>(Date.now());
  const frameTimestamps = useRef<number[]>([]);
  const hasStartedVideo = useRef<boolean>(false);

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
  const [currentFrameDetections, setCurrentFrameDetections] = useState<Detection[]>([]);
  const [detectionBuffer, setDetectionBuffer] = useState<DetectionBuffer>({});
  
  const framesReceivedCount = useRef<number>(0);
  const videoStartTime = useRef<number>(0);
  const lastProcessedTimestamp = useRef<number>(0);

  // Cargar datos de la cámara
  useEffect(() => {
    if (id) {
      loadCameraData(parseInt(id));
    }
  }, [id]);

  // Conectar WebSocket para análisis en tiempo real
  useEffect(() => {
    if (!analysisId) return;

    const wsService = getWebSocketService(analysisId);
    const unsubscribers: Array<() => void> = [];

    const connectWebSocket = async () => {
      try {
        await wsService.connect(analysisId);
        setIsConnected(true);
        console.log('✅ WebSocket conectado para análisis:', analysisId);

        // Suscribirse a frames procesados con detecciones
        const unsubFrameProcessed = wsService.on('frame_processed', (data: any) => {
          console.log('🎥 Frame procesado:', {
            frame_number: data.frame_number,
            timestamp: data.timestamp,
            detections: data.detections?.length || 0
          });

          framesReceivedCount.current++;
          lastProcessedTimestamp.current = data.timestamp;

          // Guardar en buffer con timestamp redondeado a centésimas
          const timeKey = Math.round(data.timestamp * 100) / 100;
          
          if (data.detections && Array.isArray(data.detections)) {
            const formattedDetections: Detection[] = data.detections.map((det: any) => ({
              track_id: Number(det.track_id || det.id || Math.floor(Math.random() * 1000)),
              vehicle_type: det.vehicle_type || det.class_name || 'unknown',
              bbox: det.bbox || [0, 0, 0, 0],
              confidence: Number(det.confidence || 0)
            }));

            setDetectionBuffer(prev => ({
              ...prev,
              [timeKey]: formattedDetections
            }));

            console.log(`📦 Buffer actualizado: ${Object.keys(detectionBuffer).length + 1} frames`);
          }

          // Iniciar video cuando tengamos suficiente buffer (SOLO LA PRIMERA VEZ)
          if (framesReceivedCount.current >= MIN_FRAMES_TO_START && !hasStartedVideo.current) {
             hasStartedVideo.current = true;
            console.log(`🎬 Buffer listo (${framesReceivedCount.current} frames), iniciando video...`);
            setIsBuffering(false);
            setShowProcessedFrames(true);
            
            setTimeout(() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().then(() => {
                  videoStartTime.current = Date.now();
                  console.log('▶️ Video reproduciendo normalmente');
                }).catch(err => {
                  console.error('❌ Error iniciando video:', err);
                });
              }
            }, 50);
          }

          // Actualizar progreso de buffering
          if (isBuffering) {
            const progress = Math.min(100, (framesReceivedCount.current / MIN_FRAMES_TO_START) * 100);
            setBufferingProgress(progress);
          }
        });

        unsubscribers.push(unsubFrameProcessed);

        // Suscribirse a frames con imagen (para canvas - FALLBACK)
        const unsubFrames = wsService.on('frame_update', (data: any) => {
          console.log('📸 Frame update recibido:', data.frame_number);
          
          const now = Date.now();
          const frameTime = data.timestamp ? new Date(data.timestamp).getTime() : now;
          const currentLatency = now - frameTime;
          
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
          
          // Dibujar frame en canvas (si no estamos usando video)
          if (canvasRef.current && data.frame_data && !videoUrl) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            if (ctx) {
              const img = new Image();
              img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
              };
              img.onerror = (e) => {
                console.error('❌ Error cargando imagen base64:', e);
              };
              img.src = data.frame_data;
            }
          }
        });
        unsubscribers.push(unsubFrames);

        // Suscribirse a detecciones de vehículos (para el log)
        const unsubVehicle = wsService.on('vehicle_detected', (data: any) => {
          console.log('🚗 Vehículo detectado:', data.vehicle_type, '#', data.track_id);
          
          const detection: RealtimeDetectionEvent = {
            timestamp: data.timestamp || new Date().toISOString(),
            vehicleType: data.vehicle_type || 'desconocido',
            plateNumber: data.plate_number || null,
            confidence: data.confidence || 0,
            bbox: data.bbox || null,
            frameNumber: data.frame_number || 0,
            trackId: data.track_id || '',
          };

          setDetections((prev) => {
            const exists = prev.some(d => d.trackId === detection.trackId);
            if (!exists) {
              const newDetections = [...prev, detection];
              console.log('📋 Total detecciones ahora:', newDetections.length);
              return newDetections;
            }
            return prev;
          });
          
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
          
          if (data.progress >= 100) {
            setTimeout(() => {
              setIsLoadingModels(false);
            }, 1000);
          }
        });
        unsubscribers.push(unsubLoading);

        // Suscribirse a progreso de análisis
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
          setCurrentFrameDetections([]);
          setIsBuffering(false);
        });
        unsubscribers.push(unsubComplete);

      } catch (error) {
        console.error('❌ Error connecting WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      unsubscribers.forEach(unsub => unsub());
      wsService.disconnect();
      cleanupWebSocketService(analysisId);
      setCurrentFrameDetections([]);
      setDetectionBuffer({});
      framesReceivedCount.current = 0;
    };
  }, [analysisId]);

  // Función de sincronización con interpolación
  const getDetectionsForTime = (currentTime: number): Detection[] => {
    if (!detectionBuffer || Object.keys(detectionBuffer).length === 0) return [];

    const timestamps = Object.keys(detectionBuffer)
      .map(Number)
      .sort((a, b) => a - b);

    const pastTimestamps = timestamps.filter(t => t <= currentTime);

    if (pastTimestamps.length === 0) return [];

    const lastValidTimestamp = pastTimestamps[pastTimestamps.length - 1];
    
    // Solo usar si no está muy antigua (máximo 1 segundo atrás)
    const timeDifference = currentTime - lastValidTimestamp;
    if (timeDifference > 1.0) return [];

    return detectionBuffer[lastValidTimestamp];
  };

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

  // Pausa automática al desmontar componente
  useEffect(() => {
    return () => {
      if (isPlaying && analysisId) {
        console.log('🛑 Desmontando componente - pausando análisis');
        trafficService.pauseAnalysis(analysisId).catch(console.error);
      }
    };
  }, [isPlaying, analysisId]);

  // Pausa automática al cambiar de ventana/pestaña
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && isPlaying && analysisId) {
        console.log('🛑 Ventana oculta - pausando análisis automáticamente');
        trafficService.pauseAnalysis(analysisId)
          .then(() => {
            setIsPaused(true);
            setIsPlaying(false);
            setShowProcessedFrames(false);
            setCurrentFrameDetections([]);
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

      const cameraData: CameraEntity = await trafficService.getCamera(cameraId);
      setCamera(cameraData);
      
      if (cameraData.locationId) {
        const locationData = await trafficService.getLocation(cameraData.locationId);
        setLocation(locationData);
      }

      const analysisToLoad = analysisId || cameraData.currentAnalysisId;
      
      if (analysisToLoad) {
        console.log('🔥 Cargando análisis:', analysisToLoad);
        const analysisData = await trafficService.getAnalysis(analysisToLoad.toString());
        
        if (!analysisId && cameraData.currentAnalysisId) {
          setAnalysisId(cameraData.currentAnalysisId);
        }
        
        if (analysisData.videoPath) {
          const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
          const videoUrl = `${baseUrl}/media/${analysisData.videoPath}`;
          console.log('🎥 Video URL:', videoUrl);
          setVideoUrl(videoUrl);
        }
      } else if (cameraData.currentVideoPath) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const videoUrl = `${baseUrl}/media/${cameraData.currentVideoPath}`;
        console.log('🎥 Video URL (desde cámara):', videoUrl);
        setVideoUrl(videoUrl);
      }

      // Cargar thumbnail
      if (cameraData.thumbnailPath) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const thumbUrl = `${baseUrl}/${cameraData.thumbnailPath}`;
        setThumbnailUrl(thumbUrl);
        console.log('🖼️ Thumbnail URL:', thumbUrl);
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
      setShowProcessedFrames(false);
      setCurrentFrameDetections([]);
      
      if (videoRef.current) {
        videoRef.current.pause();
      }
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
      // Resetear contadores y buffer
      framesReceivedCount.current = 0;
      setDetectionBuffer({});
      setBufferingProgress(0);
      
      if (isPaused) {
        // Reanudar
        const result = await trafficService.resumeAnalysis(analysisId);
        console.log('✅ Análisis reanudado:', result);
        
        if (videoRef.current && videoUrl) {
          videoRef.current.play();
        }
      } else {
        // Iniciar por primera vez
        setIsLoadingModels(true);
        setLoadingProgress(0);
        setLoadingMessage('Iniciando análisis...');
        
        setIsBuffering(true);
        console.log('⏳ Buffering iniciado, esperando frames...');
        
        const result = await trafficService.startAnalysis(analysisId);
        console.log('✅ Análisis iniciado:', result);
        setLiveData((prev) => ({
          ...prev,
          startTime: new Date().toLocaleTimeString(),
        }));
        
        console.log('⏳ Esperando buffer de frames antes de iniciar video...');
      }
      setIsPlaying(true);
      setIsPaused(false);
    } catch (error) {
      console.error('Error al iniciar/reanudar análisis:', error);
      setIsLoadingModels(false);
      setIsBuffering(false);
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
              <p className="text-sm text-blue-700 mt-1">
                <strong>Buffer:</strong> {Object.keys(detectionBuffer).length} frames | 
                <strong> Detecciones actuales:</strong> {currentFrameDetections.length}
              </p>
            </div>
          )}

          {/* Video Player */}
          <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg mb-6">
            <div className="relative aspect-video">
              {videoUrl ? (
                <>
                  {/* Video principal que se reproduce */}
                  <video
                    ref={videoRef}
                    src={videoUrl}
                    className={`w-full h-full object-contain ${showProcessedFrames ? 'block' : 'hidden'}`}
                    muted
                    playsInline
                    preload="auto"
                    onError={(e) => {
                      console.error('❌ Error cargando video:', e);
                    }}
                    onLoadedMetadata={() => {
                      console.log('✅ Video metadata cargada');
                    }}
                    onTimeUpdate={(e) => {
                      const currentTime = e.currentTarget.currentTime;
                      const detections = getDetectionsForTime(currentTime);
                      setCurrentFrameDetections(detections);
                    }}
                    onEnded={() => {
                      console.log('🎬 Video finalizado');
                      setCurrentFrameDetections([]);
                    }}
                  />

                  {/* Overlay de Bounding Boxes */}
                  {showProcessedFrames && currentFrameDetections.length > 0 && (
                    <BoundingBoxDrawer
                      videoRef={videoRef}
                      detections={currentFrameDetections}
                    />
                  )}
                  
                  {/* Thumbnail cuando NO está procesando */}
                  {!showProcessedFrames && !isBuffering && (
                    <div className="absolute inset-0 bg-black">
                      {thumbnailUrl ? (
                        <img
                          src={thumbnailUrl}
                          alt="Video preview"
                          className="w-full h-full object-contain"
                        />
                      ) : (
                        <video
                          src={videoUrl}
                          className="w-full h-full object-contain"
                          muted
                          preload="metadata"
                        />
                      )}
                      <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                        <div className="text-center">
                          <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center mb-4 mx-auto">
                            <Play className="w-10 h-10 text-white" />
                          </div>
                          <p className="text-white text-xl font-semibold">Video Cargado</p>
                          <p className="text-gray-300 mt-2">Presiona "Iniciar" para comenzar el análisis</p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Indicador de BUFFERING */}
                  {isBuffering && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/70 z-30">
                      <div className="text-center">
                        <div className="w-20 h-20 rounded-full border-4 border-blue-500 border-t-transparent animate-spin mb-4 mx-auto"></div>
                        <p className="text-white text-xl font-semibold">Buffering...</p>
                        <p className="text-gray-300 mt-2">
                          Esperando frames procesados ({framesReceivedCount.current}/{MIN_FRAMES_TO_START})
                        </p>
                        <div className="w-64 bg-gray-700 rounded-full h-2 mt-4 mx-auto">
                          <div 
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${bufferingProgress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Indicador de procesamiento */}
                  {showProcessedFrames && !isBuffering && (
                    <div className="absolute top-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 z-20">
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                      <span className="font-semibold">ANÁLISIS EN TIEMPO REAL</span>
                    </div>
                  )}
                  
                  {/* Contador de detecciones */}
                  {showProcessedFrames && !isBuffering && (
                    <div className="absolute bottom-3 left-3 bg-black/70 text-white px-3 py-2 rounded-lg text-sm font-mono z-20">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>{currentFrameDetections.length} vehículos</span>
                      </div>
                    </div>
                  )}

                  {/* Indicador de buffer */}
                  {showProcessedFrames && !isBuffering && (
                    <div className="absolute bottom-3 right-3 bg-black/70 text-white px-3 py-2 rounded-lg text-xs font-mono z-20">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>Buffer: {Object.keys(detectionBuffer).length} frames</span>
                      </div>
                    </div>
                  )}
                  
                  {/* Indicador de rendimiento */}
                  {showProcessedFrames && isPlaying && !isBuffering && (
                    <div className="absolute top-4 right-4 bg-black/80 text-white px-4 py-3 rounded-lg space-y-1 z-20">
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
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-sm font-medium">Detecciones:</span>
                        <span className="text-lg font-bold">{currentFrameDetections.length}</span>
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
              disabled={!isPlaying || isBuffering}
              className="flex items-center gap-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <Pause className="w-5 h-5" />
              Pausar
            </button>
            <button
              onClick={handlePlay}
              disabled={isPlaying || isBuffering}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <Play className="w-5 h-5" />
              {isBuffering ? 'Buffering...' : 'Iniciar'}
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

              {/* Barra de progreso de BUFFERING */}
              {isBuffering && (
                <div className="mb-4 p-4 bg-purple-900 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-purple-200">
                      ⏳ Cargando frames iniciales...
                    </span>
                    <span className="text-sm font-mono text-purple-200">
                      {framesReceivedCount.current}/{MIN_FRAMES_TO_START}
                    </span>
                  </div>
                  <div className="w-full bg-purple-950 rounded-full h-2.5">
                    <div 
                      className="bg-purple-500 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${bufferingProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-purple-300 mt-2">
                    El video iniciará automáticamente cuando haya suficiente buffer
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