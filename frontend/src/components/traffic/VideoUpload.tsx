import React, { useState, useRef } from 'react';
import { Upload, Camera, MapPin, Play, X } from 'lucide-react';

interface VideoUploadProps {
  onVideoSelected: (file: File) => void;
  selectedVideo: File | null;
  onCameraSelected: (cameraId: number) => void;
  onLocationSelected: (locationId: number) => void;
  onStartAnalysis: () => void;
  isProcessing: boolean;
  cameras: Array<{ id: number; name: string; locationName: string }>;
  locations: Array<{ id: number; name: string }>;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  onVideoSelected,
  selectedVideo,
  onCameraSelected,
  onLocationSelected,
  onStartAnalysis,
  isProcessing,
  cameras,
  locations,
}) => {
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('video/')) {
        onVideoSelected(file);
      } else {
        alert('Please upload a valid video file');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onVideoSelected(e.target.files[0]);
    }
  };

  const handleCameraChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const cameraId = parseInt(e.target.value);
    setSelectedCameraId(cameraId);
    onCameraSelected(cameraId);

    // Auto-seleccionar location de la cámara
    const camera = cameras.find((c) => c.id === cameraId);
    if (camera) {
      const location = locations.find((l) => l.name === camera.locationName);
      if (location) {
        setSelectedLocationId(location.id);
        onLocationSelected(location.id);
      }
    }
  };

  const handleLocationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const locationId = parseInt(e.target.value);
    setSelectedLocationId(locationId);
    onLocationSelected(locationId);
  };

  const clearVideo = () => {
    onVideoSelected(null as any);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const canStartAnalysis = selectedVideo && (selectedCameraId || selectedLocationId);

  return (
    <div className="space-y-6">
      {/* Video Upload Area */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Upload Video</h2>

        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : selectedVideo
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {selectedVideo ? (
            <div className="space-y-3">
              <div className="flex items-center justify-center">
                <Play className="h-12 w-12 text-green-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {selectedVideo.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(selectedVideo.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={clearVideo}
                className="inline-flex items-center gap-2 px-3 py-1 text-sm text-red-600 hover:text-red-700"
                disabled={isProcessing}
              >
                <X className="h-4 w-4" />
                Remove
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-center">
                <Upload className="h-12 w-12 text-gray-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600">
                  Drag and drop your video here, or{' '}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    browse
                  </button>
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supported formats: MP4, AVI, MOV (Max 500MB)
                </p>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
      </div>

      {/* Camera & Location Selection */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Analysis Settings</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Camera Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Camera className="inline h-4 w-4 mr-2" />
              Camera
            </label>
            <select
              value={selectedCameraId || ''}
              onChange={handleCameraChange}
              disabled={isProcessing}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select camera...</option>
              {cameras.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name} - {camera.locationName}
                </option>
              ))}
            </select>
          </div>

          {/* Location Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="inline h-4 w-4 mr-2" />
              Location
            </label>
            <select
              value={selectedLocationId || ''}
              onChange={handleLocationChange}
              disabled={isProcessing}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select location...</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Start Analysis Button */}
      <div className="flex justify-end">
        <button
          onClick={onStartAnalysis}
          disabled={!canStartAnalysis || isProcessing}
          className={`px-6 py-3 rounded-md font-medium flex items-center gap-2 ${
            canStartAnalysis && !isProcessing
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <Play className="h-5 w-5" />
          {isProcessing ? 'Processing...' : 'Start Analysis'}
        </button>
      </div>
    </div>
  );
};
