import { useState, useEffect, useMemo } from "react";
import ForecastHeader from "../../components/predictions/ForecastHeader";
import ForecastSummary from "../../components/predictions/ForecastSummery";
import ImpactSection from "../../components/predictions/ImpactSection";
import ComparisonSection from "../../components/predictions/ComparisionSection";
import ForecastChart from "../../components/predictions/ForecastChart";
import {
  ForecastData,
  ChangePercent,
  ForecastDataSpeed,
  Camera,
  LevelTrafficData,
} from "../../types/forecast";
import { trafficService } from "../../services/traffic.service";
import {
  getForecast,
  getForecastSpeed,
  getLevelTraffic,
} from "../../services/prediction.service";
import { Location } from "../../types/forecast";
import { useToast } from "../../components/ui/ToastContainer";
//import { getNextDate } from "../../utils/dateUtils";
import { LoadingContainer } from "@/components/ui/LoadingContainer";
import MessageHome from "@/components/botlleneck/MessageHome";
import Modal from "@/components/ui/Modal";
import { useNavigate } from "react-router-dom";

export default function PredictionPage() {
  const toast = useToast();
  const [selectedLocation, setSelectedLocation] = useState("");
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedCamera, setSelectedCamera] = useState("");
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [allCameras, setAllCameras] = useState<Camera[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("08:00");
  const [selectedPeriod, setSelectedPeriod] = useState<
    "daily" | "monthly" | "yearly"
  >("monthly");
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [levelTrafficData, setLevelTrafficData] =
    useState<LevelTrafficData | null>(null);
  const [forecastChangePercent, setForecastChangePercent] =
    useState<ChangePercent>({
      yhat_change: 0,
      trend_change: 0,
    });
  const [forecastSpeedData, setForecastSpeedData] = useState<
    ForecastDataSpeed[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const currentForecast = useMemo(() => forecastData[0], [forecastData]);
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadLocationData();
    loadCameraData();
  }, []);

  const loadCameraData = async () => {
    try {
      const data = await trafficService.getCameras();
      console.log("Cámaras>>>", data);

      if (data.length > 0) {
        setAllCameras(data);
      }
    } catch (error) {
      toast.error("Error al cargar las cámaras");
    }
  };

  const loadLocationData = async () => {
    try {
      const data = await trafficService.getLocations();
      setLocations(data);
    } catch (error) {
      toast.error("Error al cargar las ubicaciones");
    }
  };

  const validateInputs = () => {
    return (
      selectedDate !== "" &&
      selectedTime !== "" &&
      selectedLocation !== "" &&
      selectedCamera !== ""
    );
  };

  const onForecastCalculation = async () => {
    setIsLoading(true);
    try {
      const [hour, minute] = selectedTime.split(":");
      if (hour === undefined || minute === undefined) {
        toast.warning("Por favor, seleccione una hora válida.");
        setIsLoading(false);
        return;
      }

      if (!selectedLocation) {
        toast.warning("Por favor, seleccione una localidad.");
        setIsLoading(false);
        return;
      }
      if (!validateInputs()) {
        toast.warning(
          "Por favor, complete todos los campos antes de continuar."
        );
        setIsLoading(false);
        return;
      }

      const resp = await getForecast(
        selectedLocation,
        selectedCamera,
        selectedDate,
        hour,
        minute,
        selectedPeriod
      );

      const respSpeed = await getForecastSpeed(
        selectedLocation,
        selectedCamera,
        selectedDate,
        hour,
        minute
      );

      const levelTrafficData = await getLevelTraffic(
        selectedLocation,
        selectedCamera,
        resp?.yhat,
        respSpeed?.yhat_speed
      );

      if (resp.is_reliable===false || respSpeed.is_reliable===false) {
        setIsOpen(true);
      }

      console.log("Level Traffic Data: ", levelTrafficData);
      setLevelTrafficData(levelTrafficData);

      setForecastSpeedData([respSpeed]);

      setForecastChangePercent(resp?.variation_forecast_metrics);
      setForecastData([resp]);

      if (isOpen) toast.success("Pronóstico generado con éxito.");

    } catch (error) {
      if (error?.response?.status === 400) {
        toast.error(
          error?.response?.data?.error || "Error al obtener el pronóstico."
        );
      } else {
        toast.error("Error inesperado al obtener el pronóstico.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseReliable = () => {
    setIsOpen(false);
    navigate("/dashboard");
  };

  const handlePeriodChange = async (period: "daily" | "monthly" | "yearly") => {
    setIsLoading(true);
    setSelectedPeriod(period);
    try {
      if (!selectedLocation) {
        toast.warning("Por favor, seleccione una localidad.");
        setIsLoading(false);
        return;
      }
      const [hour, minute] = selectedTime.split(":");
      const resp = await getForecast(
        selectedLocation,
        selectedCamera,
        selectedDate,
        hour,
        minute,
        period
      );
      setForecastChangePercent(resp?.variation_forecast_metrics);
      toast.success("Periodo de comparación actualizado.");
    } catch (error) {
      toast.error("Error loading forecast data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredCameras = (value: string) => {
    return allCameras.filter((cam) => cam.locationId === Number(value));
  };

  const handleLocationChange = (value: string) => {
    setSelectedLocation(value);
    setSelectedCamera("");
    setSelectedDate("");
    setSelectedTime("");
    setForecastData([]);
    setCameras([]);

    if (value) {
      const cams = filteredCameras(value);
      setCameras(cams);
    }
  };
  const handleCameraChange = (value: string) => {
    setSelectedCamera(value);
    setSelectedDate("");
    setSelectedTime("");
    setForecastData([]);
  };
  const handleDateChange = (value: string) => {
    setSelectedDate(value);
    setSelectedTime("");
  };

  const currentForecastSpeed = forecastSpeedData[0];
  const shouldShowResults =
    forecastData.length > 0 &&
    levelTrafficData?.level &&
    selectedLocation &&
    selectedCamera &&
    selectedDate &&
    selectedTime;

  return (
    <div className="space-y-6">
      <ForecastHeader
        locations={locations}
        selectedLocation={selectedLocation}
        cameras={cameras}
        selectedCamera={selectedCamera}
        selectedDate={selectedDate}
        selectedTime={selectedTime}
        handleLocationChange={handleLocationChange}
        handleCameraChange={handleCameraChange}
        handleDateChange={handleDateChange}
        onTimeChange={setSelectedTime}
        onForecastCalculation={onForecastCalculation}
      />
      <Modal
        isOpen={isOpen}
        onClose={handleCloseReliable}
        onApply={() => {
          setIsOpen(false);
        }}
        closeText="Regresar"
        applyText="Continuar"
        buttonClose={true}  
        buttonApply={true}
        placeholder="La ubicación seleccionada tiene pocos datos históricos por lo que puede haber inexactitudes en el pronóstico. ¿Desea continuar?"
        type="warning"
      />

      {isLoading && (
        <LoadingContainer
          type="global"
          loading={isLoading}
          message="Cargando, espere por favor..."
        />
      )}

      {!shouldShowResults && (
        <MessageHome
          icon="PresentationChartLineIcon"
          placeholder="Selecciona los parámetros y haz clic en 'Calcular' para ver los resultados."
        />
      )}

      {shouldShowResults && (
        <>
          <ForecastSummary
            locations={locations}
            selectedLocation={selectedLocation}
            selectedDate={selectedDate}
            selectedCamera={selectedCamera}
            selectedTime={selectedTime}
            speed={currentForecastSpeed?.yhat_speed}
            numberVehicles={currentForecast?.yhat}
            confidence={currentForecast?.confidenceLevel}
            level={levelTrafficData?.level || "Sin datos"}
            factors={currentForecast?.holidays_name}
          />

          <div className="grid grid-cols-2 gap-6">
            <ImpactSection
              holidays_impact={currentForecast?.holidays}
              seasonality_impact={currentForecast?.seasonality}
            />

            <>
              <ComparisonSection
                selectedPeriod={selectedPeriod}
                comparison={forecastChangePercent}
                onPeriodChange={setSelectedPeriod}
                handlePeriodChange={handlePeriodChange}
              />
            </>
          </div>

          <ForecastChart
            data={currentForecast?.forecast}
            selectedDate={selectedDate}
          />
        </>
      )}
    </div>
  );
}
