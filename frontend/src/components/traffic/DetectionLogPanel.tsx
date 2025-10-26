/**
 * DetectionLogPanel Component
 * Panel de logs en tiempo real para mostrar detecciones de vehículos y placas
 */

import React, { useRef, useEffect } from 'react';
import { RealtimeDetectionEvent } from '@traffic-analysis/shared';

interface DetectionLogPanelProps {
  detections: RealtimeDetectionEvent[];
  maxLogs?: number;
}

export const DetectionLogPanel: React.FC<DetectionLogPanelProps> = ({ 
  detections, 
  maxLogs = 100 
}) => {
  const logRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al final cuando llegan nuevas detecciones
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [detections]);

  // Limitar cantidad de logs mostrados para performance
  const displayedDetections = detections.slice(-maxLogs);

  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    const dateStr = date.toLocaleDateString('es-EC', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    const timeStr = date.toLocaleTimeString('es-EC', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    return `${dateStr} ${timeStr}`;
  };

  const getVehicleTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'CAR': 'auto',
      'TRUCK': 'camión',
      'MOTORCYCLE': 'moto',
      'BUS': 'bus',
      'BICYCLE': 'bicicleta',
      'OTHER': 'otro'
    };
    return labels[type] || type.toLowerCase();
  };

  return (
    <div 
      ref={logRef}
      className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-y-auto"
      style={{
        height: '400px', // Altura fija más grande que antes (antes 256px)
        scrollBehavior: 'smooth',
        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
        // Scrollbar personalizado (webkit)
        scrollbarWidth: 'thin' as const,
        scrollbarColor: '#4B5563 #1F2937'
      }}
    >
      <style>{`
        /* Scrollbar personalizado para Webkit (Chrome, Safari, Edge) */
        .bg-gray-900::-webkit-scrollbar {
          width: 10px;
        }
        .bg-gray-900::-webkit-scrollbar-track {
          background: #1F2937;
          border-radius: 5px;
        }
        .bg-gray-900::-webkit-scrollbar-thumb {
          background: #4B5563;
          border-radius: 5px;
          border: 2px solid #1F2937;
        }
        .bg-gray-900::-webkit-scrollbar-thumb:hover {
          background: #6B7280;
        }
      `}</style>
      
      {displayedDetections.length === 0 ? (
        <div className="text-gray-500 text-center py-8">
          Esperando detecciones...
        </div>
      ) : (
        displayedDetections.map((detection, idx) => (
          <div key={`${detection.trackId}-${idx}`} className="mb-1 hover:bg-gray-800 px-2 py-1 rounded transition-colors">
            <span className="text-gray-500">
              {formatTimestamp(detection.timestamp)}
            </span>
            {' '}tipo: <span className="text-yellow-400">{getVehicleTypeLabel(detection.vehicleType)}</span>
            {detection.plateNumber ? (
              <>, placa <span className="text-blue-400 font-bold">{detection.plateNumber}</span></>
            ) : (
              <>, placa <span className="text-gray-600">desconocida</span></>
            )}
            {detection.confidence && (
              <span className="text-gray-600">
                {' '}conf: {(detection.confidence * 100).toFixed(1)}%
              </span>
            )}
            <span className="text-gray-700">...........</span>
          </div>
        ))
      )}
    </div>
  );
};

export default DetectionLogPanel;
