import React from 'react';
import { Car, Truck, Bike, Bus, TrendingUp, Clock, MapPin } from 'lucide-react';
import type { ProcessingComplete } from '../../services/websocket.service';

interface AnalysisResultsProps {
  results: ProcessingComplete | null;
  analysisId: number | null;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  results,
  analysisId,
}) => {
  if (!results) {
    return null;
  }

  const vehicleTypeIcons: Record<string, React.ReactNode> = {
    car: <Car className="h-5 w-5" />,
    truck: <Truck className="h-5 w-5" />,
    motorcycle: <Bike className="h-5 w-5" />,
    bus: <Bus className="h-5 w-5" />,
  };

  const vehicleCounts = results.stats?.vehicle_counts || {};
  const totalVehicles = Object.values(vehicleCounts).reduce(
    (sum: number, count) => sum + (count as number),
    0
  );

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Vehicles</p>
              <p className="text-3xl font-bold text-gray-900">{totalVehicles}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <Car className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Processing Time</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatDuration(results.processing_time)}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <Clock className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Analysis ID</p>
              <p className="text-3xl font-bold text-gray-900">#{analysisId}</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Vehicle Type Breakdown */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Vehicle Type Distribution
        </h3>

        <div className="space-y-4">
          {Object.entries(vehicleCounts).map(([type, count]) => {
            const percentage =
              totalVehicles > 0 ? ((count as number) / totalVehicles) * 100 : 0;

            return (
              <div key={type}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="text-gray-600">
                      {vehicleTypeIcons[type] || <Car className="h-5 w-5" />}
                    </div>
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {type}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">
                      {percentage.toFixed(1)}%
                    </span>
                    <span className="text-sm font-semibold text-gray-900">
                      {count as number}
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Additional Stats */}
      {results.stats && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Detailed Statistics
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-xs text-gray-600">Total Frames</p>
              <p className="text-xl font-bold text-gray-900">
                {results.stats.total_frames || 0}
              </p>
            </div>

            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-xs text-gray-600">Processed Frames</p>
              <p className="text-xl font-bold text-gray-900">
                {results.stats.processed_frames || 0}
              </p>
            </div>

            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-xs text-gray-600">Unique Vehicles</p>
              <p className="text-xl font-bold text-gray-900">
                {results.stats.unique_vehicles || 0}
              </p>
            </div>

            <div className="border-l-4 border-yellow-500 pl-4">
              <p className="text-xs text-gray-600">Video FPS</p>
              <p className="text-xl font-bold text-gray-900">
                {results.stats.video_fps || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={() =>
            (window.location.href = `/traffic/analysis/${analysisId}/details`)
          }
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 font-medium"
        >
          View Detailed Report
        </button>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-3 border border-gray-300 rounded-md hover:bg-gray-50 font-medium text-gray-700"
        >
          New Analysis
        </button>
      </div>
    </div>
  );
};
