import React, { useState, useEffect } from 'react';
import { X, Camera, MapPin, Settings } from 'lucide-react';
import { trafficService, type Location } from '../../services/traffic.service';
import { CameraEntity, StatusCameraKey } from '@traffic-analysis/shared';

interface EditCameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (cameraData: CameraEntity) => Promise<void>;
  camera: CameraEntity;
}

const EditCameraModal: React.FC<EditCameraModalProps> = ({
  isOpen,
  onClose,
  onSave,
  camera,
}) => {
  const [formData, setFormData] = useState<CameraEntity>(camera);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [isLoadingLocations, setIsLoadingLocations] = useState(false);

  // Cargar ubicaciones cuando se abre el modal
  useEffect(() => {
    if (isOpen) {
      loadLocations();
    }
  }, [isOpen]);

  useEffect(() => {
    setFormData(camera);
  }, [camera]);

  const loadLocations = async () => {
    setIsLoadingLocations(true);
    try {
      const data = await trafficService.getLocations();
      setLocations(data);
    } catch (err) {
      console.error('Error cargando ubicaciones:', err);
      setError('No se pudieron cargar las ubicaciones');
    } finally {
      setIsLoadingLocations(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error al actualizar la cámara');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (field: keyof CameraEntity, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleMaintenanceToggle = () => {
    setFormData(prev => ({
      ...prev,
      status: prev.status === 'MAINTENANCE' ? 'ACTIVE' : 'MAINTENANCE'
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">
                Configurar Cámara
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Nombre */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <Camera className="w-4 h-4" />
                <span>Nombre de la Cámara</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ej: Cámara Av. Principal"
                required
              />
            </div>

            {/* Ubicación */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4" />
                <span>Ubicación</span>
              </label>
              {isLoadingLocations ? (
                <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50">
                  <span className="text-sm text-gray-500">Cargando ubicaciones...</span>
                </div>
              ) : (
                <select
                  value={formData.locationId || ''}
                  onChange={(e) => {
                    const selectedId = parseInt(e.target.value);
                    const selectedLocation = locations.find(loc => loc.id === selectedId);
                    setFormData(prev => ({
                      ...prev,
                      locationId: selectedId,
                      location: selectedLocation?.description || ''
                    }));
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Seleccione una ubicación</option>
                  {locations.map(location => (
                    <option key={location.id} value={location.id}>
                      {location.description} - {location.city || location.country}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Estado */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <Settings className="w-4 h-4" />
                <span>Estado de la Cámara</span>
              </label>
              <select
                value={formData.status}
                onChange={(e) => handleChange('status', e.target.value as StatusCameraKey)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="ACTIVE">✅ Activa - En funcionamiento</option>
                <option value="MAINTENANCE">🔧 En Mantenimiento - Temporalmente fuera de servicio</option>
                <option value="INACTIVE">❌ Inactiva - Deshabilitada</option>
              </select>
              
              {/* Checkbox de Mantenimiento Rápido */}
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.status === 'MAINTENANCE'}
                    onChange={handleMaintenanceToggle}
                    className="w-4 h-4 text-yellow-600 border-gray-300 rounded focus:ring-yellow-500"
                  />
                  <span className="text-sm font-medium text-yellow-900">
                    🔧 Poner en mantenimiento
                  </span>
                </label>
                <p className="text-xs text-yellow-700 mt-1 ml-7">
                  Marca esta opción para pausar temporalmente el procesamiento de esta cámara
                </p>
              </div>
              
              {/* Explicación del estado seleccionado */}
              <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                {formData.status === 'ACTIVE' && (
                  <p className="text-xs text-gray-600">
                    <strong>Activa:</strong> La cámara está funcionando normalmente y procesando videos.
                  </p>
                )}
                {formData.status === 'MAINTENANCE' && (
                  <p className="text-xs text-gray-600">
                    <strong>En Mantenimiento:</strong> La cámara está temporalmente fuera de servicio para reparación o mantenimiento preventivo.
                  </p>
                )}
                {formData.status === 'INACTIVE' && (
                  <p className="text-xs text-gray-600">
                    <strong>Inactiva:</strong> La cámara está deshabilitada y no se utilizará para análisis.
                  </p>
                )}
              </div>
            </div>

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={isSaving}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
                disabled={isSaving}
              >
                {isSaving ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Guardando...
                  </span>
                ) : (
                  '💾 Guardar Cambios'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditCameraModal;
