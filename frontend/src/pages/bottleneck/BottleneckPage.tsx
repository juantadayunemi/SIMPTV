import { useState, useEffect } from "react";
import { Camera, Location } from "../../types/forecast";
import { CustomSelect } from "../../components/customerSelect/CustomSelect";
import { QuickDateButtons } from "../../components/botlleneck/QuickDateButtons";
import { TrafficSummaryCard } from "../../components/botlleneck/TrafficSummaryCard";
import { TrafficTable } from "../../components/botlleneck/TrafficTable";
import { getNextDate, getLocalDateString } from "../../utils/dateUtils";
import { filterDataByTime } from "../../utils/trafficUtils";
import {
  getBottleneckData,
  getNotificationBottleneck,
  NotificationBottleneck,
} from "../../services/bottleneck.service";
import { trafficService } from "../../services/traffic.service";
import { useToast } from "../../components/ui/ToastContainer";
import { BottleneckData } from "@/types/bottlenecl";
import TimePicker from "@/components/predictions/TimerPicker";
import SelectDate from "@/components/customerSelect/SelectDate";
import MessageHome from "@/components/botlleneck/MessageHome";
import { LoadingContainer } from "@/components/ui/LoadingContainer";
import { useLocation, useNavigate } from "react-router-dom";
import Modal from "@/components/ui/Modal";
import { NotificationsBottleneck } from "@/components/botlleneck/NotificationsBottleneck";

