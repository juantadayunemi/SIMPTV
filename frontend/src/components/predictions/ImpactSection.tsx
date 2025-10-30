import { ImpactMetrics } from '../../types/forecast';

interface ImpactSectionProps {
  metrics: ImpactMetrics;
}

export default function ImpactSection({ holidays_impact, seasonality_impact }: ImpactMetrics) {

  console.log("Festividades: ", holidays_impact)
  console.log("Estacionalidad: ", seasonality_impact)
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4">Análisis de Impacto</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs sm:text-sm text-gray-600">Impacto de Feriados</span>
            <span className="text-base sm:text-lg font-bold text-blue-600">
              
              {holidays_impact > 0 ? '+' : ''}{holidays_impact?.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${holidays_impact >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(Math.abs(holidays_impact), 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs sm:text-sm text-gray-600">Impacto de Estacionalidad</span>
            <span className="text-base sm:text-lg font-bold text-blue-600">
              {seasonality_impact > 0 ? '+' : ''}{seasonality_impact?.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${seasonality_impact >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(Math.abs(seasonality_impact), 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}