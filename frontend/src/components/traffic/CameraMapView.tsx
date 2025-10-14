/**
 * Componente CameraMapView
 * Mapa interactivo que muestra todas las cámaras registradas en el sistema
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { trafficService } from '../../services/traffic.service';
import { CameraEntity } from '@traffic-analysis/shared';

// Fix para los iconos de Leaflet en Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Icono personalizado para cámaras activas (verde)
const activeCameraIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// Icono personalizado para cámaras inactivas (rojo)
const inactiveCameraIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// Icono personalizado para cámaras en mantenimiento (amarillo)
const maintenanceCameraIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

interface CameraWithLocation extends CameraEntity {
  location?: {
    latitude: number;
    longitude: number;
    description: string;
    city?: string;
    province?: string;
  };
}

interface CameraMapViewProps {
  height?: string;
  onCameraClick?: (camera: CameraWithLocation) => void;
}

export default function CameraMapView({ height = '500px', onCameraClick }: CameraMapViewProps) {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState<CameraWithLocation[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Posición por defecto: Guayaquil, Ecuador
  const defaultCenter: [number, number] = [-2.170998, -79.922359];

  useEffect(() => {
    loadCamerasWithLocations();
  }, []);

  const loadCamerasWithLocations = async () => {
    try {
      setLoading(true);
      
      // Obtener todas las cámaras
      const camerasData = await trafficService.getCameras();
      
      // Para cada cámara, obtener su ubicación
      const camerasWithLocations = await Promise.all(
        camerasData.map(async (camera) => {
          try {
            const location = await trafficService.getLocation(camera.locationId);
            return {
              ...camera,
              location: {
                latitude: location.latitude,
                longitude: location.longitude,
                description: location.description,
                city: location.city,
                province: location.province,
              },
            };
          } catch (error) {
            console.error(`Error loading location for camera ${camera.id}:`, error);
            return camera;
          }
        })
      );
      
      setCameras(camerasWithLocations);
    } catch (error) {
      console.error('Error loading cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCameraIcon = (camera: CameraWithLocation) => {
    if (camera.status === 'ACTIVE') return activeCameraIcon;
    if (camera.status === 'MAINTENANCE') return maintenanceCameraIcon;
    return inactiveCameraIcon;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Activa</span>';
      case 'MAINTENANCE':
        return '<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Mantenimiento</span>';
      case 'INACTIVE':
        return '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Inactiva</span>';
      default:
        return '<span style="background: #6b7280; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Desconocido</span>';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando mapa de cámaras...</p>
        </div>
      </div>
    );
  }

  // Calcular el centro del mapa basado en las cámaras existentes
  const mapCenter: [number, number] = cameras.length > 0 && cameras[0].location
    ? [cameras[0].location.latitude, cameras[0].location.longitude]
    : defaultCenter;

  return (
    <div style={{ height, borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)' }}>
      <MapContainer
        center={mapCenter}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
      >
        {/* OpenStreetMap Tiles - GRATIS, sin límites */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Marcadores de cámaras */}
        {cameras.map((camera) => {
          if (!camera.location) return null;
          
          return (
            <Marker
              key={camera.id}
              position={[camera.location.latitude, camera.location.longitude]}
              icon={getCameraIcon(camera)}
              eventHandlers={{
                click: () => onCameraClick?.(camera),
              }}
            >
              <Popup>
                <div style={{ minWidth: '220px' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <strong style={{ fontSize: '16px' }}>{camera.name}</strong>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    {getStatusBadge(camera.status)}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    <div><strong>Marca:</strong> {camera.brand}</div>
                    <div><strong>Modelo:</strong> {camera.model}</div>
                    <div><strong>Resolución:</strong> {camera.resolution}</div>
                    <div><strong>FPS:</strong> {camera.fps}</div>
                    <div style={{ marginTop: '8px' }}>
                      <strong>Ubicación:</strong><br />
                      {camera.location.description}
                    </div>
                    {camera.location.city && (
                      <div><strong>Ciudad:</strong> {camera.location.city}</div>
                    )}
                  </div>
                  <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                    <button
                      onClick={() => navigate(`/camera/${camera.id}`)}
                      style={{
                        width: '100%',
                        backgroundColor: '#2563eb',
                        color: 'white',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: '500',
                        fontSize: '14px',
                      }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1d4ed8'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
                    >
                      ▶️ Reproducir
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
