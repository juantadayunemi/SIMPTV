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

class TrafficService {
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
    const response = await api.get('/api/traffic/analysis', { params });
    return response.data;
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