export default function BottleneckPage() {
  const [bottleneckData, setBottleneckData] = useState<BottleneckData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedCamera, setSelectedCamera] = useState("");
  const [allCameras, setAllCameras] = useState<Camera[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [isNotificationActive, setIsNotificationActive] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const toast = useToast();
  const locationPage = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    loadLocationData();
    loadCameraData();
  }, []);

  useEffect(() => {
    const fetchNotificationStatus = async () => {
      if (selectedLocation && selectedCamera) {
        console.log("Llamar si tiene notificación activa");
        try {
          setIsLoading(true);
          const resp = await getNotificationBottleneck(
            selectedLocation,
            selectedCamera
          );

          console.log("Respuesta de notificación:", resp);
          if (resp.results && resp.results.length > 0) {
            console.log("is_notification_active:", resp.results[0].isActive);
            setIsNotificationActive(resp.results[0].isActive);
          } else {
            setIsNotificationActive(false);
          }
        } catch (error) {
          console.error("Error fetching notification status:", error);
          setIsNotificationActive(false);
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchNotificationStatus();
  }, [selectedLocation, selectedCamera]);

  useEffect(() => {
    const state = locationPage.state as any;
    if (state?.autoLoad && allCameras.length > 0) {
      const cams = filteredCameras(state.locationId);
      setCameras(cams);
      setSelectedLocation(state.locationId);
      setSelectedCamera(state.cameraId);
    }
  }, [allCameras]);

  useEffect(() => {
    const loadData = async () => {
      const state = locationPage.state as any;
      if (state?.autoLoad && state?.locationId && state?.cameraId) {
        try {
          setIsLoading(true);
          await loadLocationData();
          await loadCameraData();

          setSelectedDate(state.date || "");
          setSelectedTime(state.time || "");

          const [hour, minute] = (state.time || "00:00").split(":");

          await loadBottleneckData(
            state.locationId,
            state.cameraId,
            state.date,
            hour,
            minute
          );

          // Limpiar el state para evitar recargas
          window.history.replaceState({}, document.title);
        } catch (err: any) {
          toast.error("Error al cargar la página de embotellamientos");
          navigate("/predictions");
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadData();
  }, [locationPage.state]);

  const loadLocationData = async () => {
    try {
      setIsLoading(true);
      const data = await trafficService.getLocations();

      console.log(">>>", data);
      setLocations(data);
      //setLocation(data.length > 0 ? data[0].id : 0);
    } catch (error) {
      toast.error("Error al cargar las ubicaciones");
    } finally {
      setIsLoading(false);
    }
  };

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

  const loadBottleneckData = async (
    locationId: string,
    cameraId: string,
    date: string,
    hour: string,
    minute: string
  ) => {
    setIsLoading(true);
    try {
      if (!locationId) {
        toast.error("Por favor, seleccione una ubicación.");
        return;
      }
      const data = await getBottleneckData(
        locationId,
        cameraId,
        date,
        hour,
        minute
      );
      console.log("Datos de embotellamiento>>>", data);
      const hasOutOfRange = data.some(
        (row) =>
          row.yhat_count < 0 ||
          row.yhat_count > 1000 ||
          row.yhat_speed < 0 ||
          row.yhat_speed > 1000
      );

      if (hasOutOfRange) {
        setIsOpen(true);
      }

      setBottleneckData(data);

      if (data && data.length > 0) {
        toast.success("Datos cargados con éxito.");
      }
    } catch (err: any) {
      toast.error("Error al cargar los datos del embotellamiento.");
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
    setBottleneckData([]);
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
    setBottleneckData([]);
  };

  const handleDateChange = (value: string) => {
    const today = new Date();
    const todayString = getLocalDateString(today);
    if (value < todayString) {
      toast.warning("La fecha seleccionada no puede ser anterior a hoy.");
      return;
    }
    setSelectedDate(value);
    setSelectedTime("");

    if (value && selectedLocation && selectedCamera) {
      loadBottleneckData(selectedLocation, selectedCamera, value, "0", "0");
    }
  };

  const handleTimeChange = (value: string) => {
    setSelectedTime(value);
  };

  const handleTimeClear = () => {
    setSelectedTime("");
  };

  const handleTodayClick = () => {
    const today = new Date();
    const todayString = getLocalDateString(today);
    setSelectedDate(todayString);
    if (selectedLocation && selectedCamera) {
      loadBottleneckData(
        selectedLocation,
        selectedCamera,
        todayString,
        "0",
        "0"
      );
    }
  };

  const handleTomorrowClick = () => {
    const today = new Date();
    const tomorrow = getNextDate(today);
    setSelectedDate(tomorrow);
    if (selectedLocation && selectedCamera) {
      loadBottleneckData(selectedLocation, selectedCamera, tomorrow, "0", "0");
    }
  };

  const handleCloseReliable = () => {
    setIsOpen(false);
    navigate("/predictions");
  };
  const handleToggleNotification = async () => {
    if (!isNotificationActive) {
      toast.success(
        "Empezarás a recibir notificaciones para esta ubicación y cámara."
      );
    } else {
      toast.info(
        "Desactivaste las notificaciones para esta ubicación y cámara."
      );
    }
    try {
      setIsLoading(true);
      const resp = await NotificationBottleneck(
        selectedLocation,
        selectedCamera
      );
      setIsNotificationActive(!isNotificationActive);
      // sessionStorage.setItem("isNotificationActive", (!isNotificationActive).toString());
      console.log("Notificación respuesta>>>", resp);
    } catch (error) {
      toast.error("Error al actualizar la notificación.");
    } finally {
      setIsLoading(false);
    }
  };

  const canShowQuickButtons = selectedLocation && selectedCamera;
  const shouldShowTable =
    bottleneckData.length > 0 && selectedDate && !selectedTime;
  const shouldShowSummary =
    bottleneckData.length > 0 && selectedDate && selectedTime;

  const selectedLocationName =
    locations.find((l) => l.id === Number(selectedLocation))?.description || "";
  const selectedCameraName =
    allCameras.find((c) => c.id === Number(selectedCamera))?.name || "";

  const currentTimeData = selectedTime
    ? filterDataByTime(bottleneckData, selectedTime)
    : null;
  const clearTime = selectedTime !== "";

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 relative">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-2">
            Pronósticos de Tráfico
          </h2>
          <p className="text-sm text-gray-500 mb-4 sm:mb-6">
            Predicciones basadas en el análisis histórico
          </p>
          {canShowQuickButtons && (
            <div className="absolute top-4 right-4">
              <NotificationsBottleneck
                handleToggleNotification={handleToggleNotification}
                isNotificationActive={isNotificationActive}
              />
            </div>
          )}

          <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4">
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
            <div className="flex-1 min-w-[200px]">
              <CustomSelect
                value={selectedLocation}
                onChange={handleLocationChange}
                options={locations.map((loc) => ({
                  value: loc.id,
                  label: loc.description,
                }))}
                placeholder="Seleccionar ubicación"
              />
            </div>

            {selectedLocation && (
              <div className="flex-1 min-w-[200px]">
                <CustomSelect
                  value={selectedCamera}
                  onChange={handleCameraChange}
                  options={cameras.map((cam) => ({
                    value: cam.id,
                    label: cam.name,
                  }))}
                  placeholder="Seleccionar cámara"
                />
              </div>
            )}

            {selectedCamera && (
              <div className="flex items-center min-w-[200px]">
                <SelectDate
                  date={selectedDate}
                  onDateChange={handleDateChange}
                />
              </div>
            )}

            {selectedDate && bottleneckData.length > 0 && (
              <div className="flex-1 min-w-[200px]">
                <TimePicker
                  time={selectedTime}
                  onTimeChange={handleTimeChange}
                />
              </div>
            )}

            {clearTime && (
              <div className="flex items-center justify-center sm:justify-start min-w-[150px]">
                <button
                  onClick={handleTimeClear}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors w-full sm:w-auto"
                >
                  Limpiar hora
                </button>
              </div>
            )}
          </div>
        </div>

        {canShowQuickButtons && (
          <QuickDateButtons
            onTodayClick={handleTodayClick}
            onTomorrowClick={handleTomorrowClick}
            disabled={!canShowQuickButtons}
          />
        )}

        {!selectedLocation || !selectedCamera ? (
          <MessageHome
            icon="PresentationChartLineIcon"
            placeholder="Selecciona los parámetros para empezar"
          />
        ) : null}

        {isLoading && (
          <LoadingContainer
            type="global"
            loading={isLoading}
            message="Cargando, espere por favor..."
          />
        )}

        {shouldShowSummary && currentTimeData && (
          <TrafficSummaryCard
            location={selectedLocationName}
            camera={selectedCameraName}
            date={selectedDate}
            data={currentTimeData}
          />
        )}

        {shouldShowTable && (
          <TrafficTable
            location={selectedLocationName}
            camera={selectedCameraName}
            date={selectedDate}
            data={bottleneckData}
          />
        )}

        <div className="text-center text-gray-500 text-xs sm:text-sm pt-4">
          Esta predicción de tráfico es útil como referencia, pero no sustituye
          la observación en tiempo real.
        </div>
      </div>
    </div>
  );
}
