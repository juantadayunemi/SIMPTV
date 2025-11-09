import { useState, useMemo } from 'react';
import { DayData } from '../../types/historyTraffic';
import { useToast } from '../ui/ToastContainer';
import DocumentMagnifyingGlassIcon from '@heroicons/react/24/outline/DocumentMagnifyingGlassIcon';

interface TrafficChartProps {
  data: DayData[];
  color: string;
  title: string;
  subtitle: string;
}

export default function TrafficChart({ data, color, title, subtitle }: TrafficChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<{ index: number; x: number; y: number } | null>(null);
  const toast = useToast();
  if (data === undefined) {
    data = [];
    toast.error("No hay datos disponibles");
    return
  }
  const chartDimensions = {
    width: 1000,
    height: 400,
    padding: { top: 40, right: 40, bottom: 60, left: 60 },
  };

  const chartArea = {
    width: chartDimensions.width - chartDimensions.padding.left - chartDimensions.padding.right,
    height: chartDimensions.height - chartDimensions.padding.top - chartDimensions.padding.bottom,
  };

  const { points, maxValue, minValue, xLabels } = useMemo(() => {
    if (!data || data.length === 0) {
      return { points: [], maxValue: 0, minValue: 0, xLabels: [] };
    }

    const values = data.map(d => d.total);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;

    const calculatedPoints = data.map((item, index) => {
      const x = chartDimensions.padding.left + (index / (data.length - 1 || 1)) * chartArea.width;
      const normalizedValue = (item.total - min) / range;
      const y = chartDimensions.padding.top + chartArea.height - (normalizedValue * chartArea.height);
      return { x, y, value: item.total, date: item.day };
    });

    const labelIndices = data.length <= 7
      ? data.map((_, i) => i)
      : data.length <= 30
      ? data.map((_, i) => i).filter((_, i) => i % Math.ceil(data.length / 7) === 0)
      : data.map((_, i) => i).filter((_, i) => i % Math.ceil(data.length / 10) === 0);

    const labels = labelIndices.map(i => ({
      index: i,
      x: chartDimensions.padding.left + (i / (data.length - 1 || 1)) * chartArea.width,
      date: data[i].day,
    }));

    return { points: calculatedPoints, maxValue: max, minValue: min, xLabels: labels };
  }, [data, chartArea.width, chartArea.height, chartDimensions.padding]);

  const pathD = useMemo(() => {
    if (points.length === 0) return '';

    const path = points.map((point, index) => {
      if (index === 0) return `M ${point.x} ${point.y}`;
      return `L ${point.x} ${point.y}`;
    }).join(' ');

    return path;
  }, [points]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
  };

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-500">{subtitle}</p>
        </div>
        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
          <DocumentMagnifyingGlassIcon className="h-12 w-12 text-gray-300 mb-2" />
          <span className="select-none">No hay datos disponibles</span>
        </div>
      </div>
    );
  }

  const yAxisTicks = 5;
  const yAxisValues = Array.from({ length: yAxisTicks }, (_, i) => {
    const value = minValue + (maxValue - minValue) * (i / (yAxisTicks - 1));
    return Math.round(value);
  });

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mt-0">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500">{subtitle}</p>
      </div>

      <div className="relative">
        <svg
          width={chartDimensions.width}
          height={chartDimensions.height}
          className="overflow-visible"
        >
          <defs>
            <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.2" />
              <stop offset="100%" stopColor={color} stopOpacity="0.05" />
            </linearGradient>
          </defs>

          <rect
            x={chartDimensions.padding.left}
            y={chartDimensions.padding.top}
            width={chartArea.width}
            height={chartArea.height}
            fill="transparent"
            stroke="#e5e7eb"
            strokeWidth="1"
          />

          {yAxisValues.map((value, i) => {
            const y = chartDimensions.padding.top + chartArea.height - (i / (yAxisTicks - 1)) * chartArea.height;
            return (
              <g key={`y-axis-${i}`}>
                <line
                  x1={chartDimensions.padding.left}
                  y1={y}
                  x2={chartDimensions.padding.left + chartArea.width}
                  y2={y}
                  stroke="#f3f4f6"
                  strokeWidth="1"
                />
                <text
                  x={chartDimensions.padding.left - 10}
                  y={y}
                  textAnchor="end"
                  alignmentBaseline="middle"
                  className="text-xs fill-gray-600"
                >
                  {value}
                </text>
              </g>
            );
          })}

          {xLabels.map((label) => (
            <text
              key={`x-label-${label.index}`}
              x={label.x}
              y={chartDimensions.height - chartDimensions.padding.bottom + 20}
              textAnchor="middle"
              className="text-xs fill-gray-600"
            >
              {formatDate(label.date)}
            </text>
          ))}

          {points.length > 0 && (
            <>
              <path
                d={`${pathD} L ${points[points.length - 1].x} ${chartDimensions.padding.top + chartArea.height} L ${points[0].x} ${chartDimensions.padding.top + chartArea.height} Z`}
                fill={`url(#gradient-${color})`}
              />

              <path
                d={pathD}
                fill="none"
                stroke={color}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {points.map((point, index) => (
                <circle
                  key={`point-${index}`}
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  fill="white"
                  stroke={color}
                  strokeWidth="2"
                  className="cursor-pointer transition-all hover:r-8"
                  onMouseEnter={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setHoveredPoint({ index, x: rect.left, y: rect.top });
                  }}
                  onMouseLeave={() => setHoveredPoint(null)}
                />
              ))}
            </>
          )}
        </svg>

        {hoveredPoint !== null && (
          <div
            className="fixed bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm z-50 pointer-events-none"
            style={{
              left: `${hoveredPoint.x}px`,
              top: `${hoveredPoint.y - 60}px`,
              transform: 'translateX(-50%)',
            }}
          >
            <div className="font-semibold">{formatDate(points[hoveredPoint.index].date)}</div>
            <div className="text-gray-300">Total: {Math.round(points[hoveredPoint.index].value)}</div>
          </div>
        )}
      </div>
    </div>
  );
}
