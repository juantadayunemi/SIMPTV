import api from './api';

export interface TrafficAnalysis {
  id: string;
  location: string;
  videoPath?: string;
  vehicleCount: number;
  analysisData?: any;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  createdAt: string;
  plateDetections?: PlateDetection[];
}

export interface PlateDetection {
  id: string;
  plateNumber: string;
  confidence: number;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  vehicleType?: string;
  trafficAnalysisId: string;
  createdAt: string;
}

export interface CreateAnalysisData {
  location: string;
  videoPath?: string;
}

export interface TrafficPrediction {
  timeSlot: string;
  predictedVehicles: number;
  densityLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
}

export interface TrafficStatistics {
  totalAnalyses: number;
  avgVehiclesPerAnalysis: number;
  totalVehiclesDetected: number;
  totalPlatesDetected: number;
  mostActiveLocation: string;
  locationBreakdown: Record<string, number>;
}

export interface Location {
  id: number;
  description: string;
  latitude: number;
  longitude: number;
  city?: string;
  province?: string;
  country: string;
  notes?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Camera {
  id: number;
  name: string;
  brand?: string;
  model?: string;
  resolution?: string;
  fps?: number;
  locationId: number;
  currentLocationId?: number;
  isActive: boolean;
  isMobile: boolean;
  lanes: number;
  coversBothDirections: boolean;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateLocationData {
  description: string;
  latitude: number;
  longitude: number;
  city?: string;
  province?: string;
  country: string;
  notes?: string;
}

export interface CreateCameraData {
  name: string;
  brand?: string;
  model?: string;
  resolution?: string;
  fps?: number;
  locationId: number;
  lanes: number;
  coversBothDirections: boolean;
  notes?: string;
}

class TrafficService {
  // ============================================
  // LOCATIONS
  // ============================================
  
  async createLocation(data: CreateLocationData): Promise<Location> {
    const response = await api.post('/api/traffic/locations/', data);
    return response.data;
  }

  async getLocations(): Promise<Location[]> {
    const response = await api.get('/api/traffic/locations/');
    // DRF devuelve un objeto paginado: { count, next, previous, results }
    return response.data.results || response.data;
  }

  async getLocation(locationId: number): Promise<Location> {
    const response = await api.get(`/api/traffic/locations/${locationId}/`);
    return response.data;
  }

  // ============================================
  // CAMERAS
  // ============================================
  
  async createCamera(data: CreateCameraData): Promise<Camera> {
    const response = await api.post('/api/traffic/cameras/', data);
    return response.data;
  }

  async getCameras(): Promise<Camera[]> {
    const response = await api.get('/api/traffic/cameras/');
    // DRF devuelve un objeto paginado: { count, next, previous, results }
    return response.data.results || response.data;
  }

  async getCamera(cameraId: number): Promise<Camera> {
    const response = await api.get(`/api/traffic/cameras/${cameraId}/`);
    return response.data;
  }

  // ============================================
  // TRAFFIC ANALYSIS
  // ============================================
  
  // Create new traffic analysis
  async createAnalysis(data: CreateAnalysisData): Promise<TrafficAnalysis> {
    const response = await api.post('/api/traffic/analysis', data);
    return response.data;
  }

  // Upload video file
  async uploadVideo(analysisId: string, videoFile: File): Promise<{ message: string; file_path: string }> {
    const formData = new FormData();
    formData.append('video_file', videoFile);

    const response = await api.post(`/api/traffic/upload-video/${analysisId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Start video analysis
  async analyzeVideo(analysisId: string): Promise<TrafficAnalysis> {
    const response = await api.post(`/api/traffic/analyze/${analysisId}`);
    return response.data;
  }

  // Get all traffic analyses
  async getAnalyses(params?: {
    location?: string;
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<TrafficAnalysis[]> {
    const response = await api.get('/api/traffic/analysis/', { params });
    // DRF devuelve un objeto paginado: { count, next, previous, results }
    return response.data.results || response.data;
  }

  // Get specific analysis
  async getAnalysis(analysisId: string): Promise<TrafficAnalysis> {
    const response = await api.get(`/api/traffic/analysis/${analysisId}`);
    return response.data;
  }

  // Update analysis
  async updateAnalysis(analysisId: string, data: Partial<TrafficAnalysis>): Promise<TrafficAnalysis> {
    const response = await api.put(`/api/traffic/analysis/${analysisId}`, data);
    return response.data;
  }

  // Delete analysis
  async deleteAnalysis(analysisId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/traffic/analysis/${analysisId}`);
    return response.data;
  }

  // Get traffic predictions
  async getPredictions(location: string, hoursAhead: number = 24): Promise<{
    location: string;
    predictions: TrafficPrediction[];
    generated_at: string;
  }> {
    const response = await api.get('/api/traffic/predictions', {
      params: { location, hours_ahead: hoursAhead }
    });
    return response.data;
  }

  // Get traffic statistics
  async getStatistics(location?: string): Promise<TrafficStatistics> {
    const response = await api.get('/api/traffic/statistics', {
      params: { location }
    });
    return response.data;
  }
}

export const trafficService = new TrafficService();
export default trafficService;