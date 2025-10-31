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
  OptionsType,
} from "../../types/historyTraffic";
import { Location } from "../../types/forecast";
import { trafficService } from "../../services/traffic.service";
import HistoryHeader from "@/components/historyTraffic/HistoryHeader";
import HistoryChart from "@/components/historyTraffic/HistoryChart";
import { handleExport, useHandleExport } from "../../utils/exportPdf";
import { useToast } from "../../components/ui/ToastContainer";
import { HistorySummary } from "@/components/historyTraffic/HistorySummary";
import { LoadingContainer } from "@/components/ui/LoadingContainer";

export default function HistoryTraffic() {
  const toast = useToast();
  const [selectedLocation, setSelectedLocation] = useState(0);
  const [locations, setLocations] = useState<Location[]>([]);
  const [dateRangeType, setDateRangeType] = useState<DateRangeType>("7days");
  const [customDateRange, setCustomDateRange] = useState<DateRange | null>(
    null
  );
  const [trafficType, setTrafficType] = useState<TrafficType>("congestion");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [locationsLoading, setLocationsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [congestionData, setCongestionData] = useState<CongestionData | null>(
    null
  );
  const [velocityData, setVelocityData] = useState<VelocityData | null>(null);
  const [volumeData, setVolumeData] = useState<VolumeData | null>(null);
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadLocationsData();
  }, []);

  const loadLocationsData = async () => {
    setLocationsLoading(true);
    try {
      const data = await trafficService.getLocations();
      setLocations(data);
      console.log("Locations loaded:", data);
    } catch (err) {
      toast.error("Error al cargar las ubicaciones");
      console.error("Error al cargar las ubicaciones:", err);
    } finally {
      setLocationsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedLocation, dateRangeType, customDateRange, trafficType]);

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

      console.log("dateRange:", dateRangeType);
      console.log("->> selectedLocation:", selectedLocation);
      const data = await getHistoryTraffic(
        trafficType,
        selectedLocation,
        dateRange.dateFrom,
        dateRange.dateTo
      );

      console.log(">>>", data);
      if (data || data?.detail) {
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

  const handleDateRangeChange = (value: string) => {
    const newDateRangeType = value as DateRangeType;
    setDateRangeType(newDateRangeType);

    if (newDateRangeType === "custom") {
      setIsModalOpen(true);
    } else {
      setCustomDateRange(null);
    }
  };

  const handleCustomDateApply = (dateRange: DateRange) => {
    setCustomDateRange(dateRange);
    setIsModalOpen(false);
  };

  const onHandleExport = useHandleExport(pageRef);

  return (
    <div className=" w-full min-h-screen">
      <HistoryHeader
        locations={locations}
        trafficType={trafficType}
        selectedLocation={selectedLocation}
        setSelectedLocation={setSelectedLocation}
        dateRangeType={dateRangeType}
        setTrafficType={setTrafficType}
        handleDateRangeChange={handleDateRangeChange}
        onExportClick={onHandleExport}
      />
      {locationsLoading || isLoading ? (
        <LoadingContainer
          type="section"
          loading={isLoading}
          message="Cargando, espere por favor..."
        />
      ) : (
        <div ref={pageRef} className="w-full mx-auto py-6 space-y-6">
          <HistorySummary
            trafficType={trafficType}
            congestionData={congestionData}
            velocityData={velocityData}
            volumeData={volumeData}
          />

          <DateRangeModal
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              if (!customDateRange) setDateRangeType("7days");
            }}
            onApply={handleCustomDateApply}
          />

          {congestionData || velocityData || volumeData ? (
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
          ) : (
            <div className="w-full p-6 flex flex-col items-center justify-center h-64 space-y-3">
              <div className="text-gray-400">
                No hay datos disponibles para el rango seleccionado.
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
