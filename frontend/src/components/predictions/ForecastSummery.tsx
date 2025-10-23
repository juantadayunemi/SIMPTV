import { Location } from "../../types/forecast";

interface ForecastSummaryProps {
  locations: Location[];
  location: string;
  date: string;
  time: string;
  speed: number;
  numberVehicles: number;
  confidence: number;
  levelTraffic: string;
  factors: string;
}

export default function ForecastSummary({
  locations,
  location,
  date,
  time,
  speed,
  numberVehicles,
  confidence,
  levelTraffic,
  factors,
}: ForecastSummaryProps) {
  const getStatus = () => {
    if (levelTraffic == "Alto")
      return { label:levelTraffic , color: "text-red-600 bg-red-100" };
    if (levelTraffic == "Medio")
      return { label: levelTraffic, color: "text-orange-600 bg-orange-100" };
    return { label: levelTraffic, color: "text-green-600 bg-green-100" };
  };

  const status = getStatus();
  const locationFilter = locations.find((x) => x.id === Number(location));

  console.log("Location: ", locationFilter);
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-1">
            Pronóstico para {date} a las {time}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span>{locationFilter?.description}</span>
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${status.color}`}
        >
          {status.label}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-blue-600">{speed}</div>
          <div className="text-sm text-gray-600 mt-1">km/h estimados</div>
        </div>

        <div className="bg-orange-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-600">
            {Math.round(numberVehicles)}
          </div>
          <div className="text-sm text-gray-600 mt-1">vehículos/hora</div>
        </div>

        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-600">{confidence}%</div>
          <div className="text-sm text-gray-600 mt-1">nivel de confianza</div>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-600">Factores Considerados:</span>
          <span className="text-sm font-medium text-gray-800">
            {confidence}%
          </span>
        </div>
        <div className="flex gap-2 mb-2">
          <span className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
            {factors}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-orange-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${confidence}%` }}
          ></div>
        </div>
        <div className="text-xs text-gray-500 mt-1">Nivel de Confianza</div>
      </div>
    </div>
  );
}
