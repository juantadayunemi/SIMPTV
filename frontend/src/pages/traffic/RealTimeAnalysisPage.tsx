import React, { useState } from 'react';
import { VideoPlayerWithOverlay } from '../../components/traffic/VideoPlayerWithOverlay';
import { trafficService } from '../../services/traffic.service';

interface Camera {
  id: number;
  name: string;
}

interface Location {
  id: number;
  name: string;
}

export const RealTimeAnalysisPage: React.FC = () => {
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showPlayer, setShowPlayer] = useState(false);

  // Mock data - TODO: Load from API
  const cameras: Camera[] = [
    { id: 1, name: 'Cámara Norte - Intersección Principal' },
    { id: 2, name: 'Cámara Sur - Av. Principal' },
    { id: 3, name: 'Cámara Este - Centro Comercial' },
  ];

  const locations: Location[] = [
    { id: 1, name: 'Intersección Principal' },
    { id: 2, name: 'Av. Principal' },
    { id: 3, name: 'Centro Comercial' },
  ];

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedVideo(e.target.files[0]);
    }
  };

  const handleStartAnalysis = async () => {
    if (!selectedVideo) {
      alert('Por favor selecciona un video');
      return;
    }

    if (!selectedCameraId && !selectedLocationId) {
      alert('Por favor selecciona una cámara o ubicación');
      return;
    }

    try {
      setIsUploading(true);

      // Obtener userId del localStorage (asumiendo que está guardado en el login)
      const userId = localStorage.getItem('userId') || '1';

      // Crear FormData
      const formData = new FormData();
      formData.append('video', selectedVideo);
      formData.append('userId', userId);
      
      if (selectedCameraId) {
        formData.append('cameraId', selectedCameraId.toString());
      }
      if (selectedLocationId) {
        formData.append('locationId', selectedLocationId.toString());
      }

      // Subir video y obtener ID de análisis
      const response = await trafficService.startVideoAnalysis(formData);

      setAnalysisId(response.analysisId.toString());
      setShowPlayer(true);
      
    } catch (error: any) {
      console.error('Error al iniciar análisis:', error);
      alert(`Error: ${error.message || 'No se pudo iniciar el análisis'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Análisis de Tráfico en Tiempo Real
          </h1>
          <p className="text-gray-600 mt-2">
            Sube un video y observa las detecciones de vehículos en tiempo real
          </p>
        </div>

        {/* Upload Section */}
        {!showPlayer && (
          <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
            <h2 className="text-xl font-semibold mb-4">Configuración del Análisis</h2>
            
            {/* Video Upload */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seleccionar Video
              </label>
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100
                  cursor-pointer"
              />
              {selectedVideo && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ {selectedVideo.name} ({(selectedVideo.size / (1024 * 1024)).toFixed(2)} MB)
                </p>
              )}
            </div>

            {/* Camera Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cámara (Opcional)
              </label>
              <select
                value={selectedCameraId || ''}
                onChange={(e) => setSelectedCameraId(e.target.value ? Number(e.target.value) : null)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Seleccionar cámara...</option>
                {cameras.map((camera) => (
                  <option key={camera.id} value={camera.id}>
                    {camera.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Location Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ubicación (Opcional)
              </label>
              <select
                value={selectedLocationId || ''}
                onChange={(e) => setSelectedLocationId(e.target.value ? Number(e.target.value) : null)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Seleccionar ubicación...</option>
                {locations.map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Start Button */}
            <button
              onClick={handleStartAnalysis}
              disabled={!selectedVideo || isUploading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold
                hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                transition-colors duration-200"
            >
              {isUploading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Subiendo video...
                </span>
              ) : (
                '🚀 Iniciar Análisis'
              )}
            </button>
          </div>
        )}

        {/* Video Player with Overlay */}
        {showPlayer && selectedVideo && analysisId && (
          <div className="mt-6">
            <VideoPlayerWithOverlay
              videoFile={selectedVideo}
              analysisId={analysisId}
              wsUrl={import.meta.env.VITE_WS_URL || 'localhost:8000'}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default RealTimeAnalysisPage;
