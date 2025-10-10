import React, { useState, useEffect } from 'react';
import { VideoUpload } from '../../components/traffic/VideoUpload';
import { AnalysisProgress } from '../../components/traffic/AnalysisProgress';
import { AnalysisResults } from '../../components/traffic/AnalysisResults';
import { trafficService } from '../../services/traffic.service';
import {
  getWebSocketService,
  type ProgressUpdate,
  type ProcessingComplete,
  type LogMessage,
  type VehicleDetected,
} from '../../services/websocket.service';

interface Camera {
  id: number;
  name: string;
  locationName: string;
}

interface Location {
  id: number;
  name: string;
}

export const TrafficAnalysisPage: React.FC = () => {
  // State
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [analysisId, setAnalysisId] = useState<number | null>(null);
  
  // Progress tracking
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [results, setResults] = useState<ProcessingComplete | null>(null);
  
  // Data
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);

  // Load cameras and locations
  useEffect(() => {
    const loadData = async () => {
      try {
        // TODO: Implement API calls to fetch cameras and locations
        // const [camerasData, locationsData] = await Promise.all([
        //   trafficService.getCameras(),
        //   trafficService.getLocations(),
        // ]);
        
        // Mock data for now
        setCameras([
          { id: 1, name: 'Camera Norte', locationName: 'Intersección Principal' },
          { id: 2, name: 'Camera Sur', locationName: 'Av. Principal' },
        ]);
        
        setLocations([
          { id: 1, name: 'Intersección Principal' },
          { id: 2, name: 'Av. Principal' },
        ]);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // WebSocket connection cleanup
  useEffect(() => {
    const ws = getWebSocketService();
    
    return () => {
      ws.disconnect();
    };
  }, []);

  const handleStartAnalysis = async () => {
    if (!selectedVideo || (!selectedCameraId && !selectedLocationId)) {
      alert('Please select a video and either a camera or location');
      return;
    }

    try {
      setIsProcessing(true);
      setHasError(false);
      setIsComplete(false);
      setProgress(null);
      setLogs([]);
      setResults(null);

      // Upload video and create analysis
      const formData = new FormData();
      formData.append('video', selectedVideo);
      if (selectedCameraId) formData.append('cameraId', selectedCameraId.toString());
      if (selectedLocationId) formData.append('locationId', selectedLocationId.toString());

      const response = await trafficService.startVideoAnalysis(formData);
      const newAnalysisId = response.id;
      setAnalysisId(newAnalysisId);

      // Connect to WebSocket
      const ws = getWebSocketService();
      await ws.connect(newAnalysisId);

      // Subscribe to progress updates
      ws.on('progress_update', (data: ProgressUpdate) => {
        setProgress(data);
      });

      // Subscribe to vehicle detections
      ws.on('vehicle_detected', (data: VehicleDetected) => {
        setLogs((prev) => [
          ...prev,
          {
            level: 'info',
            message: `Vehicle detected: ${data.vehicle_type} (confidence: ${(data.confidence * 100).toFixed(1)}%)`,
            timestamp: new Date().toISOString(),
          },
        ]);
      });

      // Subscribe to completion
      ws.on('processing_complete', (data: ProcessingComplete) => {
        setIsProcessing(false);
        setIsComplete(true);
        setResults(data);
        setLogs((prev) => [
          ...prev,
          {
            level: 'info',
            message: `Analysis complete! Total vehicles: ${data.total_vehicles}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      });

      // Subscribe to errors
      ws.on('processing_error', (data: any) => {
        setIsProcessing(false);
        setHasError(true);
        setLogs((prev) => [
          ...prev,
          {
            level: 'error',
            message: data.error || 'Processing failed',
            timestamp: new Date().toISOString(),
          },
        ]);
      });

      // Subscribe to log messages
      ws.on('log_message', (data: LogMessage) => {
        setLogs((prev) => [...prev, data]);
      });

    } catch (error: any) {
      console.error('Error starting analysis:', error);
      setIsProcessing(false);
      setHasError(true);
      setLogs((prev) => [
        ...prev,
        {
          level: 'error',
          message: error.message || 'Failed to start analysis',
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Traffic Analysis</h1>
        <p className="text-gray-600">Upload and analyze traffic video footage</p>
      </div>

      {/* Upload Section */}
      {!isProcessing && !isComplete && (
        <VideoUpload
          onVideoSelected={setSelectedVideo}
          selectedVideo={selectedVideo}
          onCameraSelected={setSelectedCameraId}
          onLocationSelected={setSelectedLocationId}
          onStartAnalysis={handleStartAnalysis}
          isProcessing={isProcessing}
          cameras={cameras}
          locations={locations}
        />
      )}

      {/* Progress Section */}
      {(isProcessing || isComplete || hasError) && (
        <AnalysisProgress
          progress={progress}
          logs={logs}
          isProcessing={isProcessing}
          isComplete={isComplete}
          hasError={hasError}
        />
      )}

      {/* Results Section */}
      {isComplete && results && (
        <AnalysisResults results={results} analysisId={analysisId} />
      )}
    </div>
  );
};

export default TrafficAnalysisPage;