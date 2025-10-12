import React, { useState, useCallback, useRef } from 'react';
import { trafficService } from '../../services/traffic.service';
import { X, Upload, Play, Loader2 } from 'lucide-react';

interface ConnectPathModalProps {
  isOpen: boolean;
  onClose: () => void;
  cameraName: string;
  cameraId: number;
  locationId: number;
  userId: number;
  onPlay: (videoFile: File, analysisId: number) => void;
}

export const ConnectPathModal: React.FC<ConnectPathModalProps> = ({
  isOpen,
  onClose,
  cameraName,
  cameraId,
  locationId,
  userId,
  onPlay,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const uploadRef = useRef<{ cancel: boolean }>({ cancel: false });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const videoFile = files.find(file => file.type.startsWith('video/'));

    if (videoFile) {
      setSelectedFile(videoFile);
    } else {
      alert('Por favor selecciona un archivo de video válido');
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Subida real por chunks con análisis incremental
  const handlePlay = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setProgress(0);
    uploadRef.current.cancel = false;

    try {
      // Usar el nuevo método de subida por chunks
      const result = await trafficService.uploadVideoInChunks(
        selectedFile,
        cameraId,
        locationId,
        userId,
        '', // weatherConditions - opcional
        (progress, message) => {
          setProgress(progress);
          console.log(`Progress: ${progress}% - ${message}`);
        },
        (chunkIndex, response) => {
          console.log(`Chunk ${chunkIndex} uploaded:`, response);
        }
      );

      console.log('Upload completed:', result);
      setIsProcessing(false);
      setSelectedFile(null);
      onPlay(selectedFile, parseInt(result.analysisId));
      onClose();

    } catch (err) {
      console.error('Error uploading video:', err);
      alert('Error subiendo el video en chunks.');
      setIsProcessing(false);
    }
  };

  // Si el modal se cierra manualmente, cancela la subida simulada
  const handleClose = () => {
    uploadRef.current.cancel = true;
    setIsProcessing(false);
    setProgress(0);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Conectar Video</h2>
            <p className="text-sm text-gray-600 mt-1">Cámara: {cameraName}</p>
          </div>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Drag & Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              isDragging
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 bg-gray-50'
            }`}
          >
            <Upload
              className={`w-12 h-12 mx-auto mb-4 ${
                isDragging ? 'text-primary-500' : 'text-gray-400'
              }`}
            />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Arrastra y suelta tu video aquí
            </p>
            <p className="text-sm text-gray-600 mb-4">
              o haz clic para seleccionar un archivo
            </p>
            <label className="inline-block">
              <input
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                disabled={isProcessing}
                className="hidden"
              />
              <span className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                Seleccionar archivo
              </span>
            </label>
          </div>

          {/* Selected File Info */}
          {selectedFile && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <Upload className="w-5 h-5 text-green-600" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-green-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-green-700">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Barra de progreso y estado de subida */}
          {isProcessing && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">
                    Subiendo video por chunks y analizando en tiempo real...
                  </p>
                  <div className="w-full bg-blue-100 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-blue-700 mt-1">{progress}% completado</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            onClick={handlePlay}
            disabled={!selectedFile || isProcessing}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Reproducir
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConnectPathModal;
