import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Camera, Play, Pause, Settings, Link as LinkIcon } from 'lucide-react';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity, VEHICLE_TYPES } from '@traffic-analysis/shared';
import { getWebSocketService, cleanupWebSocketService } from '../../services/websocket.service';
import { DetectionLogPanel } from '../../components/traffic/DetectionLogPanel';
import BoundingBoxDrawer from '../../components/traffic/BoundingBoxDrawer';
import ConnectPathModal from '../../components/traffic/ConnectPathModal';
import type { RealtimeDetectionEvent, VehicleTypeKey } from '@traffic-analysis/shared';
import { useEffect, useRef, useState } from 'react';

// ✅ Interface para el estado de navegación
interface LocationState {
  analysisId?: number;
}

interface CameraLiveData {
  vehicleCount: number;
  avgSpeed: number;
  congestion: number;
  lastUpdate: string;
  startTime: string;
  elapsedSeconds: number;
}

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number];
  confidence: number;
  speed_kmh?: number;  // ✅ NUEVO
  speed_category?: string;  // ✅ NUEVO
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

  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const [isBuffering, setIsBuffering] = useState(false);
  const [bufferingProgress, setBufferingProgress] = useState(0);
  const MIN_FRAMES_TO_START = 5;

  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [isLoadingModels, setIsLoadingModels] = useState<boolean>(false);

  const [fps, setFps] = useState<number>(0);
  const [latency, setLatency] = useState<number>(0);
  const [framesReceived, setFramesReceived] = useState<number>(0);
  const lastFrameTime = useRef<number>(Date.now());
  const frameTimestamps = useRef<number[]>([]);
  const hasStartedVideo = useRef<boolean>(false);

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
  const [videoDuration, setVideoDuration] = useState<number>(0);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [videoProgress, setVideoProgress] = useState<number>(0);

  const framesReceivedCount = useRef<number>(0);
  const videoStartTime = useRef<number>(0);
  const lastProcessedTimestamp = useRef<number>(0);
  const processedTrackIds = useRef<Set<number>>(new Set());

  const [playbackRate, setPlaybackRate] = useState<number>(1);
  const [showSpeedMenu, setShowSpeedMenu] = useState<boolean>(false);
  const [showReconnectModal, setShowReconnectModal] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      loadCameraData(parseInt(id));
    }
  }, [id]);

  useEffect(() => {
    if (!analysisId) return;

    const wsService = getWebSocketService(analysisId);
    const unsubscribers: Array<() => void> = [];

    const connectWebSocket = async () => {
      try {
        framesReceivedCount.current = 0;
        await wsService.connect(analysisId);
        setIsConnected(true);
        console.log('✅ WebSocket conectado:', analysisId);

        
        // ✅ NUEVO: Procesar batch de frames
        const unsubFramesBatch = wsService.on('frames_batch', (data: any) => {

          if (!data.frames || !Array.isArray(data.frames)) return;
          
          console.log(`📦 Batch recibido: ${data.frames.length} frames`);
          
          data.frames.forEach((frameData: any) => {
            framesReceivedCount.current++;
            lastProcessedTimestamp.current = frameData.timestamp;

            const timeKey = Math.round(frameData.timestamp * 100) / 100;

            if (frameData.detections && Array.isArray(frameData.detections)) {
              const formattedDetections: Detection[] = frameData.detections.map((det: any) => ({
                track_id: Number(det.track_id || Math.floor(Math.random() * 1000)),
                vehicle_type: det.vehicle_type || 'unknown',
                bbox: det.bbox || [0, 0, 0, 0],
                confidence: Number(det.confidence || 0),
                speed_kmh: Number(det.speed_kmh || 0),
                speed_category: det.speed_category || 'unknown'
              }));

              setDetectionBuffer(prev => ({
                ...prev,
                [timeKey]: formattedDetections
              }));

              // 🚫 NO agregar a la lista aquí - se agregará cuando aparezca en el video
            }
          });

          // Iniciar video cuando tengamos suficiente buffer
          if (framesReceivedCount.current >= MIN_FRAMES_TO_START && !hasStartedVideo.current) {
            hasStartedVideo.current = true;
            console.log(`🎬 Buffer listo (${framesReceivedCount.current} frames)`);
            setIsBuffering(false);
            setShowProcessedFrames(true);

            setTimeout(() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().catch(err => {
                  console.error('❌ Error iniciando video:', err);
                });
              }
            }, 50);
          }

          if (isBuffering) {
            const progress = Math.min(100, (framesReceivedCount.current / MIN_FRAMES_TO_START) * 100);
            setBufferingProgress(progress);
          }
        });
        unsubscribers.push(unsubFramesBatch);

        // ✅ Mantener frame_processed para compatibilidad
        const unsubFrameProcessed = wsService.on('frame_processed', (data: any) => {
          console.log(`🎯 [FRAME_PROCESSED] Datos recibidos:`, data);
          console.log(`🎯 [FRAME_PROCESSED] Tipo de data:`, typeof data);
          console.log(`🎯 [FRAME_PROCESSED] Keys:`, Object.keys(data));
          
          framesReceivedCount.current++;
          lastProcessedTimestamp.current = data.timestamp;

          const timeKey = Math.round(data.timestamp * 100) / 100;

          console.log(`🔑 [BUFFER] Guardando en timeKey: ${timeKey} | Timestamp original: ${data.timestamp}`);

          if (data.detections && Array.isArray(data.detections)) {
            const formattedDetections: Detection[] = data.detections.map((det: any) => ({
              track_id: Number(det.track_id || Math.floor(Math.random() * 1000)),
              vehicle_type: det.vehicle_type || 'unknown',
              bbox: det.bbox || [0, 0, 0, 0],
              confidence: Number(det.confidence || 0),
              speed_kmh: Number(det.speed_kmh || 0),
              speed_category: det.speed_category || 'unknown'
            }));

            setDetectionBuffer(prev => ({
              ...prev,
              [timeKey]: formattedDetections
            }));

            // 🚫 NO agregar a la lista aquí - se agregará cuando aparezca en el video
          }

          if (framesReceivedCount.current >= MIN_FRAMES_TO_START && !hasStartedVideo.current) {
            hasStartedVideo.current = true;
            setIsBuffering(false);
            setShowProcessedFrames(true);

            setTimeout(() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().catch(console.error);
              }
            }, 50);
          }

          if (isBuffering) {
            const progress = Math.min(100, (framesReceivedCount.current / MIN_FRAMES_TO_START) * 100);
            setBufferingProgress(progress);
          }
        });
        unsubscribers.push(unsubFrameProcessed);

        // 🚫 EVENTO ELIMINADO: vehicle_detected (ya procesamos detecciones desde frame_processed)

        // ✅ Evento: Progreso del análisis
        const unsubProgress = wsService.on('progress_update', (data: any) => {
          console.log('📊 Progreso:', data.progress + '%', data);
          
          // ✅ Iniciar video en el primer progress_update si no ha iniciado
          if (!hasStartedVideo.current && videoRef.current) {
            hasStartedVideo.current = true;
            console.log('🎬 Iniciando video automáticamente con primer progress_update');
            setIsBuffering(false);
            setShowProcessedFrames(true);
            
            setTimeout(() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().catch(err => {
                  console.error('❌ Error iniciando video:', err);
                });
              }
            }, 100);
          }
          
          // ✅ Actualizar vehicleCount desde el backend (total real detectado)
          // El contador mostrará el total de vehículos guardados en BD (ej: 296)
          // La lista solo muestra los visibles en el video
          
          setLiveData((prev) => ({
            ...prev,
            // ✅ NO actualizar vehicleCount aquí - se cuenta localmente desde la lista
            // vehicleCount: data.vehicles_detected || 0,
            congestion: Math.min(100, Math.round(((data.vehicles_detected || 0) / 100) * 100)),
            lastUpdate: new Date().toLocaleTimeString(),
          }));
        });
        unsubscribers.push(unsubProgress);

        // ✅ Evento: Notificación de denuncia (para campana)
        const unsubNotificationBadge = wsService.on('notification_badge', (data: {
          plate_number: string;
          complaints_count: number;
          timestamp: string;
        }) => {
          console.log(`🔔 [NOTIFICACIÓN] Denuncia detectada: ${data.plate_number} (${data.complaints_count} denuncias)`);
          
          // Disparar evento personalizado para el Header
          window.dispatchEvent(new CustomEvent('newNotification', {
            detail: {
              plate: data.plate_number,
              count: data.complaints_count,
              timestamp: data.timestamp
            }
          }));
        });
        unsubscribers.push(unsubNotificationBadge);

        const unsubComplete = wsService.on('processing_complete', (data: any) => {
          console.log('✅ Análisis completado por el backend:', data);
          console.log(`📊 Total vehículos detectados: ${data.total_vehicles}`);
          console.log(`⏱️ Tiempo de procesamiento: ${data.processing_time}s`);
          console.log(`🚗 Desglose: ${JSON.stringify(data.vehicle_breakdown)}`);
          
          // ✅ NO detener la reproducción - Los datos ya están en el buffer
          // El video seguirá reproduciéndose y mostrando las detecciones almacenadas
          // Solo marcamos que el análisis backend terminó
          console.log('ℹ️ El video continuará mostrando las detecciones ya procesadas');
        });
        unsubscribers.push(unsubComplete);

      } catch (error) {
        console.error('❌ Error WebSocket:', error);
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

  // ✅ Sincronización mejorada con interpolación y persistencia
  const getDetectionsForTime = (currentTime: number): Detection[] => {
    if (!detectionBuffer || Object.keys(detectionBuffer).length === 0) return [];

    const timestamps = Object.keys(detectionBuffer)
      .map(Number)
      .sort((a, b) => a - b);

    // Buscar el timestamp más cercano (anterior o igual)
    const pastTimestamps = timestamps.filter(t => t <= currentTime);
    if (pastTimestamps.length === 0) {
      // Si no hay timestamps pasados, buscar el siguiente más cercano
      const futureTimestamps = timestamps.filter(t => t > currentTime);
      if (futureTimestamps.length > 0) {
        const nextTimestamp = futureTimestamps[0];
        const timeDifference = nextTimestamp - currentTime;
        // Si el siguiente frame está muy cerca (< 1s), mostrarlo
        if (timeDifference < 1.0) {
          return detectionBuffer[nextTimestamp];
        }
      }
      return [];
    }

    const lastValidTimestamp = pastTimestamps[pastTimestamps.length - 1];
    const timeDifference = currentTime - lastValidTimestamp;
    
    // Aumentar tolerancia a 2s para velocidades lentas (0.25x, 0.5x)
    // Esto permite que las detecciones persistan más tiempo en pantalla
    if (timeDifference > 1.0) return [];

    return detectionBuffer[lastValidTimestamp];
  };

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

  useEffect(() => {
    return () => {
      if (isPlaying && analysisId) {
        trafficService.pauseAnalysis(analysisId).catch(console.error);
      }
    };
  }, [isPlaying, analysisId]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && isPlaying && analysisId) {
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

  // ✅ Actualización optimizada de detecciones
  useEffect(() => {
    if (!isPlaying || !videoRef.current) return;

    let animationFrameId: number;

    const updateDetections = () => {
      if (videoRef.current) {
        const time = videoRef.current.currentTime;
        const detections = getDetectionsForTime(time);
        setCurrentFrameDetections(detections);
        
        // 🆕 AGREGAR VEHÍCULOS A LA LISTA CUANDO APARECEN EN EL VIDEO
        // Solo agregar si el track_id es NUEVO (no importa el orden de llegada)
        detections.forEach((det) => {
          if (!processedTrackIds.current.has(det.track_id)) {
            processedTrackIds.current.add(det.track_id);
            
            // Mapear vehicle_type a VehicleTypeKey válido
            const vehicleTypeMap: Record<string, VehicleTypeKey> = {
              'car': VEHICLE_TYPES.CAR,
              'truck': VEHICLE_TYPES.TRUCK,
              'motorcycle': VEHICLE_TYPES.MOTORCYCLE,
              'bus': VEHICLE_TYPES.BUS,
              'bicycle': VEHICLE_TYPES.BICYCLE,
            };
            
            const vehicleType = vehicleTypeMap[det.vehicle_type.toLowerCase()] || VEHICLE_TYPES.CAR;
            
            const detection: RealtimeDetectionEvent = {
              timestamp: new Date(),
              vehicleType: vehicleType,
              plateNumber: undefined,
              confidence: det.confidence,
              bbox: {
                x: det.bbox[0],
                y: det.bbox[1],
                width: det.bbox[2],
                height: det.bbox[3],
              },
              frameNumber: 0,
              trackId: det.track_id.toString(),
            };

            // ✅ Agregar a la lista para mostrar en DetectionLogPanel
            setDetections((prev) => [...prev, detection]);
            
            // ✅ Actualizar contador local con la cantidad de vehículos en la lista
            setLiveData((prev) => ({
              ...prev,
              vehicleCount: processedTrackIds.current.size,
              lastUpdate: new Date().toLocaleTimeString(),
            }));
            
            console.log(`🚗 Nuevo vehículo agregado al log: ${det.vehicle_type} (track_id: ${det.track_id}) @ ${time.toFixed(2)}s`);
          }
        });
        
        // ✅ Calcular velocidad promedio
        if (detections.length > 0) {
          const speeds = detections
            .map(d => d.speed_kmh || 0)
            .filter(s => s > 0);
          
          if (speeds.length > 0) {
            const avgSpeed = speeds.reduce((a, b) => a + b, 0) / speeds.length;
            setLiveData(prev => ({
              ...prev,
              avgSpeed: Math.round(avgSpeed)
            }));
          }
        }
      }
      animationFrameId = requestAnimationFrame(updateDetections);
    };

    animationFrameId = requestAnimationFrame(updateDetections);

    return () => cancelAnimationFrame(animationFrameId);
  }, [isPlaying, videoDuration, detectionBuffer]);


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
        const analysisData = await trafficService.getAnalysis(analysisToLoad.toString());

        if (!analysisId && cameraData.currentAnalysisId) {
          setAnalysisId(cameraData.currentAnalysisId);
        }

        if (analysisData.videoPath) {
          const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
          const videoUrl = `${baseUrl}/media/${analysisData.videoPath}`;
          setVideoUrl(videoUrl);
        }
      } else if (cameraData.currentVideoPath) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const videoUrl = `${baseUrl}/media/${cameraData.currentVideoPath}`;
        setVideoUrl(videoUrl);
      }

      if (cameraData.thumbnailPath) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const thumbUrl = `${baseUrl}/${cameraData.thumbnailPath}`;
        setThumbnailUrl(thumbUrl);
      }

    } catch (error) {
      console.error('Error loading camera:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReconnect = async () => {
    if (!analysisId) return;

    try {
      const wsService = getWebSocketService(analysisId);
      await wsService.connect(analysisId);
      setIsConnected(true);
    } catch (error) {
      console.error('Error al reconectar:', error);
      setIsConnected(false);
    }
  };

  // ✅ NUEVO: Manejar reconexión desde modal (igual que CamerasPage)
  const handleReconnectFromModal = async (videoFile: File, newAnalysisId: number) => {
    console.log('🔗 Reconectando video:', { videoFile: videoFile.name, newAnalysisId });

    try {
      // 1. Limpiar estado anterior
      setDetections([]);
      framesReceivedCount.current = 0;
      processedTrackIds.current.clear();
      hasStartedVideo.current = false;
      setLiveData(prev => ({ ...prev, vehicleCount: 0, avgSpeed: 0 }));
      setDetectionBuffer({});
      setBufferingProgress(0);
      setCurrentFrameDetections([]);

      // 2. Crear URL local del video subido (NO del backend)
      const localVideoUrl = URL.createObjectURL(videoFile);
      setVideoUrl(localVideoUrl);

      // 3. Establecer nuevo analysisId
      setAnalysisId(newAnalysisId);

      // 4. Activar buffering
      setIsBuffering(true);

      // 5. WebSocket se conectará automáticamente por el useEffect[analysisId]
      // Los datos llegarán por frame_processed y se almacenarán en detectionBuffer
      // Cuando haya suficientes frames, auto-iniciará el video

      console.log('✅ Video local configurado — esperando frames del backend');

    } catch (error) {
      console.error('❌ Error al reconectar video:', error);
      alert('Error al reconectar el video');
    }
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackRate(speed);
    if (videoRef.current) {
      videoRef.current.playbackRate = speed;
    }
    setShowSpeedMenu(false);
  };

  const handlePause = async () => {
    if (!analysisId) return;

    try {
      await trafficService.pauseAnalysis(analysisId);
      setIsPaused(true);
      setIsPlaying(false);
      setShowProcessedFrames(false);
      setCurrentFrameDetections([]);

      if (videoRef.current) {
        videoRef.current.pause();
      }
    } catch (error) {
      console.error('Error al pausar:', error);
    }
  };

  const handlePlay = async () => {
    if (!analysisId) return;

    try {
      if (isPaused) {
        // ✅ Si está en pausa, simplemente reanudar
        await trafficService.resumeAnalysis(analysisId);
        if (videoRef.current && videoUrl) {
          videoRef.current.play();
        }
      } else {
        // ✅ Si NO está en pausa, clonar el análisis (crear nuevo con mismos datos)
        console.log(`🔄 Clonando análisis ${analysisId}...`);
        
        setDetections([]);
        framesReceivedCount.current = 0;
        processedTrackIds.current.clear();
        hasStartedVideo.current = false;
        setLiveData(prev => ({ ...prev, vehicleCount: 0, avgSpeed: 0 }));
        setDetectionBuffer({});
        setBufferingProgress(0);
        setIsBuffering(true);

        // Clonar el análisis existente
        const cloneResponse = await trafficService.cloneAnalysis(analysisId);
        const newAnalysisId = cloneResponse.new_analysis_id;
        
        console.log(`✅ Nuevo análisis clonado: ${newAnalysisId} (original: ${analysisId})`);
        
        // Actualizar el analysisId al nuevo
        setAnalysisId(newAnalysisId);
        
        // Iniciar el nuevo análisis
        await trafficService.startAnalysis(newAnalysisId);
        
        setLiveData((prev) => ({
          ...prev,
          startTime: new Date().toLocaleTimeString(),
        }));
      }
      setIsPlaying(true);
      setIsPaused(false);
    } catch (error) {
      console.error('Error al iniciar:', error);
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
            onClick={() => navigate('/home')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[85vh] bg-gray-50 flex flex-col overflow-hidden">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/home')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h4 className="text-xl font-bold text-gray-900">
                {camera.name} - En Línea
              </h4>
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

      {/* Main content - 2 columnas */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full grid grid-cols-1 lg:grid-cols-3">
          {/* Columna izquierda: Video + Controles */}
          <div className="lg:col-span-2 flex flex-col">
            {/* Video container */}
            <div className="flex-1 bg-gray-900 relative overflow-hidden">
              {videoUrl ? (
                    <>
                      <video
                                
                        ref={videoRef}
                        src={videoUrl}

                        
                        className={`w-full h-full object-cover ${showProcessedFrames ? 'block' : 'hidden'}`}
                        muted
                        playsInline
                        preload="auto"
                        onLoadedMetadata={() => {
                          if (videoRef.current) {
                            setVideoDuration(videoRef.current.duration);
                            videoRef.current.playbackRate = playbackRate;
                          }
                        }}
                        onTimeUpdate={(e) => {
                          setCurrentTime(e.currentTarget.currentTime);
                          setVideoProgress((e.currentTarget.currentTime / videoDuration) * 100);
                        }}
                      />

                      {showProcessedFrames && currentFrameDetections.length > 0 && (
                        <BoundingBoxDrawer
                          videoRef={videoRef}
                          detections={currentFrameDetections}
                        />
                      )}

                      {!showProcessedFrames && !isBuffering && (
                        <div className="absolute inset-0 bg-black">
                          {thumbnailUrl ? (
                            <img
                              src={thumbnailUrl}
                              alt="Video preview"
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <video
                              src={videoUrl}
                              className="w-full h-full object-cover"
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
                              <p className="text-gray-300 mt-2">Presiona "Iniciar"</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {isBuffering && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/70 z-30">
                          <div className="text-center">
                            <div className="w-20 h-20 rounded-full border-4 border-blue-500 border-t-transparent animate-spin mb-4 mx-auto"></div>
                            <p className="text-white text-xl font-semibold">Buffering...</p>
                            <p className="text-gray-300 mt-2">
                              Esperando frames ({framesReceivedCount.current}/{MIN_FRAMES_TO_START})
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

                      {showProcessedFrames && !isBuffering && (
                        <div className="absolute top-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 z-20">
                          <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                          <span className="font-semibold">ANÁLISIS EN TIEMPO REAL</span>
                        </div>
                      )}

                      {/* ✅ NUEVO: Mostrar velocidades */}
                      {showProcessedFrames && !isBuffering && (
                        <div className="absolute bottom-3 left-3 bg-black/80 text-white px-4 py-3 rounded-lg space-y-1 z-20">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            <span className="text-sm font-semibold">{currentFrameDetections.length} vehículos</span>
                          </div>
                          {currentFrameDetections.some(d => (d.speed_kmh || 0) > 0) && (
                            <div className="text-xs space-y-1 mt-2 border-t border-white/30 pt-2">
                              {currentFrameDetections
                                .filter(d => (d.speed_kmh || 0) > 0)
                                .slice(0, 3)
                                .map(d => (
                                  <div key={d.track_id} className="flex items-center justify-between gap-3">
                                    <span className="text-gray-300">#{d.track_id}</span>
                                    <span className={`font-bold ${
                                      d.speed_category === 'slow' ? 'text-green-400' :
                                      d.speed_category === 'medium' ? 'text-yellow-400' :
                                      d.speed_category === 'fast' ? 'text-orange-400' :
                                      'text-red-400'
                                    }`}>
                                      {d.speed_kmh?.toFixed(1)} km/h
                                    </span>
                                  </div>
                                ))}
                            </div>
                          )}
                        </div>
                      )}

                      {showProcessedFrames && !isBuffering && (
                        <div className="absolute bottom-3 right-3 bg-black/70 text-white px-3 py-2 rounded-lg text-xs font-mono z-20">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            <span>Buffer: {Object.keys(detectionBuffer).length} frames</span>
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
                      </div>
                    </div>
                  )}
            </div>

            {/* Controles - Footer fijo */}
            <div className="bg-gray-800 px-4 py-3 flex justify-center gap-3 flex-shrink-0">
              {/* Control de velocidad */}
              <div className="relative">
                <button
                  onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                  className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors text-sm"
                >
                  <Settings className="w-4 h-4" />
                  {playbackRate}x
                </button>
                
                {showSpeedMenu && (
                  <div className="absolute bottom-full mb-2 left-0 bg-gray-800 border border-gray-700 rounded-lg shadow-lg py-2 w-32">
                    {[0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2].map((speed) => (
                      <button
                        key={speed}
                        onClick={() => handleSpeedChange(speed)}
                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-700 transition-colors ${
                          playbackRate === speed ? 'bg-blue-600 text-white' : 'text-gray-300'
                        }`}
                      >
                        {speed === 1 ? 'Normal' : `${speed}x`}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={() => setShowReconnectModal(true)}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
                title="Reconectar con nuevo video"
              >
                <LinkIcon className="w-4 h-4" />
                Reconectar
              </button>

              <button
                onClick={handlePause}
                disabled={!isPlaying || isBuffering}
                className="flex items-center gap-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors text-sm"
              >
                <Pause className="w-4 h-4" />
                Pausar
              </button>
              <button
                onClick={handlePlay}
                disabled={isPlaying || isBuffering}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors text-sm"
              >
                <Play className="w-4 h-4" />
                {isBuffering ? 'Buffering...' : 'Iniciar'}
              </button>
            </div>
          </div>

          {/* Columna derecha: Panel de detecciones */}
          <div className="lg:col-span-1 flex flex-col bg-gray-900 text-white overflow-hidden">
            {/* Stats header */}
            <div className="p-4 border-b border-gray-700 flex-shrink-0">
              <div className="grid grid-cols-1 gap-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">UBICACIÓN</span>
                  <span className="font-mono text-xs text-right">{location?.description || 'INSIV-001'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">VEHÍCULOS</span>
                  <span className="font-mono text-xl font-bold text-green-400">{liveData.vehicleCount}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">VELOCIDAD AVG</span>
                  <span className="font-mono text-lg font-bold text-blue-400">{liveData.avgSpeed} km/h</span>
                </div>
              </div>

              {showProcessedFrames && videoDuration > 0 && (
                <div className="mt-4 p-3 bg-blue-900 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-blue-200">▶️ Reproducción</span>
                    <span className="text-xs font-mono text-blue-200">
                      {Math.floor(currentTime)}s / {Math.floor(videoDuration)}s
                    </span>
                  </div>
                  <div className="w-full bg-blue-950 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${videoProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {isBuffering && framesReceivedCount.current <= MIN_FRAMES_TO_START && (
                <div className="mt-4 p-3 bg-purple-900 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-purple-200">⏳ Buffering</span>
                    <span className="text-xs font-mono text-purple-200">
                      {framesReceivedCount.current}/{MIN_FRAMES_TO_START}
                    </span>
                  </div>
                  <div className="w-full bg-purple-950 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${bufferingProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* Lista de detecciones con scroll */}
            <div className="flex-1 overflow-y-auto">
              <DetectionLogPanel detections={[...detections].reverse()} />
            </div>
          </div>
        </div>
      </div>

      {/* ✅ Modal de Reconexión usando ConnectPathModal */}
      {camera && (
        <ConnectPathModal
          isOpen={showReconnectModal}
          onClose={() => setShowReconnectModal(false)}
          cameraName={camera.name}
          cameraId={camera.id}
          locationId={camera.locationId}
          userId={1}
          onPlay={handleReconnectFromModal}
          mode="connect"
        />
      )}
    </div>
  );
};

export default CameraLiveAnalysisPage;