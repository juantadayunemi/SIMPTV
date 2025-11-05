import { DateRangeType, TrafficType } from "../../types/historyTraffic";
import { CustomSelect } from "../customerSelect/CustomSelect";
import { Camera, Location } from "@/types/forecast";
import { Download } from "lucide-react";

export interface HistoryHeaderProps {
  locations: Location[];
  selectedLocation: string;
  handleLocationChange: (selectedLocation: string) => void;
  cameras: Camera[];
  selectedCamera: string;
  handleCameraChange: (selectedCamera: string) => void;
  trafficType: TrafficType | null;
  dateRangeType: DateRangeType | null;
  setTrafficType: (type: TrafficType | null) => void;
  handleDateRangeChange: (type: DateRangeType | null) => void;
  onHandleExport: () => void;
  isExporting: boolean;
  shouldShowResults: boolean;
}
export default function HistoryHeader({
  locations,
  selectedLocation,
  handleLocationChange,
  cameras,
  selectedCamera,
  handleCameraChange,
  trafficType,
  dateRangeType,
  setTrafficType,
  handleDateRangeChange,
  onHandleExport,
  isExporting,
  shouldShowResults

}: HistoryHeaderProps) {
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
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
          <div className="flex-1 w-full sm:w-auto">
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
            <div className="flex-1 w-full sm:w-auto">
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
            <div className="flex-1 w-full sm:w-auto">
              <CustomSelect
                value={dateRangeType}
                onChange={handleDateRangeChange}
                options={[
                  { value: "today", label: "Hoy" },
                  { value: "7days", label: "Últimos 7 días" },
                  { value: "30days", label: "Últimos 30 días" },
                  { value: "custom", label: "Personalizar" },
                ]}
                placeholder="Seleccionar rango de fechas"
              />
            </div>
          )}

          {dateRangeType && (
            <div className="flex-1 w-full sm:w-auto">
              <CustomSelect
                value={trafficType}
                onChange={setTrafficType}
                options={[
                  { value: "congestion", label: "Congestión" },
                  { value: "velocity", label: "Velocidad" },
                  { value: "volume", label: "Volumen" },
                ]}
                placeholder="Seleccionar tipo de tráfico"
              />
            </div>
          )}
          {shouldShowResults && (
            <button
              className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={() => onHandleExport()}
              disabled={isExporting}
            >
              {isExporting ? (
                <div className="w-4 h-4 animate-spin border-b-2 border-white rounded-full"></div>
              ) : (
                <Download className="w-4 h-4" />
              )}
              {isExporting ? "Exportando" : "Exportar"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
