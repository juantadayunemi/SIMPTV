import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { ArrowLeft, MapPin, User, FileText, AlertCircle, Calendar, Loader2 } from 'lucide-react';
import { complaintsService, VehicleComplaintDetectionDetail, SeverityLevel } from '../../services/complaints.service';

// Fix para los iconos de Leaflet
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

// Icono para ubicación de detección
const detectionIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none"
      stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
      <circle cx="12" cy="10" r="3"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

export const VehicleComplaintDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState<VehicleComplaintDetectionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadComplaintDetail(parseInt(id));
    }
  }, [id]);

  const loadComplaintDetail = async (complaintId: number) => {
    try {
      setLoading(true);
      const data = await complaintsService.getComplaint(complaintId);
      setComplaint(data);
    } catch (err) {
      console.error('Error loading complaint detail:', err);
      setError('Error al cargar los detalles de la denuncia');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: SeverityLevel | null) => {
    switch (severity) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityLabel = (severity: SeverityLevel | null) => {
    switch (severity) {
      case 'HIGH':
        return 'Alta';
      case 'MEDIUM':
        return 'Media';
      case 'LOW':
        return 'Baja';
      default:
        return 'Desconocida';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Cargando detalles de la denuncia...</p>
        </div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">{error || 'Denuncia no encontrada'}</p>
          <button
            onClick={() => navigate('/vehicles/reports')}
            className="mt-4 text-blue-600 hover:text-blue-700 underline"
          >
            Volver al listado
          </button>
        </div>
      </div>
    );
  }

  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  const defaultCenter: [number, number] = complaint.location
    ? [complaint.location.latitude, complaint.location.longitude]
    : [-2.170998, -79.922359];

  // Crear array de posiciones para la ruta (tracking)
  const trackingPath: [number, number][] = complaint.detectionHistory
    .filter((d) => d.location)
    .map((d) => [d.location!.latitude, d.location!.longitude]);

  return (
    <div className="min-h-screen bg-gray-50 -top-4">
      {/* Header */}
      <div className="bg-white shadow -mt-2 sticky -top-8 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/vehicles-reports')}
                className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Denuncia: {complaint.plateNumber || 'N/A'}
                </h1>
                <p className="text-sm text-gray-600">Caso: {complaint.caseNumber}</p>
              </div>
            </div>
            <div className={`px-3 py-1.5 rounded-full border-2 ${getSeverityColor(complaint.severity)}`}>
              <span className="text-sm font-semibold">Prioridad: {getSeverityLabel(complaint.severity)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1800px] mx-auto px-4 mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Columna izquierda: Mapa (60%) */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Ubicación y Tracking
              </h2>
              <div style={{ height: '700px', borderRadius: '8px', overflow: 'hidden' }}>
                <MapContainer center={defaultCenter} zoom={13} style={{ height: '100%', width: '100%' }}>
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />

                  {/* Línea de tracking */}
                  {trackingPath.length > 1 && (
                    <Polyline positions={trackingPath} color="#3b82f6" weight={3} opacity={0.7} />
                  )}

                  {/* Marcadores de detecciones */}
                  {complaint.detectionHistory
                    .filter((d) => d.location)
                    .map((detection) => (
                      <Marker
                        key={detection.id}
                        position={[detection.location!.latitude, detection.location!.longitude]}
                        icon={detectionIcon}
                      >
                        <Popup>
                          <div style={{ minWidth: '200px' }}>
                            <strong>{formatDate(detection.detectedAt)}</strong>
                            <p style={{ fontSize: '12px', marginTop: '4px' }}>
                              {detection.location!.description}
                            </p>
                            {detection.location!.city && (
                              <p style={{ fontSize: '12px' }}>{detection.location!.city}</p>
                            )}
                            <p style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
                              Confianza: {(detection.confidence * 100).toFixed(1)}%
                            </p>
                          </div>
                        </Popup>
                      </Marker>
                    ))}
                </MapContainer>
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                  Ruta de tracking entre detecciones
                </p>
                <p className="flex items-center gap-2 mt-2">
                  <span className="text-red-600">📍</span>
                  Ubicaciones de detección
                </p>
              </div>
            </div>
          </div>

          {/* Columna derecha: Info y denuncias (40%) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Información del Propietario
              </h2>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Nombre</label>
                  <p className="text-gray-900 font-medium">{complaint.ownerName}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Cédula</label>
                  <p className="text-gray-900 font-medium">{complaint.ownerIdNumber}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Dirección</label>
                  <p className="text-gray-900 font-medium">{complaint.ownerAddress}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Tipo de Vehículo</label>
                    <p className="text-gray-900 font-medium">{complaint.vehicleType}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Total Denuncias</label>
                    <p className="text-gray-900 font-medium">{complaint.totalComplaintsCount}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Imágenes del vehículo */}
            {(complaint.vehicleImage || complaint.plateImage) && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Evidencia Fotográfica</h2>
                <div className="grid grid-cols-1 gap-4">
                  {complaint.vehicleImage && (
                    <div>
                      <label className="text-sm font-medium text-gray-500 block mb-2">
                        Imagen del Vehículo
                      </label>
                      <img
                        src={`${baseUrl}${complaint.vehicleImage.path}`}
                        alt="Vehículo"
                        className="w-full rounded-lg border border-gray-300"
                      />
                      <p className="text-xs text-gray-500 mt-2">
                        Capturado: {formatDate(complaint.vehicleImage.capturedAt)}
                      </p>
                    </div>
                  )}
                  {complaint.plateImage && (
                    <div>
                      <label className="text-sm font-medium text-gray-500 block mb-2">
                        Imagen de la Placa
                      </label>
                      <img
                        src={`${baseUrl}${complaint.plateImage.path}`}
                        alt="Placa"
                        className="w-full rounded-lg border border-gray-300"
                      />
                      <p className="text-xs text-gray-500 mt-2">
                        Capturado: {formatDate(complaint.plateImage.capturedAt)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Lista de denuncias */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Denuncias Registradas ({complaint.complaints.length})
              </h2>
              <div className="space-y-3">
                {complaint.complaints.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            #{item.sequenceNumber}
                          </span>
                          {item.severity && (
                            <span
                              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(
                                item.severity
                              )}`}
                            >
                              {getSeverityLabel(item.severity)}
                            </span>
                          )}
                        </div>
                        <p className="text-gray-900 font-medium">{item.complaintText}</p>
                        {item.complaintType && (
                          <p className="text-sm text-gray-600 mt-1">Tipo: {item.complaintType}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Historial de detecciones */}
            {complaint.detectionHistory.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Historial de Detecciones ({complaint.detectionHistory.length})
                </h2>
                <div className="space-y-3">
                  {complaint.detectionHistory.map((detection) => (
                    <div key={detection.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">
                            {formatDate(detection.detectedAt)}
                          </p>
                          {detection.location && (
                            <p className="text-sm text-gray-600 mt-1 flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {detection.location.description}
                              {detection.location.city && `, ${detection.location.city}`}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 mt-1">
                            Confianza: {(detection.confidence * 100).toFixed(1)}% | Frame: #
                            {detection.frameNumber}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
         
        </div>
      </div>
    </div>
  );
};

export default VehicleComplaintDetailPage;
