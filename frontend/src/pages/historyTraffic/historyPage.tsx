import { useState, useEffect, useRef } from "react";
import DateRangeModal from "../../components/historyTraffic/DateRangeModal";
import { getHistoryTraffic } from "../../services/history.service";
import { getDateRangeFromType } from "../../utils/dateUtils";
import {
  TrafficType,
  DateRangeType,
  DateRange,
  CongestionData,
  VelocityData,
  VolumeData,
} from "../../types/historyTraffic";
import { Camera, Location } from "../../types/forecast";
import { trafficService } from "../../services/traffic.service";
import HistoryHeader from "@/components/historyTraffic/HistoryHeader";
import HistoryChart from "@/components/historyTraffic/HistoryChart";
import { useHandleExport } from "../../utils/exportPdf";
import { useToast } from "../../components/ui/ToastContainer";
import { HistorySummary } from "@/components/historyTraffic/HistorySummary";
import { LoadingContainer } from "@/components/ui/LoadingContainer";
import MessageHome from "@/components/botlleneck/MessageHome";

export default function HistoryTraffic() {
  const toast = useToast();
  const [selectedLocation, setSelectedLocation] = useState<string>("");
  const [locations, setLocations] = useState<Location[]>([]);
  const [allCameras, setAllCameras] = useState<Camera[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState("");
  const [dateRangeType, setDateRangeType] = useState<DateRangeType | null>(null);
  const [customDateRange, setCustomDateRange] = useState<DateRange | null>(null);
  const [trafficType, setTrafficType] = useState<TrafficType | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [congestionData, setCongestionData] = useState<CongestionData | null>(null);
  const [velocityData, setVelocityData] = useState<VelocityData | null>(null);
  const [volumeData, setVolumeData] = useState<VolumeData | null>(null);
  const pageRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    loadLocationsData();
    loadCameraData();
  }, []);

  const loadLocationsData = async () => {
    setIsLoading(true);
    try {
      const data = await trafficService.getLocations();
      setLocations(data);
    } catch (err) {
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

useEffect(() => {
  if (trafficType && selectedLocation && selectedCamera) {
    loadData();
  }
}, [trafficType, selectedLocation, selectedCamera]);
  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let dateRange: DateRange | null = null;

      if (dateRangeType === "custom") {
        if (!customDateRange) {
          setIsLoading(false);
          return;
        }
        dateRange = customDateRange;
      } else {
        dateRange = getDateRangeFromType(dateRangeType);
      }

      if (!dateRange) {
        setIsLoading(false);
        return;
      }

      if (!selectedLocation || !selectedCamera) {
        toast.error("Por favor, seleccione una ubicación y una cámara.");
        return;
      }
      const data = await getHistoryTraffic(
        trafficType,
        selectedLocation,
        selectedCamera,
        dateRange.dateFrom,
        dateRange.dateTo
      );
      console.log("Datos de tráfico>>>", data);

      if (data?.detail) {
        setCongestionData(null);
        setVelocityData(null);
        setVolumeData(null);
        toast.error("No hay datos disponibles para el rango seleccionado.");
        return;
      }

      if (trafficType === "congestion") {
        setCongestionData(data as CongestionData);
      } else if (trafficType === "velocity") {
        setVelocityData(data as VelocityData);
      } else if (trafficType === "volume") {
        setVolumeData(data as VolumeData);
      }
      toast.success("Datos cargados con éxito.");
    } catch (err) {
      if (err instanceof Error) {
        toast.error(err.message);
      }
      setError(
        err instanceof Error ? err.message : "Error al cargar los datos"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDateRangeChange = (value: DateRangeType | null) => {
    setDateRangeType(value);
    setCustomDateRange(null);
    setTrafficType(null);

    if (value === "custom") {
      setIsModalOpen(true);
    } else {
      setCustomDateRange(null);
    }
  };

  const handleCustomDateApply = (dateRange: DateRange) => {
    setCustomDateRange(dateRange);
    setIsModalOpen(false);
  };

  const exportData = useHandleExport(pageRef);
  const onHandleExport = async () => {
    if (!congestionData && !velocityData && !volumeData) {
      toast.error("No hay datos disponibles para exportar.");
      return;
    }
    setIsExporting(true);
    if (isExporting) {
      toast.info("La exportación ya está en curso. Por favor, espere.");
      return;
    }
    try {
      await exportData();
    } catch (error) {
      toast.error(
        "Error durante la exportación: " +
          (error instanceof Error ? error.message : "Desconocido")
      );
    } finally {
      setIsExporting(false);
    }
  };
  const filteredCameras = (value: string) => {
    return allCameras.filter((cam) => cam.locationId === Number(value));
  };

  const handleLocationChange = (value: string) => {
    setSelectedLocation(value);
    setSelectedCamera("");
    setCustomDateRange(null);
    setDateRangeType(null);
    if (value) {
      const cams = filteredCameras(value);
      setCameras(cams);
    }
    setCongestionData(null);
    setVelocityData(null);
    setVolumeData(null);
  };

  const handleCameraChange = (value: string) => {
    setSelectedCamera(value);
    setCustomDateRange(null);
    setDateRangeType(null);
    setCongestionData(null);
    setVelocityData(null);
    setVolumeData(null);
  };

  const handleTrafficTypeChange = (value: TrafficType | null) => {
    setTrafficType(value);
    
  };

  const hasAnyData = !!(congestionData || velocityData || volumeData);
  const hasSelectedBasics = !!(selectedLocation && selectedCamera);
  const shouldShowResults = hasSelectedBasics && !!trafficType && hasAnyData;
  const shouldMessageNoData = hasSelectedBasics && !!trafficType && !hasAnyData && !isLoading;
  const shouldAskToSelect = !hasSelectedBasics;


  return (
    <div className="w-full min-h-screen">
      <HistoryHeader
        locations={locations}
        selectedLocation={selectedLocation}
        handleLocationChange={handleLocationChange}
        cameras={cameras}
        selectedCamera={selectedCamera}
        handleCameraChange={handleCameraChange}
        trafficType={trafficType}
        dateRangeType={dateRangeType}
        setTrafficType={handleTrafficTypeChange}
        handleDateRangeChange={handleDateRangeChange}
        onHandleExport={onHandleExport}
        isExporting={isExporting}
        shouldShowResults={shouldShowResults}
      />

      <DateRangeModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          if (!customDateRange) setDateRangeType("7days");
        }}
        onApply={handleCustomDateApply}
      />

      {isLoading && (
        <LoadingContainer
          type="global"
          loading={isLoading}
          message="Cargando, espere por favor..."
        />
      )}

      {shouldAskToSelect && (
        <MessageHome
          icon="PresentationChartLineIcon"
          placeholder="Selecciona los parámetros para empezar"
        />
      )}

      {shouldMessageNoData && (
        <MessageHome
          icon="DocumentMagnifyingGlassIcon"
          placeholder="No hay datos disponibles para el rango seleccionado."
        />
      )}

      {shouldShowResults && (
        <div ref={pageRef} className="w-full mx-auto py-6 space-y-6">
          <HistorySummary
            trafficType={trafficType}
            congestionData={congestionData}
            velocityData={velocityData}
            volumeData={volumeData}
          />

          <div className="w-full bg-white rounded-lg shadow-sm p-6">
            <HistoryChart
              isLoading={isLoading}
              error={error}
              locations={locations}
              selectedLocation={selectedLocation}
              trafficType={trafficType}
              congestionData={congestionData}
              velocityData={velocityData}
              volumeData={volumeData}
            />
          </div>
        </div>
      )}
    </div>
  );
}