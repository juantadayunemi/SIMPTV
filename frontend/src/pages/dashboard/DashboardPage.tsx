import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video } from 'lucide-react';
import CameraMapView from '../../components/traffic/CameraMapView';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity } from '@traffic-analysis/shared';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState<CameraEntity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      setLoading(true);
      const camerasData = await trafficService.getCameras();
      setCameras(camerasData);
    } catch (error) {
      console.error('Error loading cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCameraClick = (cameraId: number) => {
    // Navegar a la página de análisis en vivo de la cámara
    navigate(`/camera/${cameraId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="text-center">
        <p className="text-gray-600 mb-4">
          Gestión y predicciones inteligentes para que disfrutes de un tráfico más tranquilo.
        </p>
        <h1 className="text-3xl font-bold text-blue-600 mb-6">
          Bienvenido a TrafiSmart
        </h1>
      </div>

      {/* Camera Buttons */}
      <div className="flex justify-center gap-4 mb-6">
        {loading ? (
          <div className="text-gray-500">Cargando cámaras...</div>
        ) : cameras.length > 0 ? (
          cameras.slice(0, 2).map((camera, index) => (
            <button
              key={camera.id}
              onClick={() => handleCameraClick(camera.id)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors shadow-md"
            >
              <Video className="w-5 h-5" />
              <span>Cámara {index + 1}</span>
            </button>
          ))
        ) : (
          <div className="text-gray-500">
            No hay cámaras disponibles. Agrega cámaras desde la sección "Cámaras".
          </div>
        )}
      </div>

      {/* Map Section */}
      <div className="bg-white shadow rounded-lg p-4">
        <CameraMapView height="500px" />
      </div>
    </div>
  );
};

export default DashboardPage;