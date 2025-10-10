/**
 * Componente MapLocationPicker
 * Mapa interactivo con Leaflet para seleccionar ubicación de cámaras
 * 100% GRATIS - Sin API key - Sin límites
 */

import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

interface MapLocationPickerProps {
  onLocationSelect: (location: {
    latitude: number;
    longitude: number;
    description: string;
    city?: string;
    province?: string;
    country?: string;
  }) => void;
  initialPosition?: {
    latitude: number;
    longitude: number;
  };
  height?: string;
}

// Componente interno para manejar clicks en el mapa
function LocationMarker({ 
  position, 
  setPosition, 
  onLocationChange 
}: { 
  position: [number, number] | null;
  setPosition: (pos: [number, number]) => void;
  onLocationChange: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition([lat, lng]);
      onLocationChange(lat, lng);
    },
  });

  return position === null ? null : (
    <Marker position={position}>
      <Popup>
        📍 Ubicación seleccionada<br />
        <strong>Lat:</strong> {position[0].toFixed(6)}<br />
        <strong>Lng:</strong> {position[1].toFixed(6)}
      </Popup>
    </Marker>
  );
}

export default function MapLocationPicker({
  onLocationSelect,
  initialPosition,
  height = '400px',
}: MapLocationPickerProps) {
  // Posición por defecto: Guayaquil, Ecuador (puedes cambiar a Durán si prefieres)
  // Coordenadas de Guayaquil: -2.170998, -79.922359
  // Coordenadas de Durán: -2.170998, -79.837006
  const defaultCenter: [number, number] = [
    initialPosition?.latitude || -2.170998,  // Guayaquil
    initialPosition?.longitude || -79.922359, // Guayaquil
  ];

  const [position, setPosition] = useState<[number, number] | null>(
    initialPosition ? [initialPosition.latitude, initialPosition.longitude] : null
  );
  const [address, setAddress] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // Reverse Geocoding con Nominatim (OpenStreetMap) - GRATIS
  const fetchAddress = async (lat: number, lng: number) => {
    setLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
        {
          headers: {
            'Accept-Language': 'es',
          },
        }
      );
      const data = await response.json();
      
      if (data && data.display_name) {
        setAddress(data.display_name);
        
        // Extraer ciudad y provincia de la respuesta de Nominatim
        const addressDetails = data.address || {};
        const city = addressDetails.city || 
                    addressDetails.town || 
                    addressDetails.village || 
                    addressDetails.municipality || 
                    addressDetails.road || 
                    '';
        const province = addressDetails.state || 
                        addressDetails.province || 
                        addressDetails.county || 
                        '';
        const country = addressDetails.country || 'Ecuador';
        
        // Enviar ubicación al componente padre con datos estructurados
        onLocationSelect({
          latitude: lat,
          longitude: lng,
          description: data.display_name,
          city,
          province,
          country,
        });
      }
    } catch (error) {
      console.error('Error fetching address:', error);
      setAddress('No se pudo obtener la dirección');
      
      // Enviar ubicación sin descripción
      onLocationSelect({
        latitude: lat,
        longitude: lng,
        description: `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`,
        city: '',
        province: '',
        country: 'Ecuador',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLocationChange = (lat: number, lng: number) => {
    fetchAddress(lat, lng);
  };

  useEffect(() => {
    if (position) {
      fetchAddress(position[0], position[1]);
    }
  }, []);

  return (
    <div className="space-y-3">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <div className="text-blue-600 mt-0.5">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="text-sm">
            <p className="font-medium text-blue-900">Haz click en el mapa para seleccionar la ubicación</p>
            <p className="text-blue-700 mt-1">
              El sistema obtendrá automáticamente la dirección de la ubicación seleccionada
            </p>
          </div>
        </div>
      </div>

      <div 
        className="rounded-lg overflow-hidden border border-gray-300 shadow-md"
        style={{ height }}
      >
        <MapContainer
          center={defaultCenter}
          zoom={13}  // Zoom 13 muestra bien la ciudad (12-14 es ideal para ciudades)
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          {/* OpenStreetMap Tiles - GRATIS, sin límites */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <LocationMarker 
            position={position} 
            setPosition={setPosition}
            onLocationChange={handleLocationChange}
          />
        </MapContainer>
      </div>
    </div>
  );
}
