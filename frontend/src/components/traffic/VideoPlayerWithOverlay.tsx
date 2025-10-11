import React, { useRef, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface VehicleDetection {
  timestamp: number;
  track_id: string;
  vehicle_type: string;
  confidence: number;
  bbox: BoundingBox;
  first_appearance: boolean;
}

interface VideoPlayerProps {
  videoFile: File;
  analysisId: string;
  wsUrl: string;
}

const VEHICLE_COLORS: Record<string, string> = {
  car: '#00FF00',      // Verde
  truck: '#FF0000',    // Rojo
  bus: '#0000FF',      // Azul
  motorcycle: '#FFFF00' // Amarillo
};

export const VideoPlayerWithOverlay: React.FC<VideoPlayerProps> = ({
  videoFile,
  analysisId,
  wsUrl
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  const [detections, setDetections] = useState<VehicleDetection[]>([]);
  const [currentDetections, setCurrentDetections] = useState<VehicleDetection[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    cars: 0,
    trucks: 0,
    buses: 0,
    motorcycles: 0
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>('');

  // Crear Blob URL del video
  useEffect(() => {
    const url = URL.createObjectURL(videoFile);
    setVideoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [videoFile]);

  // Conectar WebSocket
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const fullWsUrl = `${protocol}//${wsUrl}/ws/traffic/analysis/${analysisId}/`;
    
    const ws = new WebSocket(fullWsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      addLog('✅ Conexión WebSocket establecida');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'vehicle_detected':
          handleVehicleDetection(data);
          break;
        case 'progress_update':
          addLog(`⏳ Progreso: ${data.progress}%`);
          break;
        case 'processing_complete':
          addLog('✅ Procesamiento completado');
          break;
        case 'processing_error':
          addLog(`❌ Error: ${data.error}`);
          break;
        case 'log_message':
          addLog(data.message);
          break;
      }
    };

    ws.onerror = (error) => {
      addLog('❌ Error en WebSocket');
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      addLog('🔌 Conexión WebSocket cerrada');
    };

    return () => {
      ws.close();
    };
  }, [analysisId, wsUrl]);

  // Manejar detecciones de vehículos
  const handleVehicleDetection = (data: VehicleDetection) => {
    setDetections(prev => [...prev, data]);
    
    // Actualizar estadísticas si es primera aparición
    if (data.first_appearance) {
      setStats(prev => ({
        total: prev.total + 1,
        cars: prev.cars + (data.vehicle_type === 'car' ? 1 : 0),
        trucks: prev.trucks + (data.vehicle_type === 'truck' ? 1 : 0),
        buses: prev.buses + (data.vehicle_type === 'bus' ? 1 : 0),
        motorcycles: prev.motorcycles + (data.vehicle_type === 'motorcycle' ? 1 : 0)
      }));
      
      addLog(`🚗 Nuevo ${data.vehicle_type} detectado (ID: ${data.track_id})`);
    }
  };

  // Agregar log
  const addLog = (message: string) => {
    setLogs(prev => {
      const newLogs = [message, ...prev];
      return newLogs.slice(0, 100); // Mantener últimos 100 logs
    });
  };

  // Dibujar bounding boxes en el canvas
  const drawBoundingBoxes = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (!video || !canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Ajustar tamaño del canvas al video
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Obtener tiempo actual del video
    const currentTime = video.currentTime;
    
    // Filtrar detecciones cercanas al tiempo actual (±300ms de tolerancia)
    const relevantDetections = detections.filter(d => 
      Math.abs(d.timestamp - currentTime) < 0.3
    );

    setCurrentDetections(relevantDetections);

    // Dibujar cada bounding box
    relevantDetections.forEach(detection => {
      const color = VEHICLE_COLORS[detection.vehicle_type] || '#FFFFFF';
      const { x, y, width, height } = detection.bbox;

      // Dibujar rectángulo
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);

      // Dibujar etiqueta
      const label = `${detection.vehicle_type} ${detection.track_id} (${(detection.confidence * 100).toFixed(0)}%)`;
      ctx.fillStyle = color;
      ctx.fillRect(x, y - 25, ctx.measureText(label).width + 10, 25);
      ctx.fillStyle = '#000000';
      ctx.font = '16px Arial';
      ctx.fillText(label, x + 5, y - 7);
    });

    // Continuar dibujando si el video está reproduciéndose
    if (isPlaying) {
      requestAnimationFrame(drawBoundingBoxes);
    }
  };

  // Manejar play/pause
  useEffect(() => {
    if (isPlaying) {
      drawBoundingBoxes();
    }
  }, [isPlaying]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Video Player con Canvas Overlay */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Análisis de Video en Tiempo Real</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative w-full bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              src={videoUrl}
              controls
              className="w-full h-auto"
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onSeeked={drawBoundingBoxes}
            />
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 w-full h-full pointer-events-none"
            />
          </div>

          {/* Detecciones Actuales */}
          <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <h4 className="font-semibold mb-2">Detecciones en Frame Actual:</h4>
            <div className="flex flex-wrap gap-2">
              {currentDetections.length === 0 ? (
                <span className="text-gray-500">Sin detecciones en este frame</span>
              ) : (
                currentDetections.map((d, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-full text-sm font-medium"
                    style={{
                      backgroundColor: VEHICLE_COLORS[d.vehicle_type] + '40',
                      color: VEHICLE_COLORS[d.vehicle_type]
                    }}
                  >
                    {d.vehicle_type} {d.track_id}
                  </span>
                ))
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Panel Lateral: Stats y Logs */}
      <div className="space-y-4">
        {/* Estadísticas */}
        <Card>
          <CardHeader>
            <CardTitle>Estadísticas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-semibold">Total Vehículos:</span>
                <span className="text-2xl font-bold text-blue-600">{stats.total}</span>
              </div>
              <div className="border-t pt-2 space-y-2">
                <div className="flex justify-between">
                  <span style={{ color: VEHICLE_COLORS.car }}>🚗 Autos:</span>
                  <span className="font-semibold">{stats.cars}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: VEHICLE_COLORS.truck }}>🚚 Camiones:</span>
                  <span className="font-semibold">{stats.trucks}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: VEHICLE_COLORS.bus }}>🚌 Autobuses:</span>
                  <span className="font-semibold">{stats.buses}</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: VEHICLE_COLORS.motorcycle }}>🏍️ Motos:</span>
                  <span className="font-semibold">{stats.motorcycles}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Logs */}
        <Card>
          <CardHeader>
            <CardTitle>Registro de Eventos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-96 overflow-y-auto bg-gray-900 text-green-400 p-3 rounded font-mono text-xs">
              {logs.map((log, idx) => (
                <div key={idx} className="mb-1">
                  {log}
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-gray-500">Esperando eventos...</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
