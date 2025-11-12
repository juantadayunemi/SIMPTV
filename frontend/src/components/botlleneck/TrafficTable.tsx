import { TrendingUp } from 'lucide-react';
import { generateTimeSlots } from '../../utils/trafficUtils';
import { getStatusColor } from '../../utils/trafficUtils';
import { BottleneckData } from '@/types/bottlenecl';

interface TrafficTableProps {
  location: string;
  camera: string;
  date: string;
  data: BottleneckData[];
}

export const TrafficTable = ({ location, camera, date, data }: TrafficTableProps) => {
  const timeSlots = generateTimeSlots();

  const getDataForTime = (time: string): BottleneckData | null => {
    return data.find(item => item.ds.slice(11, 16) === time) || null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-1">
          {location} - {date}
        </h3>
        <p className="text-sm text-gray-500">{camera}</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Hora</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Velocidad Promedio</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Cantidad</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Estado</th>
            </tr>
          </thead>
          <tbody>
            {timeSlots.map((time) => {
              const rowData = getDataForTime(time);
              return (
                <tr key={time} className="border-b border-gray-100 hover:bg-gray-100 transition-colors">
                  <td className="py-3 px-4 text-gray-900">{time}</td>
                  <td className="py-3 px-4">
                    {rowData ? (
                      <div className="flex items-center gap-2">
                        <TrendingUp className={`w-4 h-4 `} />{/*${getStatusColor(rowData.level)}*/}
                        <span > {/*className={`${getStatusColor(rowData.level)}`*/}
                          {Math.round(rowData.yhat_speed)} km/h
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-300">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {rowData ? (
                      <div className="flex items-center gap-2">
                        <TrendingUp className={`w-4 h-4 `} />{/*${getStatusColor(rowData.level)}*/}
                        <span > {/*className={`${getStatusColor(rowData.level)}`*/}
                          {Math.round(rowData.yhat_count)} vehículos
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-300">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {rowData ? (
                      <span className={`${getStatusColor(rowData.level)}`}>
                        {rowData.level}
                      </span>
                    ) : (
                      <span className="text-gray-300">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
