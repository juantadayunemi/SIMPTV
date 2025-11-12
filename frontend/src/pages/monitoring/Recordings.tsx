/**
 * Recordings Page
 * Display and manage saved video recordings with detections
 */
import { useEffect, useState } from 'react';
import { Play, Download, Calendar, Clock, Eye, Car, Truck, Bus, Bike, Trash2, X, AlertTriangle } from 'lucide-react';
import * as streamingService from '../../services/streamingService';
import { toast } from 'react-hot-toast';

interface Recording {
  recording_id: string;
  camera_id: string;
  video_url: string;
  filename: string;
  duration: number;
  total_detections?: number;
  stats?: Record<string, number>;
  file_size: number;
  status: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
}

export const Recordings = () => {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [recordingToDelete, setRecordingToDelete] = useState<Recording | null>(null);

  useEffect(() => {
    loadRecordings();
  }, []);

  const loadRecordings = async () => {
    try {
      setLoading(true);
      const data = await streamingService.getCompletedRecordings();
      console.log('📹 Recordings data:', data);
      setRecordings(data.recordings || []);
    } catch (error) {
      console.error('❌ Error loading recordings:', error);
      toast.error('Error cargando grabaciones');
    } finally {
      setLoading(false);
    }
  };

  const handleVisualize = (recording: Recording) => {
    setSelectedRecording(recording);
    setShowModal(true);
  };

  const handleDownload = (recording: Recording) => {
    const link = document.createElement('a');
    link.href = recording.video_url;
    link.download = recording.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success(`Descargando ${recording.filename}`);
  };

  const handleDelete = (recording: Recording) => {
    setRecordingToDelete(recording);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!recordingToDelete) return;

    const loadingToast = toast.loading('Eliminando grabación...');
    
    try {
      await streamingService.deleteRecording(recordingToDelete.recording_id);
      toast.success('Grabación eliminada correctamente', { id: loadingToast });
      
      // Cerrar modal y limpiar
      setShowDeleteModal(false);
      setRecordingToDelete(null);
      
      // Recargar lista
      await loadRecordings();
    } catch (error: any) {
      console.error('❌ Error eliminando:', error);
      toast.error(error?.message || 'Error eliminando grabación', { id: loadingToast });
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getVehicleIcon = (type: string) => {
    switch (type) {
      case 'car': return <Car className="w-4 h-4" />;
      case 'truck': return <Truck className="w-4 h-4" />;
      case 'bus': return <Bus className="w-4 h-4" />;
      case 'motorcycle':
      case 'bicycle':
        return <Bike className="w-4 h-4" />;
      default: return <Car className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando grabaciones...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">📹 Grabaciones</h1>
          <p className="mt-1 text-sm text-gray-500">
            {recordings.length} grabación{recordings.length !== 1 ? 'es' : ''} disponible{recordings.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {recordings.length === 0 ? (
          <div className="text-center py-12">
            <Play className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No hay grabaciones</h3>
            <p className="mt-2 text-sm text-gray-500">
              Las grabaciones aparecerán aquí después de grabar desde Live Monitoring
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recordings.map((recording) => (
              <div
                key={recording.recording_id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden"
              >
                {/* Video Preview */}
                <div className="relative bg-gray-900 aspect-video">
                  <video
                    src={recording.video_url}
                    className="w-full h-full object-contain"
                    muted
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleVisualize(recording)}
                      className="bg-white rounded-full p-4 hover:bg-gray-100 transition-colors"
                    >
                      <Play className="w-8 h-8 text-blue-600" />
                    </button>
                  </div>
                </div>

                {/* Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 truncate" title={recording.filename}>
                    {recording.filename}
                  </h3>

                  <div className="mt-3 space-y-2 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>Duración: {formatDuration(recording.duration || 0)}</span>
                    </div>

                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      <span>{formatDate(recording.started_at)}</span>
                    </div>

                    <div className="flex items-center">
                      <Download className="w-4 h-4 mr-2" />
                      <span>{formatFileSize(recording.file_size)}</span>
                    </div>

                    {recording.total_detections !== undefined && (
                      <div className="flex items-center">
                        <Eye className="w-4 h-4 mr-2" />
                        <span>{recording.total_detections} detecciones</span>
                      </div>
                    )}

                    {/* Stats */}
                    {recording.stats && Object.keys(recording.stats).length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {Object.entries(recording.stats).map(([type, count]) => (
                          <div
                            key={type}
                            className="flex items-center space-x-1 bg-gray-100 rounded-full px-2 py-1"
                          >
                            {getVehicleIcon(type)}
                            <span className="text-xs font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Botones de acción */}
                  <div className="mt-4 flex space-x-2">
                    <button
                      onClick={() => handleVisualize(recording)}
                      className="flex-1 flex items-center justify-center space-x-1 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      title="Visualizar video"
                    >
                      <Eye className="w-4 h-4" />
                      <span className="text-sm">Ver</span>
                    </button>

                    <button
                      onClick={() => handleDownload(recording)}
                      className="flex-1 flex items-center justify-center space-x-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors"
                      title="Descargar video"
                    >
                      <Download className="w-4 h-4" />
                      <span className="text-sm">Descargar</span>
                    </button>

                    <button
                      onClick={() => handleDelete(recording)}
                      className="flex items-center justify-center bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors"
                      title="Eliminar grabación"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal de visualización */}
      {showModal && selectedRecording && (
        <div className="fixed inset-0 bg-black bg-opacity-75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full overflow-hidden">
            {/* Header del modal */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedRecording.filename}
              </h3>
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedRecording(null);
                }}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Video */}
            <div className="bg-black">
              <video
                src={selectedRecording.video_url}
                controls
                autoPlay
                className="w-full"
              />
            </div>

            {/* Información */}
            <div className="p-4 bg-gray-50">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Duración:</span>
                  <span className="ml-2 font-medium">{formatDuration(selectedRecording.duration || 0)}</span>
                </div>
                <div>
                  <span className="text-gray-600">Tamaño:</span>
                  <span className="ml-2 font-medium">{formatFileSize(selectedRecording.file_size)}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-600">Fecha:</span>
                  <span className="ml-2 font-medium">{formatDate(selectedRecording.started_at)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmación de eliminación */}
      {showDeleteModal && recordingToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-2xl">
            {/* Header con icono de advertencia */}
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">Confirmar Eliminación</h3>
            </div>

            {/* Mensaje */}
            <div className="mb-6">
              <p className="text-gray-700 mb-2">
                ¿Estás seguro de que deseas eliminar esta grabación?
              </p>
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded border border-gray-200">
                📹 <strong>{recordingToDelete.filename}</strong>
              </p>
              <p className="text-sm text-red-600 mt-3 font-medium">
                ⚠️ Esta acción no se puede deshacer.
              </p>
            </div>

            {/* Botones */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setRecordingToDelete(null);
                }}
                className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                className="px-5 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Recordings;
