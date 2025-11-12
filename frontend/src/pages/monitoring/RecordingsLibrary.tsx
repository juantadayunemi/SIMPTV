/**
 * RecordingsLibrary Page
 * View and manage saved recordings from AWS S3
 */
import React, { useState, useEffect } from 'react';
import { Video, Download, Calendar, HardDrive, AlertCircle } from 'lucide-react';
import * as streamingService from '../../services/streamingService';

export const RecordingsLibrary = () => {
  const [recordings, setRecordings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecordings();
  }, []);

  const loadRecordings = async () => {
    try {
      setLoading(true);
      const response = await streamingService.getRecordings();
      
      if (response.success) {
        setRecordings(response.recordings);
      } else {
        setError('Failed to load recordings');
      }
    } catch (err: any) {
      console.error('Error loading recordings:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs}h ${mins}m ${secs}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando grabaciones...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Video className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Biblioteca de Grabaciones</h1>
                <p className="text-sm text-gray-600">
                  {recordings.length} grabación{recordings.length !== 1 ? 'es' : ''} guardada{recordings.length !== 1 ? 's' : ''} en AWS S3
                </p>
              </div>
            </div>
            <button
              onClick={loadRecordings}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Actualizar
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Error: {error}</span>
            </div>
          </div>
        )}

        {/* Recordings Grid */}
        {recordings.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <Video className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay grabaciones</h3>
            <p className="text-gray-600">
              Las grabaciones aparecerán aquí después de usar el monitoreo en vivo
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recordings.map((recording: any) => (
              <div
                key={recording.recording_id}
                className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Video Placeholder */}
                <div className="aspect-video bg-gray-900 flex items-center justify-center">
                  <Video className="w-16 h-16 text-gray-600" />
                </div>

                {/* Recording Info */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="font-semibold text-gray-900 truncate">
                      {recording.camera_id}
                    </h3>
                    <p className="text-xs text-gray-500 font-mono">
                      {recording.recording_id}
                    </p>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center text-gray-600">
                      <Calendar className="w-4 h-4 mr-2" />
                      {formatDate(recording.start_time)}
                    </div>
                    
                    <div className="flex items-center text-gray-600">
                      <HardDrive className="w-4 h-4 mr-2" />
                      {formatFileSize(recording.file_size)} · {formatDuration(recording.duration)}
                    </div>

                    <div className="flex items-center text-blue-600">
                      <span className="text-xs font-semibold">
                        🚗 {recording.detections_count} detecciones
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-3 border-t border-gray-200">
                    <a
                      href={recording.s3_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center space-x-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      <Download className="w-4 h-4" />
                      <span>Descargar</span>
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecordingsLibrary;
