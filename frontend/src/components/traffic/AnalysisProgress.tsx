import React from 'react';
import { CheckCircle, AlertCircle, Loader2, Car, Clock } from 'lucide-react';
import type { ProgressUpdate, LogMessage } from '../../services/websocket.service';

interface AnalysisProgressProps {
  progress: ProgressUpdate | null;
  logs: LogMessage[];
  isProcessing: boolean;
  isComplete: boolean;
  hasError: boolean;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  progress,
  logs,
  isProcessing,
  isComplete,
  hasError,
}) => {
  const getStatusColor = () => {
    if (hasError) return 'text-red-600';
    if (isComplete) return 'text-green-600';
    if (isProcessing) return 'text-blue-600';
    return 'text-gray-600';
  };

  const getStatusIcon = () => {
    if (hasError) return <AlertCircle className="h-6 w-6" />;
    if (isComplete) return <CheckCircle className="h-6 w-6" />;
    if (isProcessing) return <Loader2 className="h-6 w-6 animate-spin" />;
    return null;
  };

  const getStatusText = () => {
    if (hasError) return 'Error in processing';
    if (isComplete) return 'Analysis complete';
    if (isProcessing) return 'Processing video...';
    return 'Ready';
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 space-y-6">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={getStatusColor()}>{getStatusIcon()}</div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {getStatusText()}
            </h3>
            {progress && (
              <p className="text-sm text-gray-600">{progress.status}</p>
            )}
          </div>
        </div>

        {progress && (
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">
              {progress.percentage.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500">
              {progress.processed_frames} / {progress.total_frames} frames
            </p>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {progress && (
        <div className="space-y-2">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                hasError
                  ? 'bg-red-500'
                  : isComplete
                  ? 'bg-green-500'
                  : 'bg-blue-500'
              }`}
              style={{ width: `${progress.percentage}%` }}
            />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="flex items-center gap-2 text-sm">
              <Car className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">Vehicles:</span>
              <span className="font-semibold text-gray-900">
                {progress.vehicles_detected}
              </span>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">FPS:</span>
              <span className="font-semibold text-gray-900">
                {progress.total_frames > 0
                  ? ((progress.processed_frames / progress.total_frames) * 30).toFixed(1)
                  : '0'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Logs */}
      {logs.length > 0 && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Processing Logs
          </h4>
          <div className="bg-gray-50 rounded-md p-3 max-h-48 overflow-y-auto space-y-1">
            {logs.slice(-10).map((log, index) => (
              <div
                key={index}
                className={`text-xs font-mono flex items-start gap-2 ${
                  log.level === 'error'
                    ? 'text-red-600'
                    : log.level === 'warning'
                    ? 'text-yellow-600'
                    : 'text-gray-600'
                }`}
              >
                <span className="text-gray-400">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="flex-1">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
