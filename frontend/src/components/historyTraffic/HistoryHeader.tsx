import { Download } from "lucide-react";
import { TrafficType } from "../../types/historyTraffic";

export default function HistoryHeader({
  locations,
  trafficType,
  selectedLocation,
  setSelectedLocation,
  dateRangeType,
  setTrafficType,
  handleDateRangeChange,
  onExportClick,
}: any) {
  return (
    <div className="w-full mx-auto pl-0 pr-0 pt-6 pb-0 ">
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Análisis Histórico
            </h2>
            <p className="text-sm text-gray-500">
              Revisa patrones y tendencias de tráfico
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 hide-controls">
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            {locations.map((element) => (
              <option key={element?.id} value={element?.id}>
                {element?.description}
              </option>
            ))}
          </select>

          <select
            value={dateRangeType}
            onChange={(e) => handleDateRangeChange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            <option value="today">Hoy</option>
            <option value="7days">Últimos 7 días</option>
            <option value="30days">Últimos 30 días</option>
            <option value="custom">Personalizar</option>
          </select>

          <select
            value={trafficType}
            onChange={(e) => setTrafficType(e.target.value as TrafficType)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            <option value="congestion">Congestión</option>
            <option value="velocity">Velocidad</option>
            <option value="volume">Volumen</option>
          </select>

          <button
            className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={() => onExportClick()}
          >
            <Download className="w-4 h-4" />
            Exportar
          </button>
        </div>
      </div>
    </div>
  );
}
