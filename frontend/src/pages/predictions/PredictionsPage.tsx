import { useState, useEffect } from "react";
import ForecastHeader from "../../components/predictions/ForecastHeader";
import ForecastSummary from "../../components/predictions/ForecastSummery";
import ImpactSection from "../../components/predictions/ImpactSection";
import ComparisonSection from "../../components/predictions/ComparisionSection";
import ForecastChart from "../../components/predictions/ForecastChart";
import { ForecastData, ChangePercent } from "../../types/forecast";
import { trafficService } from "../../services/traffic.service";
import { getForecast } from "../../services/prediction.service";
import { Location } from "../../types/forecast";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { useToast } from "../../components/ui/ToastContainer";

export default function PredictionPage() {
  const toast = useToast();
  const [location, setLocation] = useState(0);
  const [locations, setLocations] = useState<Location[]>([]);
  const [date, setDate] = useState(() => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  });
  const [time, setTime] = useState("08:00");
  const [selectedPeriod, setSelectedPeriod] = useState<
    "daily" | "monthly" | "yearly"
  >("monthly");
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [forecastChangePercent, setForecastChangePercent] =
    useState<ChangePercent>({
      yhat_change: 0,
      trend_change: 0,
    });
  const [loading, setLoading] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);

  useEffect(() => {
    loadLocationData();
  }, []);

  const loadLocationData = async () => {
    const data = await trafficService.getLocations();
    console.log(">>>", data);
    setLocations(data);
  };

  useEffect(() => {
    console.log("Estado:", forecastData);
  }, [forecastData]);

  const validateInputs = () => {
    console.log(date, time, location);
    return date !== "" && time !== "";
  };

  const onForecastCalculation = async () => {
    console.log(">>>Entra");
    setLoading(true);
    try {
      console.log(time);
      const [hour, minute] = time.split(":");
      console.log([hour, minute]);

      if (!validateInputs()) {
        toast.warning("Por favor, complete todos los campos antes de continuar.");
        setLoading(false);
        return;
      }

      const resp = await getForecast(
        location,
        date,
        hour,
        minute,
        selectedPeriod
      );
      console.log(">>>", resp);
      setForecastChangePercent(resp?.variation_forecast_metrics);
      setForecastData([resp]);
      console.log(resp);
      toast.success("Pronóstico generado con éxito.");
    } catch (error) {
      console.error("Error loading forecast data:", error);
      if (error?.response?.status === 400) {
        toast.error(
          error?.response?.data?.error || "Error al obtener el pronóstico."
        );
      } else {
        toast.error("Error inesperado al obtener el pronóstico.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = async (period: "daily" | "monthly" | "yearly") => {
    setLoadingComparison(true);
    setSelectedPeriod(period);
    try {
      const [hour, minute] = time.split(":");
      const resp = await getForecast(location, date, hour, minute, period);
      console.log(">>>", resp);
      setForecastChangePercent(resp?.variation_forecast_metrics);
      console.log(resp);
      toast.success("Periodo de comparación actualizado.");
    } catch (error) {
      toast.error("Error loading forecast data:", error);
    } finally {
      setLoadingComparison(false);
    }

    console.log(">>> period change in page", period);
    console.log("Cambiar periodo");
  };

  const currentForecast = forecastData[0];
  console.log("Forecast Change Percent", forecastChangePercent);
  console.log("Forecast Chart Data", currentForecast?.forecast);

  return (
    <div className="space-y-6">
      <ForecastHeader
        locations={locations}
        location={location}
        date={date}
        time={time}
        onLocationChange={setLocation}
        onDateChange={setDate}
        onTimeChange={setTime}
        onForecastCalculation={onForecastCalculation}
      />

      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-3">
          <LoadingSpinner />
          <div className="text-gray-400">Cargando, espere por favor...</div>
        </div>
      ) : (
        <>
          {currentForecast ? (
            <>
              <ForecastSummary
                locations={locations}
                location={location}
                date={date}
                time={time}
                speed={currentForecast.yhat > 200 ? 27 : 45}
                numberVehicles={currentForecast.yhat}
                confidence={currentForecast.confidenceLevel * 100}
                levelTraffic={currentForecast.levelTraffic}
                factors={currentForecast.holidays_name}
              />

              <div className="grid grid-cols-2 gap-6">
                <ImpactSection
                  holidays_impact={currentForecast?.holidays}
                  seasonality_impact={currentForecast?.seasonality}
                />
                {loadingComparison ? (
                  <LoadingSpinner />
                ) : (
                  <>
                    <ComparisonSection
                      selectedPeriod={selectedPeriod}
                      comparison={forecastChangePercent}
                      onPeriodChange={setSelectedPeriod}
                      handlePeriodChange={handlePeriodChange}
                    />
                  </>
                )}
              </div>

              <ForecastChart data={currentForecast} selectedDate={date} />
            </>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-400">Comienza a predecir...</div>
            </div>
          )}
        </>
      )}

      <div className="bg-blue-50 rounded-lg p-4 text-center">
        <p className="text-sm text-blue-800">
          Proyecto de Gestión de tránsito y predicción vehicular - ©UNEMI 2025
        </p>
      </div>
    </div>
  );
}
