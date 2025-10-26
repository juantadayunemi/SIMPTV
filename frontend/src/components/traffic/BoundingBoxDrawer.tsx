/**
 * BoundingBoxDrawer.tsx
 * Componente para dibujar bounding boxes sobre el video/canvas en tiempo real
 * ✅ Compatible con HTMLVideoElement y HTMLCanvasElement
 */

import React, { useEffect, useRef } from 'react';

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number]; // [x, y, width, height]
  confidence: number;
}

interface BoundingBoxDrawerProps {
  videoRef: React.RefObject<HTMLVideoElement | HTMLCanvasElement>;
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
    const videoOrCanvas = videoRef.current;
    
    if (!canvas || !videoOrCanvas) {
      console.warn('⚠️ BoundingBoxDrawer: canvas o videoRef no disponible');
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error('❌ BoundingBoxDrawer: No se pudo obtener contexto 2D');
      return;
    }

    // ✅ Obtener dimensiones según el tipo de elemento
    let canvasWidth: number;
    let canvasHeight: number;

    if (videoOrCanvas instanceof HTMLVideoElement) {
      // Es un video
      canvasWidth = width || videoOrCanvas.videoWidth || 640;
      canvasHeight = height || videoOrCanvas.videoHeight || 480;
    } else if (videoOrCanvas instanceof HTMLCanvasElement) {
      // Es un canvas
      canvasWidth = width || videoOrCanvas.width || 640;
      canvasHeight = height || videoOrCanvas.height || 480;
    } else {
      // Fallback para el objeto dummy
      canvasWidth = width || (videoOrCanvas as any).videoWidth || 640;
      canvasHeight = height || (videoOrCanvas as any).videoHeight || 480;
    }

    // Ajustar tamaño del canvas overlay
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;


    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Si no hay detecciones, no dibujar nada
    if (!detections || detections.length === 0) {

      return;
    }

    // Dibujar cada detección
    detections.forEach((detection, index) => {
      const [x, y, w, h] = detection.bbox;
      const color = COLORS[detection.vehicle_type.toLowerCase()] || COLORS.unknown;
  

      // Dibujar bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      // Dibujar fondo para label
      const label = `${detection.vehicle_type} #${detection.track_id} (${(detection.confidence * 100).toFixed(0)}%)`;
      ctx.font = 'bold 14px sans-serif';
      const labelWidth = ctx.measureText(label).width;
      const labelHeight = 25;
      
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.8;
      ctx.fillRect(x, y - labelHeight, labelWidth + 10, labelHeight);

      // Dibujar texto
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
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