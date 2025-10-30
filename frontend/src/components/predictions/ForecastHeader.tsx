import { Calendar } from "lucide-react";
import { useEffect } from "react";
import TimePicker  from '../../components/predictions/TimerPicker';

interface ForecastHeaderProps {
  locations: [];
  location: number;
  date: string;
  time: string;
  onLocationChange: (location: number) => void;
  onDateChange: (date: string) => void;
  onTimeChange: (time: string) => void;
  onForecastCalculation: () => void;
}

export default function ForecastHeader({
  locations,
  location,
  date,
  time,
  onLocationChange,
  onDateChange,
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
        <div className="flex items-center gap-2 flex-1 w-full sm:w-auto">
          <select
            value={location}
            onChange={(e) => onLocationChange(e.target.value)}
            className="flex-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {locations.map((element) => (
              <option key={element?.id} value={element?.id}>
                {element?.description}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Calendar size={20} className="text-gray-400 flex-shrink-0" />
          <input
            type="date"
            value={date}
            onChange={(e) => onDateChange(e.target.value)}
            className="flex-1 sm:flex-none px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <TimePicker time={time} onTimeChange={onTimeChange}/>
        </div>

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