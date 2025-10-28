import {
  Download,
  Gauge,
  TrendingUp,
  Users,
  Calendar,
  Filter,
} from "lucide-react";
import { DateRangeType, TrafficType } from "../../types/historyTraffic";
import StatCard from "./StatCard";
import { on } from "events";

export default function HistoryHeader({
  locations,
  trafficType,
  congestionData,
  velocityData,
  volumeData,
  selectedLocation,
  setSelectedLocation,
  dateRangeType,
  setTrafficType,
  handleDateRangeChange,
  onExportClick
}: any) {
  const renderStats = () => {
    if (trafficType === "congestion" && congestionData) {
      return (
        <>
          <StatCard
            title="Velocidad Promedio"
            value={`${congestionData?.avg_velocity?.toFixed(0)} km/h`}
            subtitle="En el periodo seleccionado"
            icon={Gauge}
            iconColor="bg-green-100 text-green-600"
          />
          <StatCard
            title="Congestión Promedio"
            value={`${(congestionData?.avg_congestion * 100)?.toFixed(2)}%`}
            subtitle="Nivel de congestión"
            icon={TrendingUp}
            iconColor="bg-orange-100 text-orange-600"
          />
          <StatCard
            title="Hora Pico"
            value={`${congestionData?.rush_hour?.hour}:00`}
            subtitle={`${congestionData?.rush_hour?.count_vehicles?.toFixed(
              0
            )} vehículos`}
            icon={Calendar}
            iconColor="bg-red-100 text-red-600"
          />
          <StatCard
            title="Días Analizados"
            value={congestionData?.days_analyzed}
            subtitle="Periodo de análisis"
            icon={Filter}
            iconColor="bg-blue-100 text-blue-600"
          />
        </>
      );
    }

    if (trafficType === "velocity" && velocityData) {
      return (
        <>
          <StatCard
            title="Velocidad Promedio"
            value={`${velocityData?.avg_velocity?.toFixed(2)} km/h`}
            subtitle="En el periodo seleccionado"
            icon={Gauge}
            iconColor="bg-blue-100 text-blue-600"
          />
          <StatCard
            title="Velocidad Máxima"
            value={`${velocityData?.max_velocity?.toFixed(2)} km/h`}
            subtitle="Velocidad registrada"
            icon={TrendingUp}
            iconColor="bg-green-100 text-green-600"
          />
          <StatCard
            title="Velocidad Mínima"
            value={`${velocityData?.min_velocity?.toFixed(2)} km/h`}
            subtitle="Velocidad registrada"
            icon={TrendingUp}
            iconColor="bg-orange-100 text-orange-600"
          />
          <StatCard
            title="Días Analizados"
            value={velocityData?.days_analyzed}
            subtitle="Periodo de análisis"
            icon={Calendar}
            iconColor="bg-gray-100 text-gray-600"
          />
        </>
      );
    }

    if (trafficType === "volume" && volumeData) {
      return (
        <>
          <StatCard
            title="Cantidad Total de Vehículos"
            value={volumeData?.total_volume?.toFixed(0)}
            subtitle="En el periodo seleccionado"
            icon={Users}
            iconColor="bg-blue-100 text-blue-600"
          />
          <StatCard
            title="Promedio de Vehículos por Hora"
            value={volumeData?.avg_vehicles_per_hour?.toFixed(0)}
            subtitle="Vehículos/hora"
            icon={TrendingUp}
            iconColor="bg-green-100 text-green-600"
          />
          <StatCard
            title="Hora Pico de Tráfico"
            value={`${volumeData?.rush_hour?.hour}:00`}
            subtitle={`${volumeData?.rush_hour?.count_vehicles} vehículos`}
            icon={Calendar}
            iconColor="bg-orange-100 text-orange-600"
          />
          <StatCard
            title="Días Analizados"
            value={volumeData?.days_analyzed}
            subtitle="Periodo de análisis"
            icon={Filter}
            iconColor="bg-gray-100 text-gray-600"
          />
        </>
      );
    }

    return null;
  };

  return (
    <div className="w-full mx-auto pl-0 pr-0 pt-6 pb-4">
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {renderStats()}
      </div>
    </div>
  );
}
