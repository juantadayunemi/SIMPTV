import { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { ComparisonPeriod } from '../../types/forecast';

interface ComparisonSectionProps {
  selectedPeriod: 'daily' | 'monthly' | 'yearly';
  comparison: ComparisonPeriod;
  onPeriodChange?: (period: 'daily' | 'monthly' | 'yearly') => void;
  handlePeriodChange?: (period: 'daily' | 'monthly' | 'yearly') => void;
}

export default function ComparisonSection({ selectedPeriod, comparison, onPeriodChange, handlePeriodChange }: ComparisonSectionProps) {

  const periods: ComparisonPeriod[] = [
    { label: 'Día anterior', value: 'daily' },
    { label: 'Mes anterior', value: 'monthly' },
    { label: 'Año anterior', value: 'yearly' }
  ];

  const onHandlePeriodChange = (period: 'daily' | 'monthly' | 'yearly') => {
    console.log(">>> period", period);
    onPeriodChange?.(period);
    handlePeriodChange?.(period);
  };

  const renderMetric = (label: string, value: number) => {
    const isPositive = value >= 0;
    const Icon = isPositive ? TrendingUp : TrendingDown;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';
    const bgClass = isPositive ? 'bg-green-50' : 'bg-red-50';

    return (
      <div className={`${bgClass} rounded-lg p-4`}>
        <div className="text-sm text-gray-600 mb-2">{label}</div>
        <div className={`flex items-center gap-2 ${colorClass}`}>
          <Icon size={24} />
          <span className="text-2xl font-bold">
            {isPositive ? '+' : ''}{value?.toFixed(1)}%
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-800">Comparación de Periodo</h3>
        <select
          value={selectedPeriod}
          onChange={(e) => onHandlePeriodChange(e.target.value as 'daily' | 'monthly' | 'yearly')}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {periods.map((period) => (
            <option key={period.value} value={period.value}>
              {period.label}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {renderMetric('Cambio en Yhat', comparison?.yhat_change)}
        {renderMetric('Cambio en Tendencia', comparison?.trend_change)}
      </div>
    </div>
  );
}
