import { useState, useEffect, useMemo } from "react";
import ForecastHeader from "../../components/predictions/ForecastHeader";
import ForecastSummary from "../../components/predictions/ForecastSummery";
import ImpactSection from "../../components/predictions/ImpactSection";
import ComparisonSection from "../../components/predictions/ComparisionSection";
import ForecastChart from "../../components/predictions/ForecastChart";
import { ForecastData, ChangePercent, ForecastDataSpeed } from "../../types/forecast";
import { trafficService } from "../../services/traffic.service";
import { getForecast, getForecastSpeed } from "../../services/prediction.service";
import { Location } from "../../types/forecast";
import { useToast } from "../../components/ui/ToastContainer";
import { getNextDate } from "../../utils/dateUtils";
import { LoadingContainer } from "@/components/ui/LoadingContainer";

export default function PredictionPage() {
  const toast = useToast();
  const [location, setLocation] = useState(0);
  const [locations, setLocations] = useState<Location[]>([]);
  const [date, setDate] = useState(() => {
    const today = new Date();
    return getNextDate(today);
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
  const [forecastSpeedData, setForecastSpeedData] = useState<ForecastDataSpeed[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const currentForecast = useMemo(() => forecastData[0], [forecastData]);

  useEffect(() => {
    loadLocationData();
  }, []);

  const loadLocationData = async () => {
    try {
      const data = await trafficService.getLocations();
      console.log(">>>", data);
      setLocations(data);
      setLocation(data.length > 0 ? data[0].id : 0);
    } catch (error) {
      toast.error("Error al cargar las ubicaciones");
      console.error("Error loading locations:", error);
    }
  };

  useEffect(() => {
    console.log("Estado:", forecastData);
  }, [forecastData]);

  const validateInputs = () => {
    console.log(date, time, location);
    return date !== "" && time !== "";
  };

  const onForecastCalculation =async () => {
    setLoading(true);
    try {
      const [hour, minute] = time.split(":");

      if (!validateInputs()) {
        toast.warning(
          "Por favor, complete todos los campos antes de continuar."
        );
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
      
      const respSpeed = await getForecastSpeed(
        location,
        date,
        hour,
        minute
      );  

      console.log(">>>", respSpeed);
      setForecastSpeedData([respSpeed]);

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

  //const currentForecast = forecastData[0];
  const currentForecastSpeed = forecastSpeedData[0];
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
        <LoadingContainer
          type="section"
          loading={loading}
          message="Cargando, espere por favor..."
        />
      ) : (
        <>
          {currentForecast ? (
            <>
              <ForecastSummary
                locations={locations}
                location={location}
                date={date}
                time={time}
                speed={currentForecastSpeed?.yhat_speed}
                numberVehicles={currentForecast?.yhat}
                confidence={currentForecast?.confidenceLevel}
                levelTraffic={currentForecast?.levelTraffic}
                factors={currentForecast?.holidays_name}
              />

              <div className="grid grid-cols-2 gap-6">
                <ImpactSection
                  holidays_impact={currentForecast?.holidays}
                  seasonality_impact={currentForecast?.seasonality}
                />
                {loadingComparison ? (
                  <LoadingContainer
                    type="global"
                    loading={loadingComparison}
                    message="Cargando, espere por favor..."
                  />
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

              <ForecastChart data={currentForecast?.forecast} selectedDate={date} />
            </>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-400">Comienza a predecir...</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
