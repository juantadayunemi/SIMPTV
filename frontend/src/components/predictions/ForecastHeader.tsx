import { useEffect } from "react";
import TimePicker from "../../components/predictions/TimerPicker";
import { CustomSelect } from "../customerSelect/CustomSelect";
import SelectDate from "../customerSelect/SelectDate";
import { Location,Camera } from "@/types/forecast";

interface ForecastHeaderProps {
  locations: Location[];
  selectedLocation: string;
  cameras: Camera[];
  selectedCamera: string;
  selectedDate: string;
  selectedTime: string;
  handleLocationChange: (selectedLocation: string) => void;
  handleCameraChange: (selectedCamera: string) => void;
  handleDateChange: (selectedDate: string) => void;
  onTimeChange: (selectedTime: string) => void;
  onForecastCalculation: () => void;
}

export default function ForecastHeader({
  locations,
  selectedLocation,
  cameras,
  selectedCamera,
  selectedDate,
  selectedTime,
  handleLocationChange,
  handleCameraChange,
  handleDateChange,
  onTimeChange,
  onForecastCalculation,
}: ForecastHeaderProps) {
  useEffect(() => {}, []);

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-2">
        Pronósticos de Tráfico
      </h2>
      <p className="text-sm text-gray-500 mb-4 sm:mb-6">
        Predicciones basadas en el análisis histórico
      </p>

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
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <SelectDate date={selectedDate} onDateChange={handleDateChange} />
          </div>
        )}

        {selectedDate && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <TimePicker time={selectedTime} onTimeChange={onTimeChange} />
          </div>
        )}

        <button
          onClick={() => onForecastCalculation()}
          className="w-full sm:w-auto bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Calcular
        </button>
      </div>
    </div>
  );
}
