/**
 * LiveMonitoring Page
 * Real-time camera monitoring with YOLO detection and AWS S3 recording
 */
import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  Play, 
  Camera, 
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  HardDrive
} from 'lucide-react';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity, FrameData } from '@traffic-analysis/shared';
import * as streamingService from '../../services/streamingService';
import { toast } from 'react-hot-toast';

// Tipo para cámaras físicas del dispositivo
interface PhysicalCamera {
  deviceId: string;
  label: string;
  kind: string;
}

export const LiveMonitoring = () => {
  const [searchParams] = useSearchParams();
  
  // State
  const [physicalCameras, setPhysicalCameras] = useState<PhysicalCamera[]>([]);
  const [selectedPhysicalCamera, setSelectedPhysicalCamera] = useState<PhysicalCamera | null>(null);
  const [selectedDbCamera, setSelectedDbCamera] = useState<CameraEntity | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Refs for video and canvas
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processingIntervalRef = useRef<number | null>(null);
  
  // Detections state
  const [currentDetections, setCurrentDetections] = useState<any[]>([]);
  
  // NEW: Tracking statistics
  const [uniqueVehicles, setUniqueVehicles] = useState<Set<number>>(new Set());
  const [totalFramesProcessed, setTotalFramesProcessed] = useState(0);
  const [totalDetections, setTotalDetections] = useState(0);
  
  // Detection session management (for JSON export)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  // Statistics
  const [streamStats, setStreamStats] = useState({
    frameCount: 0,
    detectionCount: 0,
    elapsedTime: 0,
    recordingId: null
  });

  // NUEVO: Estados para cronómetro y timestamp
  const [elapsedTime, setElapsedTime] = useState(0); // en segundos
  const [startTimestamp, setStartTimestamp] = useState<string>('');
  const streamingStartTimeRef = useRef<number | null>(null);

  // Load physical cameras on mount
  useEffect(() => {
    loadPhysicalCameras();
    loadDbCameraFromUrl();
    
    // Cleanup on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      // Limpiar intervalo de cámara IP
      if (ipCameraIntervalRef.current) {
        clearInterval(ipCameraIntervalRef.current);
      }
    };
  }, []);

  // Nuevo: Ref para el intervalo de la cámara IP
  const ipCameraIntervalRef = useRef<number | null>(null);

  // NUEVO: Cronómetro de streaming en tiempo real
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isStreaming && streamingStartTimeRef.current) {
      interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - streamingStartTimeRef.current!) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    } else {
      // Reset cuando no está streaming
      setElapsedTime(0);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStreaming]);

  // Attach stream to video element when streaming starts
  useEffect(() => {
    const attachStream = async () => {
      if (isStreaming && streamRef.current && videoRef.current) {
        console.log('� Adjuntando stream en useEffect...');
        videoRef.current.srcObject = streamRef.current;
        
        try {
          await videoRef.current.play();
          console.log('▶️ Video reproduciendo desde useEffect');
          
          // Log state after playing
          setTimeout(() => {
            if (videoRef.current) {
              console.log('Estado del video element:');
              console.log('  - srcObject:', videoRef.current.srcObject);
              console.log('  - readyState:', videoRef.current.readyState);
              console.log('  - paused:', videoRef.current.paused);
              console.log('  - videoWidth:', videoRef.current.videoWidth);
              console.log('  - videoHeight:', videoRef.current.videoHeight);
              
              // Start frame processing after video is ready
              startFrameProcessing();
            }
          }, 1000);
        } catch (err) {
          console.error('Error al reproducir en useEffect:', err);
        }
      }
    };
    
    attachStream();
    
    // Cleanup when streaming stops
    return () => {
      stopFrameProcessing();
    };
  }, [isStreaming]);

  // Load physical cameras from device
  const loadPhysicalCameras = async () => {
    try {
      setLoading(true);
      
      // Request permission first
      const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
      
      // Stop the temporary stream immediately
      tempStream.getTracks().forEach(track => track.stop());
      
      // Now enumerate devices with permissions granted
      const devices = await navigator.mediaDevices.enumerateDevices();
      
      // Filter video input devices (TODAS las cámaras USB, incluyendo DroidCam)
      const videoDevices = devices
        .filter(device => device.kind === 'videoinput')
        .map((device, index) => ({
          deviceId: device.deviceId,
          label: device.label || `Cámara ${index + 1}`,
          kind: device.kind,
          isIPCamera: false
        }));
      
      console.log('📹 Cámaras detectadas:', videoDevices);
      setPhysicalCameras(videoDevices);
      
      // NO auto-seleccionar ninguna cámara
      // El usuario debe seleccionar manualmente
    } catch (err: any) {
      console.error('Error accessing cameras:', err);
      setError('No se pudo acceder a las cámaras del dispositivo. Por favor, da permisos de cámara.');
    } finally {
      setLoading(false);
    }
  };

  // Load database camera info from URL (for location display)
  const loadDbCameraFromUrl = async () => {
    const cameraIdFromUrl = searchParams.get('cameraId');
    
    if (cameraIdFromUrl) {
      try {
        const camerasData = await trafficService.getCameras();
        const camera = camerasData.find(c => c.id.toString() === cameraIdFromUrl);
        if (camera) {
          setSelectedDbCamera(camera);
        }
      } catch (err) {
        console.error('Error loading camera info:', err);
      }
    }
  };

  // NUEVO: Handler para confirmar la configuración de IP
  // Handler para cuando se selecciona una cámara
  const handleCameraSelect = (camera: PhysicalCamera) => {
    console.log('📹 Cámara seleccionada:', camera.label);
    setSelectedPhysicalCamera(camera);
  };

  // Frame processing functions
  const captureAndProcessFrame = async () => {
    if (!videoRef.current || !canvasRef.current) {
      console.log('Video or canvas ref not available');
      return;
    }
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.log('Video not ready, readyState:', video.readyState);
      return;
    }
    
    console.log('Capturing frame...', {
      videoWidth: video.videoWidth,
      videoHeight: video.videoHeight,
      readyState: video.readyState
    });
    
    // Set canvas size to match video DIMENSIONS (not display size)
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current video frame to canvas for sending to backend
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    
    if (!tempCtx) {
      console.error('Could not get 2D context from temporary canvas');
      return;
    }
    
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    
    // Convert canvas to base64
    const frameData = tempCanvas.toDataURL('image/jpeg', 0.8);
    console.log('Frame converted to base64, size:', frameData.length);
    
    try {
      console.log('Sending frame to backend...');
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      
      if (!token) {
        console.error('No authentication token');
        setError('No hay token de autenticación. Por favor, inicia sesión.');
        return;
      }
      
      console.log('🔑 Token encontrado:', token.substring(0, 20) + '...');
      
      // Send to backend for YOLO processing (Daphne port 8001)
      const response = await fetch('http://localhost:8001/api/streaming/process-frame/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          frame: frameData
        })
      });
      
      console.log('Backend response:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', errorText);
        throw new Error(`Backend error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Data received:', data);
      
      if (data.success) {
        console.log(`Detections: ${data.detections?.length || 0}`);
        
        // Update tracking statistics from backend
        if (data.stats) {
          setTotalFramesProcessed(data.stats.frames_processed || 0);
          setTotalDetections(data.stats.detection_count || 0);
          
          // Update unique vehicles set
          if (data.stats.unique_vehicles !== undefined) {
            console.log(`Total unique vehicles: ${data.stats.unique_vehicles}`);
          }
        }
        
        // Update local unique vehicles from current detections
        if (data.detections && data.detections.length > 0) {
          const newUniqueVehicles = new Set(uniqueVehicles);
          data.detections.forEach((det: any) => {
            if (det.id !== undefined) {
              newUniqueVehicles.add(det.id);
            }
          });
          setUniqueVehicles(newUniqueVehicles);
        }
        
        // Update detections and draw immediately
        setCurrentDetections(data.detections || []);
        
        // Draw detections on overlay canvas
        drawDetectionsOverlay(data.detections || []);
        
        // Save detections when session is active (not only when recording)
        if (currentSessionId && data.detections && data.detections.length > 0) {
          // Save all detections in parallel (non-blocking)
          data.detections.forEach((detection: any) => {
            streamingService.saveDetection(
              selectedPhysicalCamera?.deviceId || 'webcam-default',
              currentSessionId,
              {
                vehicle_type: detection.label,
                plate_number: detection.plate || 'UNREADABLE',
                confidence: detection.confidence || 0.0,
                detection_method: 'live',
                frame_base64: frameData,
                bbox: detection.bbox,
                timestamp: new Date().toISOString()
              }
            ).then(() => {
              console.log(`Detection saved: ${detection.label}`);
            }).catch((saveError: any) => {
              console.error('Error saving detection:', saveError);
            });
          });
        }
        
        // Update stats
        setStreamStats(prev => ({
          ...prev,
          frameCount: prev.frameCount + 1,
          detectionCount: prev.detectionCount + (data.detections?.length || 0)
        }));
      } else {
        console.error('Backend reported error:', data.error);
        setError(data.error);
      }
    } catch (error) {
      console.error('Error processing frame:', error);
      // No mostramos error en UI para no interrumpir el stream
    }
  };
  
  const drawDetectionsOverlay = (detections: any[]) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw each detection
    detections.forEach((detection) => {
      // bbox format from backend: [x, y, width, height]
      const [x, y, width, height] = detection.bbox;
      const x1 = x;
      const y1 = y;
      const x2 = x + width;
      const y2 = y + height;
      
      // Color consistente basado en el ID (el backend ya envía colores, pero podemos usar el ID)
      let color = '#00FF00'; // Verde por defecto
      
      // Si hay ID, usar color basado en ID para consistencia
      if (detection.id !== undefined) {
        const colors = [
          '#00FF00',  // Verde
          '#FF0000',  // Rojo
          '#0000FF',  // Azul
          '#FFFF00',  // Amarillo
          '#FF00FF',  // Magenta
          '#00FFFF',  // Cyan
          '#FF8000',  // Naranja
          '#8000FF',  // Púrpura
          '#FFC0CB',  // Rosa
          '#008000',  // Verde oscuro
        ];
        color = colors[detection.id % colors.length];
      } else {
        // Fallback: color por tipo de vehículo
        switch(detection.label) {
          case 'car': color = '#00FF00'; break;
          case 'truck': color = '#FF0000'; break;
          case 'motorcycle': color = '#0000FF'; break;
          case 'bus': color = '#FFFF00'; break;
          case 'bicycle': color = '#FF00FF'; break;
        }
      }
      
      // Draw bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, width, height);
      
      // Draw label with ID
      let label = '';
      if (detection.id !== undefined) {
        // Nuevo formato: "ID#1 - car (95%)"
        const confidence = detection.confidence !== undefined 
          ? `${(detection.confidence * 100).toFixed(0)}%` 
          : '';
        label = `ID#${detection.id} - ${detection.label} ${confidence}`;
        
        // Agregar edad del tracking si está disponible
        if (detection.age !== undefined) {
          label += ` [${detection.age}f]`;
        }
      } else {
        // Formato antiguo sin ID
        label = `${detection.label} ${(detection.confidence * 100).toFixed(0)}%`;
      }
      
      ctx.font = 'bold 16px Arial';
      const textMetrics = ctx.measureText(label);
      const textWidth = textMetrics.width;
      
      ctx.fillStyle = color;
      ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
      
      // Draw label text
      ctx.fillStyle = '#000000'; // Texto negro para mejor contraste
      ctx.fillText(label, x1 + 5, y1 - 7);
    });
  };
  
  const startFrameProcessing = () => {
    console.log('Starting frame processing...');
    
    // Process frames every 500ms (~2 FPS) - Balance between continuous detection and performance
    // Increased from 300ms to 500ms to process each frame completely
    processingIntervalRef.current = window.setInterval(() => {
      captureAndProcessFrame();
    }, 500);
  };
  
  const stopFrameProcessing = () => {
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
      processingIntervalRef.current = null;
      console.log('Frame processing stopped');
    }
  };

  const handleStartStream = async () => {
    if (!selectedPhysicalCamera) {
      alert('Por favor seleccione una cámara');
      return;
    }

    try {
      setError(null);
      console.log('🎥 Iniciando stream con cámara:', selectedPhysicalCamera);
      
      // Todas las cámaras son USB (incluyendo DroidCam via USB)
      const constraints: MediaStreamConstraints = {
        video: {
          deviceId: { exact: selectedPhysicalCamera.deviceId },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      };
      
      console.log('Constraints:', constraints);
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Stream obtained:', stream);
      console.log('📹 Tracks del stream:', stream.getTracks());
      
      // Store stream in ref
      streamRef.current = stream;
      
      // Set streaming to true - useEffect will handle attaching the stream
      setIsStreaming(true);
      setStreamStats({
        frameCount: 0,
        detectionCount: 0,
        elapsedTime: 0,
        recordingId: null
      });
      
      // NUEVO: Capturar timestamp de inicio y resetear cronómetro
      const now = new Date();
      const formattedTimestamp = now.toLocaleString('es-EC', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
      setStartTimestamp(formattedTimestamp);
      streamingStartTimeRef.current = Date.now();
      setElapsedTime(0);
      
      console.log('✅ Stream iniciado correctamente');
      console.log('📅 Timestamp inicio:', formattedTimestamp);
      
      // ✅ Iniciar sesión del YOLOProcessor para guardar JSON
      try {
        const cameraName = selectedPhysicalCamera.label || selectedPhysicalCamera.deviceId || 'Unknown Camera';
        const response = await fetch('http://localhost:8001/api/streaming/processor-session/start/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ camera_name: cameraName })
        });
        
        const data = await response.json();
        
        if (data.success) {
          setCurrentSessionId(data.session_id);
          console.log('✅ YOLOProcessor session started:', data.session_id);
          toast.success('▶️ Streaming iniciado - Guardando detecciones en JSON');
        } else {
          console.error('⚠️ Failed to start processor session:', data.error);
          toast.success('▶️ Streaming iniciado (sin guardar detecciones)');
        }
      } catch (sessionError) {
        console.error('⚠️ Error starting processor session:', sessionError);
        toast.success('▶️ Streaming iniciado (sin guardar detecciones)');
      }
      
    } catch (err) {
      console.error('❌ Error starting stream:', err);
      setError(`No se pudo acceder a la cámara: ${(err as Error).message}`);
    }
  };
  const handleStopStream = async () => {
    // Stop frame processing
    stopFrameProcessing();
    
    // ✅ Finalizar sesión del YOLOProcessor y guardar JSON
    try {
      const response = await fetch('http://localhost:8001/api/streaming/processor-session/end/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ YOLOProcessor session ended:', data.session_id);
        console.log(`📄 JSON saved with ${data.total_detections} detections`);
        toast.success(`⏹️ Streaming detenido - ${data.total_detections} detecciones guardadas en JSON`);
      } else {
        console.warn('⚠️ No active session to end');
        toast('⏹️ Streaming detenido', { icon: '✅' });
      }
    } catch (error) {
      console.error('⚠️ Error ending processor session:', error);
      toast('⏹️ Streaming detenido', { icon: '✅' });
    }
    
    // Limpiar session ID
    setCurrentSessionId(null);
    
    // NUEVO: Detener intervalo de cámara IP si existe
    if (ipCameraIntervalRef.current) {
      clearInterval(ipCameraIntervalRef.current);
      ipCameraIntervalRef.current = null;
      console.log('⏹️ Intervalo de cámara IP detenido');
    }
    
    // Stop media tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // Clear video element
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.src = ''; // También limpiar src para cámaras IP
      videoRef.current.load(); // Resetear el elemento
    }
    
    // Clear detections
    setCurrentDetections([]);
    
    // Reset tracking statistics
    setUniqueVehicles(new Set());
    setTotalFramesProcessed(0);
    setTotalDetections(0);
    console.log('🔄 Estadísticas de tracking reseteadas');
    
    // NUEVO: Limpiar cronómetro y timestamp
    streamingStartTimeRef.current = null;
    setElapsedTime(0);
    setStartTimestamp('');
    
    setIsStreaming(false);
    
    toast('⏹️ Streaming detenido - Sesión finalizada', { icon: '✅' });
  };

  // Format elapsed time
  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading cameras...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Camera className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Monitoreo en Vivo</h1>
                <p className="text-sm text-gray-600">
                  Streaming en tiempo real con detección YOLO
                </p>
              </div>
            </div>

            {/* Status Badge */}
            <div className="flex items-center space-x-2">
              {isStreaming ? (
                <span className="flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  <Activity className="w-4 h-4 mr-1 animate-pulse" />
                  Transmitiendo
                </span>
              ) : (
                <span className="flex items-center px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm font-medium">
                  <Clock className="w-4 h-4 mr-1" />
                  Detenido
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Error: {error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column - Video Stream */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Camera Selection */}
            <div className="bg-white rounded-lg shadow-sm p-4 space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Cámara Física
                </label>
                <select
                  value={selectedPhysicalCamera?.deviceId || ''}
                  onChange={(e) => {
                    const camera = physicalCameras.find(c => c.deviceId === e.target.value);
                    if (camera) {
                      handleCameraSelect(camera);
                    }
                  }}
                  disabled={isStreaming}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">-- Seleccionar Cámara --</option>
                  {physicalCameras.map((camera) => (
                    <option key={camera.deviceId} value={camera.deviceId}>
                      {camera.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Show location info if camera was selected from traffic page */}
              {selectedDbCamera && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-sm text-blue-800">
                    <Camera className="w-4 h-4" />
                    <span className="font-medium">Ubicación asignada:</span>
                    <span>{selectedDbCamera.name}</span>
                  </div>
                  {selectedDbCamera.locationId && (
                    <div className="text-xs text-blue-600 mt-1 ml-6">
                      Location ID: {selectedDbCamera.locationId}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Video Stream Viewer */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden relative">
                {isStreaming ? (
                  <div className="relative w-full h-full bg-black">
                    {/* Video element showing live camera feed */}
                    <video
                      ref={videoRef}
                      className="w-full h-full object-contain"
                      autoPlay
                      playsInline
                      muted
                      style={{ backgroundColor: 'black' }}
                    />
                    {/* Canvas overlay for YOLO detections */}
                    <canvas
                      ref={canvasRef}
                      className="absolute inset-0 w-full h-full object-contain pointer-events-none"
                    />
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                    <Camera className="w-16 h-16 mb-4" />
                    <p className="text-lg font-medium">No hay transmisión activa</p>
                    <p className="text-sm">Selecciona una cámara y presiona "Iniciar"</p>
                  </div>
                )}

                {/* Recording Indicator */}
                {isStreaming && (
                  <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-medium">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    <span>TRANSMITIENDO</span>
                  </div>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex justify-center gap-4 max-w-md mx-auto">
                
                {/* Iniciar Button */}
                <button
                  onClick={handleStartStream}
                  disabled={!selectedPhysicalCamera || isStreaming || loading}
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium shadow-md hover:shadow-lg flex-1"
                >
                  <Play className="w-5 h-5" />
                  <span>Iniciar</span>
                </button>

                {/* Detener Button */}
                <button
                  onClick={handleStopStream}
                  disabled={!isStreaming}
                  className="flex items-center justify-center space-x-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium shadow-md hover:shadow-lg flex-1"
                >
                  <Activity className="w-5 h-5" />
                  <span>Detener</span>
                </button>

              </div>
            </div>
          </div>

          {/* Right Column - Stats & Detections */}
          <div className="space-y-6">
            
            {/* Statistics */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-blue-600" />
                Estadísticas de Tracking
              </h2>
              
              <div className="space-y-4">
                {/* Vehículos Únicos - Destacado */}
                <div className="flex justify-between items-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-blue-300">
                  <div className="flex items-center gap-2">
                    <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
                      <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z"/>
                    </svg>
                    <span className="text-sm font-semibold text-gray-700">Vehículos Únicos</span>
                  </div>
                  <span className="text-3xl font-bold text-blue-600">
                    {uniqueVehicles.size}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Frames Procesados</span>
                  <span className="text-lg font-bold text-gray-900">
                    {totalFramesProcessed?.toLocaleString() || 0}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Detecciones en Frame Actual</span>
                  <span className="text-lg font-bold text-blue-600">
                    {currentDetections.length}
                  </span>
                </div>

                {/* Timestamp de Inicio */}
                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
                    </svg>
                    Inicio de Análisis
                  </span>
                  <span className="text-xs font-mono font-bold text-gray-900 bg-blue-50 px-2 py-1 rounded">
                    {startTimestamp || 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd"/>
                    </svg>
                    Tiempo Transcurrido
                  </span>
                  <span className="text-lg font-mono font-bold text-green-600">
                    {formatTime(elapsedTime)}
                  </span>
                </div>
              </div>
            </div>

            {/* Current Detections Panel */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                Vehículos Trackeados
              </h2>

              {currentDetections.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {currentDetections.map((detection, idx) => {
                    // Color consistente basado en ID
                    const colors = [
                      'bg-green-500',
                      'bg-red-500',
                      'bg-blue-500',
                      'bg-yellow-500',
                      'bg-purple-500',
                      'bg-cyan-500',
                      'bg-orange-500',
                      'bg-pink-500',
                      'bg-indigo-500',
                      'bg-teal-500'
                    ];
                    const colorClass = detection.id !== undefined 
                      ? colors[detection.id % colors.length]
                      : 'bg-gray-500';
                    
                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center space-x-3 flex-1">
                          <div className={`w-3 h-3 rounded-full ${colorClass}`}></div>
                          <div className="flex flex-col">
                            <div className="flex items-center gap-2">
                              {detection.id !== undefined && (
                                <span className="text-xs font-bold text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                                  ID#{detection.id}
                                </span>
                              )}
                              <span className="text-sm font-medium text-gray-900 capitalize">
                                {detection.label}
                              </span>
                            </div>
                            {detection.age !== undefined && (
                              <span className="text-xs text-gray-500">
                                {detection.age} frames
                              </span>
                            )}
                          </div>
                        </div>
                        <span className="text-xs font-semibold text-gray-600 bg-white px-2 py-1 rounded">
                          {detection.confidence !== undefined 
                            ? `${(detection.confidence * 100).toFixed(0)}%`
                            : 'N/A'
                          }
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <p className="text-sm">
                    {isStreaming ? 'Buscando vehículos...' : 'No hay detecciones'}
                  </p>
                </div>
              )}
            </div>

            {/* Recording Info */}
            {isStreaming && streamStats.recordingId && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <HardDrive className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-blue-900 mb-1">
                      Grabando Localmente
                    </h3>
                    <p className="text-xs text-blue-700">
                      La grabación se subirá a AWS S3 cuando presiones "Guardar"
                    </p>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveMonitoring;
