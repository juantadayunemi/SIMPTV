/**
 * BoundingBoxDrawer.tsx
 * Componente para dibujar bounding boxes sobre el video en tiempo real
 */

import React, { useEffect, useRef } from 'react';

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number]; // [x, y, width, height]
  confidence: number;
}

interface BoundingBoxDrawerProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  detections: Detection[];
  width?: number;
  height?: number;
}

const COLORS: Record<string, string> = {
  car: '#3b82f6',        // azul
  truck: '#ef4444',      // rojo
  motorcycle: '#10b981', // verde
  bus: '#f59e0b',        // naranja
  bicycle: '#8b5cf6',    // morado
  unknown: '#6b7280'     // gris
};

const BoundingBoxDrawer: React.FC<BoundingBoxDrawerProps> = ({
  videoRef,
  detections,
  width,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Ajustar tamaño del canvas al video
    canvas.width = width || video.videoWidth || 640;
    canvas.height = height || video.videoHeight || 480;

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Si no hay detecciones, no dibujar nada
    if (!detections || detections.length === 0) return;

    // Dibujar cada detección
    detections.forEach((detection) => {
      const [x, y, w, h] = detection.bbox;
      const color = COLORS[detection.vehicle_type] || COLORS.unknown;

      // Dibujar bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      // Dibujar fondo para label
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.8;
      const labelHeight = 25;
      ctx.fillRect(x, y - labelHeight, w, labelHeight);

      // Dibujar texto
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 14px sans-serif';
      const label = `${detection.vehicle_type} #${detection.track_id} (${(detection.confidence * 100).toFixed(0)}%)`;
      ctx.fillText(label, x + 5, y - 7);
    });

  }, [detections, videoRef, width, height]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ 
        width: '100%', 
        height: '100%', 
        objectFit: 'contain',
        zIndex: 10
      }}
    />
  );
};

export default BoundingBoxDrawer;