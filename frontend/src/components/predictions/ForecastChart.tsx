import { useState } from 'react';
import { ForecastData } from '../types/forecast';

interface ForecastChartProps {
  data: ForecastData | null;
  selectedDate: string;
}

interface TooltipData {
  x: number;
  y: number;
  value: number;
  time: string;
}

export default function ForecastChart({ data, selectedDate }: ForecastChartProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  if (!data || !data.forecast || data.forecast.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Pronóstico de 24 Horas - {selectedDate}
        </h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          No hay datos disponibles
        </div>
      </div>
    );
  }

  const forecastPoints = data.forecast;

  const values = forecastPoints.map(d => d.yhat);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;

  const padding = range * 0.1;
  const adjustedMax = maxValue + padding;
  const adjustedMin = minValue - padding;
  const adjustedRange = adjustedMax - adjustedMin;

  const points = forecastPoints.map((d, index) => {
    const x = (index / (forecastPoints.length - 1)) * 100;
    const y = 100 - ((d.yhat - adjustedMin) / adjustedRange) * 100;
    return { x, y, value: d.yhat, time: d.ds };
  });

  const pathData = points.map((p, i) =>
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ');

  const fillPath = `${pathData} L 100 100 L 0 100 Z`;

  const displayTimeLabels = forecastPoints.filter((_, index) => {
    const totalPoints = forecastPoints.length;
    const step = Math.ceil(totalPoints / 6);
    return index % step === 0 || index === totalPoints - 1;
  });

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const relativeX = (x / rect.width) * 100;

    const closestPoint = points.reduce((prev, curr) => {
      return Math.abs(curr.x - relativeX) < Math.abs(prev.x - relativeX) ? curr : prev;
    });

    if (Math.abs(closestPoint.x - relativeX) < 5) {
      setTooltip({
        x: (closestPoint.x / 100) * rect.width,
        y: (closestPoint.y / 100) * rect.height,
        value: closestPoint.value,
        time: closestPoint.time
      });
    } else {
      setTooltip(null);
    }
  };

  const handleMouseLeave = () => {
    setTooltip(null);
  };

  const yAxisLabels = [
    adjustedMax,
    adjustedMax - adjustedRange * 0.25,
    adjustedMax - adjustedRange * 0.5,
    adjustedMax - adjustedRange * 0.75,
    adjustedMin
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Pronóstico de 24 Horas - {selectedDate}
      </h3>

      <div className="relative h-96 bg-gray-50 rounded-lg p-6">
        <div className="absolute left-2 top-6 bottom-16 flex flex-col justify-between text-xs text-gray-500">
          {yAxisLabels.map((label, i) => (
            <span key={i} className="text-right pr-2">{label?.toFixed(0)}</span>
          ))}
        </div>

        <div
          className="ml-14 mr-4 h-[calc(100%-3rem)] relative"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="none">
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#FFA500" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#FFA500" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {[0, 25, 50, 75, 100].map((y) => (
              <line
                key={y}
                x1="0"
                y1={y}
                x2="100"
                y2={y}
                stroke="#E5E7EB"
                strokeWidth="0.2"
                vectorEffect="non-scaling-stroke"
              />
            ))}

            <path
              d={fillPath}
              fill="url(#gradient)"
            />

            <path
              d={pathData}
              fill="none"
              stroke="#FFA500"
              strokeWidth="0.8"
              vectorEffect="non-scaling-stroke"
            />

            {points.map((point, i) => (
              <circle
                key={i}
                cx={point.x}
                cy={point.y}
                r="1.2"
                fill="#FFA500"
                className="cursor-pointer hover:r-2"
                vectorEffect="non-scaling-stroke"
                opacity={i % Math.ceil(points.length / 20) === 0 ? 1 : 0}
              />
            ))}
          </svg>

          {tooltip && (
            <div
              className="absolute pointer-events-none z-10"
              style={{
                left: `${tooltip.x}px`,
                top: `${tooltip.y - 60}px`,
                transform: 'translateX(-50%)'
              }}
            >
              <div className="bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-xs whitespace-nowrap">
                <div className="font-semibold">{formatDateTime(tooltip.time)}</div>
                <div className="text-orange-300">Valor: {tooltip.value?.toFixed(0)}</div>
              </div>
              <div
                className="w-0 h-0 mx-auto"
                style={{
                  borderLeft: '6px solid transparent',
                  borderRight: '6px solid transparent',
                  borderTop: '6px solid #111827'
                }}
              />
            </div>
          )}

          <div className="absolute -bottom-8 left-0 right-0 flex justify-between text-xs text-gray-500">
            {displayTimeLabels.map((point, i) => (
              <span key={i} className="transform -rotate-0">
                {formatTime(point.ds)}
              </span>
            ))}
          </div>
        </div>

        <div className="absolute bottom-2 left-0 right-0 text-center text-sm text-gray-600">
          <span className="font-medium">Tiempo (Horas)</span>
        </div>
      </div>

      <div className="mt-4 flex justify-center gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-orange-500"></div>
          <span>Predicción (yhat)</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Total de puntos: {forecastPoints.length}</span>
        </div>
      </div>
    </div>
  );
}
