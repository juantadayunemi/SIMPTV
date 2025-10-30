import TrafficChart from "./TrafficChart";

export default function HistoryChart({
  isLoading,
  error,
  locations,
  selectedLocation,
  trafficType,
  congestionData,
  velocityData,
  volumeData,
}: any) {
  const renderChart = () => {
    if (isLoading) {
      return (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-center h-64 text-red-500">
            {error}
          </div>
        </div>
      );
    }

    const locationDescription =
      locations.find((loc) => loc.id === selectedLocation)?.description || "";

    if (trafficType === "congestion" && congestionData) {
      return (
        <TrafficChart
          data={congestionData.congestion_per_day}
          color="#f97316"
          title="Tendencia de Congestión"
          subtitle={locationDescription}
        />
      );
    }

    if (trafficType === "velocity" && velocityData) {
      return (
        <TrafficChart
          data={velocityData.velocity_per_day}
          color="#3b82f6"
          title="Tendencia de Velocidad"
          subtitle={locationDescription}
        />
      );
    }

    if (trafficType === "volume" && volumeData) {
      return (
        <TrafficChart
          data={volumeData.volume_per_day}
          color="#10b981"
          title="Tendencia de Volumen"
          subtitle={locationDescription}
        />
      );
    }

    return null;
  };

  return <>{renderChart()}</>;
}
