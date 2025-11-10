import React, { useEffect, useRef } from 'react';

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: [number, number, number, number];
  confidence: number;
  speed_kmh?: number;
  speed_category?: string;
}

interface BoundingBoxDrawerProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  detections: Detection[];
}

const BoundingBoxDrawer: React.FC<BoundingBoxDrawerProps> = ({ videoRef, detections }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const updateCanvas = () => {
      // ✅ Obtener dimensiones RENDERIZADAS del video en pantalla
      const displayWidth = video.clientWidth;
      const displayHeight = video.clientHeight;
      
      // ✅ Ajustar canvas al tamaño VISUAL del video (no al tamaño original)
      canvas.width = displayWidth;
      canvas.height = displayHeight;

      // ✅ Calcular el área visible con object-cover
      // object-cover hace que el video llene el container manteniendo aspect ratio
      const videoAspect = video.videoWidth / video.videoHeight;
      const displayAspect = displayWidth / displayHeight;
      
      let renderWidth, renderHeight, offsetX, offsetY;
      
      if (videoAspect > displayAspect) {
        // Video más ancho que container - se recorta a los lados
        renderHeight = displayHeight;
        renderWidth = displayHeight * videoAspect;
        offsetX = (displayWidth - renderWidth) / 2;
        offsetY = 0;
      } else {
        // Video más alto que container - se recorta arriba/abajo
        renderWidth = displayWidth;
        renderHeight = displayWidth / videoAspect;
        offsetX = 0;
        offsetY = (displayHeight - renderHeight) / 2;
      }

      // ✅ Calcular escala considerando el área renderizada real
      const scaleX = renderWidth / video.videoWidth;
      const scaleY = renderHeight / video.videoHeight;

      // Limpiar canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Dibujar cada detección
      detections.forEach((det) => {
        const [origX, origY, origW, origH] = det.bbox;
        
        // ✅ ESCALAR coordenadas y aplicar offset por object-cover
        const x = origX * scaleX + offsetX;
        const y = origY * scaleY + offsetY;
        const w = origW * scaleX;
        const h = origH * scaleY;
        
        // Color según tipo de vehículo
        let color = '#00FF00'; // verde por defecto
        switch (det.vehicle_type) {
          case 'car':
            color = '#00FF00'; // verde
            break;
          case 'truck':
            color = '#FF6B00'; // naranja
            break;
          case 'bus':
            color = '#0099FF'; // azul
            break;
          case 'motorcycle':
            color = '#FFD700'; // amarillo
            break;
        }

        // ✅ Color según velocidad (prioridad sobre tipo)
        if (det.speed_kmh && det.speed_kmh > 0) {
          if (det.speed_category === 'slow') {
            color = '#00FF00'; // verde
          } else if (det.speed_category === 'medium') {
            color = '#FFFF00'; // amarillo
          } else if (det.speed_category === 'fast') {
            color = '#FF9900'; // naranja
          } else if (det.speed_category === 'very_fast') {
            color = '#FF0000'; // rojo
          }
        }

        // Dibujar bounding box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        // ✅ Fondo para el texto (más grande para velocidad)
        const labelHeight = det.speed_kmh ? 50 : 30;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(x, y - labelHeight, Math.max(w, 150), labelHeight);

        // Texto del label
        ctx.fillStyle = color;
        ctx.font = 'bold 16px Arial';
        const label = `#${det.track_id} ${det.vehicle_type.toUpperCase()}`;
        ctx.fillText(label, x + 5, y - labelHeight + 20);

        // ✅ MOSTRAR VELOCIDAD
        if (det.speed_kmh && det.speed_kmh > 0) {
          ctx.font = 'bold 14px Arial';
          ctx.fillStyle = '#FFFFFF';
          const speedText = `${det.speed_kmh.toFixed(1)} km/h`;
          ctx.fillText(speedText, x + 5, y - labelHeight + 40);
        }

        // Confianza
        ctx.font = '12px Arial';
        ctx.fillStyle = '#FFFFFF';
        const confText = `${(det.confidence * 100).toFixed(0)}%`;
        ctx.fillText(confText, x + w - 50, y - labelHeight + 20);
      });
    };

    updateCanvas();

    // ✅ Observer para redimensionar canvas cuando cambia el tamaño del video
    const resizeObserver = new ResizeObserver(() => {
      updateCanvas();
    });

    resizeObserver.observe(video);

    return () => {
      resizeObserver.disconnect();
    };
  }, [detections, videoRef]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full h-full pointer-events-none"
      style={{ zIndex: 10 }}
    />
  );
};

export default BoundingBoxDrawer;