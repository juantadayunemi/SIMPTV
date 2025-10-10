/**
 * Modal para agregar nueva cámara con selección de ubicación en mapa
 */

import { useState } from 'react';
import { X } from 'lucide-react';
import MapLocationPicker from './MapLocationPicker';

interface AddCameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (cameraData: CameraFormData) => Promise<void>;
}

export interface CameraFormData {
  // Camera data
  name: string;
  brand: string;
  model: string;
  resolution: string;
  fps: number;
  lanes: number;
  coversBothDirections: boolean;
  notes: string;
  
  // Location data
  locationDescription: string;
  latitude: number;
  longitude: number;
  city: string;
  province: string;
  country: string;
}

export default function AddCameraModal({ isOpen, onClose, onSubmit }: AddCameraModalProps) {
  const [step, setStep] = useState<'location' | 'camera'>('location');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [formData, setFormData] = useState<CameraFormData>({
    name: '',
    brand: '',
    model: '',
    resolution: '1920x1080',
    fps: 30,
    lanes: 2,
    coversBothDirections: false,
    notes: '',
    locationDescription: '',
    latitude: 0,
    longitude: 0,
    city: '',
    province: '',
    country: 'Ecuador',
  });

  const handleLocationSelect = (location: {
    latitude: number;
    longitude: number;
    description: string;
    city?: string;
    province?: string;
    country?: string;
  }) => {
    // Usar los datos estructurados de Nominatim
    setFormData(prev => ({
      ...prev,
      latitude: location.latitude,
      longitude: location.longitude,
      locationDescription: location.description,
      city: location.city || '',
      province: location.province || '',
      country: location.country || 'Ecuador',
    }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validaciones
    if (!formData.latitude || !formData.longitude) {
      setError('Por favor selecciona una ubicación en el mapa');
      setStep('location');
      return;
    }

    if (!formData.name.trim()) {
      setError('El nombre de la cámara es requerido');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      await onSubmit(formData);
      
      // Reset form
      setFormData({
        name: '',
        brand: '',
        model: '',
        resolution: '1920x1080',
        fps: 30,
        lanes: 2,
        coversBothDirections: false,
        notes: '',
        locationDescription: '',
        latitude: 0,
        longitude: 0,
        city: '',
        province: '',
        country: 'Ecuador',
      });
      setStep('location');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error al crear la cámara');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-white rounded-t-xl flex-shrink-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Agregar Nueva Cámara</h2>
            <p className="text-sm text-gray-600 mt-1">
              Paso {step === 'location' ? '1' : '2'} de 2: {step === 'location' ? 'Ubicación' : 'Datos de la Cámara'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={loading}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-4 pb-2 flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className={`flex-1 h-2 rounded-full ${step === 'location' ? 'bg-blue-600' : 'bg-green-600'}`} />
            <div className={`flex-1 h-2 rounded-full ${step === 'camera' ? 'bg-blue-600' : 'bg-gray-200'}`} />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
          {/* Content - Scrollable Area */}
          <div className={`flex-1 overflow-y-auto ${step === 'location' ? 'p-6 pb-0' : 'p-6'}`}>
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{error}</span>
                </div>
              </div>
            )}

            {/* Step 1: Location */}
            {step === 'location' && (
              <div className="space-y-4">
                <MapLocationPicker
                  onLocationSelect={handleLocationSelect}
                  height="450px"
                />
              </div>
            )}

            {/* Step 2: Camera Data */}
            {step === 'camera' && (
              <div className="space-y-6">
                {/* Nombre */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de la Cámara *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Ej: CAM-001-Centro"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Brand & Model */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Marca
                    </label>
                    <input
                      type="text"
                      name="brand"
                      value={formData.brand}
                      onChange={handleInputChange}
                      placeholder="Ej: Hikvision"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Modelo
                    </label>
                    <input
                      type="text"
                      name="model"
                      value={formData.model}
                      onChange={handleInputChange}
                      placeholder="Ej: DS-2CD2143G0-I"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Resolution & FPS */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Resolución
                    </label>
                    <select
                      name="resolution"
                      value={formData.resolution}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="1920x1080">1920x1080 (Full HD)</option>
                      <option value="1280x720">1280x720 (HD)</option>
                      <option value="3840x2160">3840x2160 (4K)</option>
                      <option value="2560x1440">2560x1440 (2K)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      FPS
                    </label>
                    <input
                      type="number"
                      name="fps"
                      value={formData.fps}
                      onChange={handleInputChange}
                      min="1"
                      max="120"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Lanes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Número de Carriles
                  </label>
                  <input
                    type="number"
                    name="lanes"
                    value={formData.lanes}
                    onChange={handleInputChange}
                    min="1"
                    max="8"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Covers Both Directions */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    name="coversBothDirections"
                    id="coversBothDirections"
                    checked={formData.coversBothDirections}
                    onChange={handleInputChange}
                    className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <label htmlFor="coversBothDirections" className="text-sm font-medium text-gray-700">
                    Cubre ambas direcciones del tráfico
                  </label>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notas Adicionales
                  </label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    placeholder="Información adicional sobre la cámara..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
          
              </div>
            )}
          </div>

          {/* Footer Actions - Fixed at bottom */}
          <div className="flex-shrink-0 border-t bg-gray-50 rounded-b-xl">
            {/* Location Info (only in step 1) */}
            {step === 'location' && formData.latitude && formData.longitude && (
              <div className="px-6 pt-4 pb-2">
                <div className="bg-white border border-gray-200 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 text-xl flex-shrink-0">✓</span>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-gray-900 text-sm mb-1">Ubicación Seleccionada</h4>
                      <p className="text-sm text-gray-700 mb-1 break-words">{formData.locationDescription}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">
                          Lat: {formData.latitude.toFixed(6)}
                        </span>
                        <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">
                          Lng: {formData.longitude.toFixed(6)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Buttons */}
            <div className="flex items-center justify-between p-6 pt-3">
            {step === 'location' ? (
              <>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={loading}
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (!formData.latitude || !formData.longitude) {
                      setError('Por favor selecciona una ubicación en el mapa');
                      return;
                    }
                    setError('');
                    setStep('camera');
                  }}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={!formData.latitude || !formData.longitude}
                >
                  Siguiente →
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setStep('location')}
                  className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={loading}
                >
                  ← Atrás
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Creando...</span>
                    </>
                  ) : (
                    'Crear Cámara'
                  )}
                </button>
              </>
            )}
          </div>
          </div>
        </form>
      </div>
    </div>
  );
}
