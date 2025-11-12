//import { useEffect, useRef } from "react";
import { getStatusColor } from "../../utils/trafficUtils";
import { BottleneckData } from "@/types/bottlenecl";
//import { useToast } from "../ui/ToastContainer";

interface TrafficSummaryCardProps {
  location: string;
  camera: string;
  date: string;
  data: BottleneckData;
}

export const TrafficSummaryCard = ({
  location,
  camera,
  date,
  data,
}: TrafficSummaryCardProps) => {
  /*const toast = useToast();
  const firstRender = useRef(true);
  useEffect(() => {
    if (
      (data?.yhat_speed < 0 ||
        data?.yhat_count > 1000 ||
        data?.yhat_count < 0) &&
      firstRender.current
    ) {
      toast.warning(
        "No hay suficientes datos históricos para generar una predicción confiable. Asegúrate de que la cámara tenga datos suficientes y vuelve a intentarlo."
      );
      firstRender.current = false;
    }
  }, [data]);*/

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-1">
            Pronóstico para {date} a las { data?.ds.slice(11, 16)}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span>
              {location} - {camera}
            </span>
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            data?.level === "Fluido"
              ? "bg-green-50 text-green-600"
              : data?.level === "Denso"
              ? "bg-yellow-50 text-yellow-600"
              : "bg-red-50 text-red-600"
          }`}
        >
          {data?.level}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <div
            className={`text-3xl font-semibold ${getStatusColor(data?.level)}`}
          >
            {data?.ds.slice(11, 16)}
          </div>
          <div className="text-sm text-gray-600 mt-1">Hora</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <div
            className={`text-3xl font-semibold ${getStatusColor(data?.level)}`}
          >
            {Math.round(data?.yhat_speed)}
          </div>
          <div className="text-sm text-gray-600 mt-1">km/h estimados</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <div
            className={`text-3xl font-semibold ${getStatusColor(data?.level)}`}
          >
            {Math.round(data?.yhat_count)}
          </div>
          <div className="text-sm text-gray-600 mt-1">vehículos/hora</div>
        </div>
      </div>
    </div>
  );
};
