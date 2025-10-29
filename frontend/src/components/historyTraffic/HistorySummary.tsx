import StatCard from "../historyTraffic/StatCard";
import { Gauge, TrendingUp, Calendar, Filter, Users } from "lucide-react";

export function HistorySummary({
  trafficType,
  congestionData,
  velocityData,
  volumeData,
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {renderStats()}
    </div>
  );
}
