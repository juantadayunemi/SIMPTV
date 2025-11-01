import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Camera, Play, Pause, RotateCcw } from 'lucide-react';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity } from '@traffic-analysis/shared';
import { getWebSocketService, cleanupWebSocketService } from '../../services/websocket.service';
import { DetectionLogPanel } from '../../components/traffic/DetectionLogPanel';
import BoundingBoxDrawer from '../../components/traffic/BoundingBoxDrawer';
import type { RealtimeDetectionEvent } from '@traffic-analysis/shared';
import { useEffect, useRef, useState } from 'react';

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
                speed_kmh: Number(det.speed_kmh || 0),  // ✅ VELOCIDAD
                speed_category: det.speed_category || 'unknown'  // ✅ CATEGORÍA
              }));

              setDetectionBuffer(prev => ({
                ...prev,
                [timeKey]: formattedDetections
              }));
            }
          });



           // ✅ Agregar detecciones al log (solo vehículos nuevos)
          formattedDetections.forEach((det) => {
            if (!processedTrackIds.current.has(det.track_id)) {
              processedTrackIds.current.add(det.track_id);
              
              const detection: RealtimeDetectionEvent = {
                timestamp: new Date(frameData.timestamp * 1000).toISOString(),
                vehicleType: det.vehicle_type,
                plateNumber: null,
                confidence: det.confidence,
                bbox: det.bbox,
                frameNumber: frameData.frame_number || 0,
                trackId: det.track_id.toString(),
              };

              setDetections((prev) => [...prev, detection]);
              setLiveData((prev) => ({
                ...prev,
                vehicleCount: prev.vehicleCount + 1,
                lastUpdate: new Date().toLocaleTimeString(),
              }));
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
          framesReceivedCount.current++;
          lastProcessedTimestamp.current = data.timestamp;

          const timeKey = Math.round(data.timestamp * 100) / 100;

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

        // Vehículo detectado (para el log)
        const unsubVehicle = wsService.on('vehicle_detected', (data: any) => {
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
              return [...prev, detection];
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

        const unsubProgress = wsService.on('progress_update', (data: any) => {
          console.log('📊 Progreso:', data.percentage + '%');
        });
        unsubscribers.push(unsubProgress);

        const unsubComplete = wsService.on('processing_complete', (data: any) => {
          console.log('✅ Análisis completado:', data);
          setIsPlaying(false);
          setIsPaused(false);
          setShowProcessedFrames(false);
          setCurrentFrameDetections([]);
          setIsBuffering(false);
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

  // ✅ Sincronización mejorada con interpolación
  const getDetectionsForTime = (currentTime: number): Detection[] => {
    if (!detectionBuffer || Object.keys(detectionBuffer).length === 0) return [];

    const timestamps = Object.keys(detectionBuffer)
      .map(Number)
      .sort((a, b) => a - b);

    const pastTimestamps = timestamps.filter(t => t <= currentTime);
    if (pastTimestamps.length === 0) return [];

    const lastValidTimestamp = pastTimestamps[pastTimestamps.length - 1];
    const timeDifference = currentTime - lastValidTimestamp;
    
    // ✅ Aumentar tolerancia a 0.5s
    if (timeDifference > 0.5) return [];

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
        await trafficService.resumeAnalysis(analysisId);
        if (videoRef.current && videoUrl) {
          videoRef.current.play();
        }
      } else {
        setDetections([]);
        framesReceivedCount.current = 0;
        processedTrackIds.current.clear();
        hasStartedVideo.current = false;
        setLiveData(prev => ({ ...prev, vehicleCount: 0, avgSpeed: 0 }));
        setDetectionBuffer({});
        setBufferingProgress(0);
        setIsBuffering(true);

        await trafficService.startAnalysis(analysisId);
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

      <div className="p-2">
        <div className="w-full">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg sticky top-2 z-10">
                <div className="relative w-full aspect-video min-h-[70vh]">
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
              </div>

              <div className="flex justify-center gap-4">
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
            </div>

            <div className="lg:col-span-1">
              <div className="bg-gray-900 text-white rounded-lg p-6 shadow-lg sticky top-2">
                <div className="grid grid-cols-1 gap-3 mb-4 pb-4 border-b border-gray-700">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-xs">UBICACIÓN</span>
                    <span className="font-mono text-xs text-right">{location?.description || 'INSIV-001'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-xs">VEHÍCULOS</span>
                    <span className="font-mono text-xl font-bold text-green-400">{liveData.vehicleCount}</span>
                  </div>
                  {/* ✅ NUEVO: Mostrar velocidad promedio */}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-xs">VELOCIDAD AVG</span>
                    <span className="font-mono text-lg font-bold text-blue-400">{liveData.avgSpeed} km/h</span>
                  </div>
                </div>

                {showProcessedFrames && videoDuration > 0 && (
                  <div className="mb-4 p-3 bg-blue-900 rounded-lg">
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
                  <div className="mb-4 p-3 bg-purple-900 rounded-lg">
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

                <div className="h-[calc(100vh-300px)] overflow-y-auto">
                  <DetectionLogPanel detections={[...detections].reverse()} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraLiveAnalysisPage;