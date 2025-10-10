import React from 'react';

interface TrafficStatusBadgeProps {
  level: 'low' | 'moderate' | 'heavy' | 'congested';
  size?: 'sm' | 'md' | 'lg';
}

const TrafficStatusBadge: React.FC<TrafficStatusBadgeProps> = ({ level, size = 'md' }) => {
  const getStatusConfig = () => {
    switch (level) {
      case 'low':
        return {
          label: 'Fluido',
          color: 'bg-success-100 text-success-800 border-success-200',
          dotColor: 'bg-success-500'
        };
      case 'moderate':
        return {
          label: 'Moderado',
          color: 'bg-warning-100 text-warning-800 border-warning-200',
          dotColor: 'bg-warning-500'
        };
      case 'heavy':
        return {
          label: 'Congestionado',
          color: 'bg-orange-100 text-orange-800 border-orange-200',
          dotColor: 'bg-orange-500'
        };
      case 'congested':
        return {
          label: 'Muy Congestionado',
          color: 'bg-error-100 text-error-800 border-error-200',
          dotColor: 'bg-error-500'
        };
      default:
        return {
          label: 'Desconocido',
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          dotColor: 'bg-gray-500'
        };
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1 text-xs';
      case 'lg':
        return 'px-4 py-2 text-base';
      default:
        return 'px-3 py-1.5 text-sm';
    }
  };

  const config = getStatusConfig();

  return (
    <span className={`inline-flex items-center space-x-1.5 ${getSizeClasses()} rounded-full font-medium border ${config.color}`}>
      <span className={`w-2 h-2 rounded-full ${config.dotColor}`}></span>
      <span>{config.label}</span>
    </span>
  );
};

export default TrafficStatusBadge;
