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

export interface Camera {
  id: number;
  name: string;
  brand?: string;
  model?: string;
  resolution?: string;
  fps?: number;
  locationId: number;
  status: string;
  lanes: number;
  coversBothDirections: boolean;
  notes?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
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

  // (Eliminado: uploadVideo, ya no se usa para este flujo)

  // Start video analysis
  async analyzeVideo(analysisId: string): Promise<TrafficAnalysis> {
    const response = await api.post(`/api/traffic/analyze/${analysisId}`);
    return response.data;
  }

  // Start video analysis (combined upload + process)
  async startVideoAnalysis(formData: FormData): Promise<{ id: number; message: string }> {
    const response = await api.post('/api/traffic/analyze-video/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Upload video in chunks with real-time analysis
  async uploadVideoInChunks(
    file: File,
    cameraId: number,
    locationId: number,
    userId: number,
    weatherConditions: string = '',
    onProgress?: (progress: number, message: string) => void,
    onChunkComplete?: (chunkIndex: number, response: any) => void
  ): Promise<{ analysisId: string; finalResponse: any }> {
    const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    const analysisId = crypto.randomUUID(); // Generate unique analysis ID

    onProgress?.(0, `Iniciando subida de ${totalChunks} chunks...`);

    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
      const start = chunkIndex * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const chunk = file.slice(start, end);

      const formData = new FormData();
      formData.append('analysisId', analysisId);
      formData.append('chunkIndex', chunkIndex.toString());
      formData.append('totalChunks', totalChunks.toString());
      formData.append('file', chunk, `chunk_${chunkIndex}.mp4`);
      formData.append('cameraId', cameraId.toString());
      formData.append('locationId', locationId.toString());
      formData.append('userId', userId.toString());
      formData.append('weatherConditions', weatherConditions);

      try {
        const response = await api.post('/api/traffic/upload-chunk/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const progress = Math.round(((chunkIndex + 1) / totalChunks) * 100);
        const message = chunkIndex === 0 
          ? 'Primer chunk enviado - análisis iniciado!' 
          : `Chunk ${chunkIndex + 1}/${totalChunks} completado`;

        onProgress?.(progress, message);
        onChunkComplete?.(chunkIndex, response.data);

        // Small delay between chunks to avoid overwhelming the server
        if (chunkIndex < totalChunks - 1) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (error) {
        console.error(`Error uploading chunk ${chunkIndex}:`, error);
        throw new Error(`Failed to upload chunk ${chunkIndex}: ${error}`);
      }
    }

    // Get final analysis status
    try {
      const finalResponse = await this.getAnalysis(analysisId);
      onProgress?.(100, 'Análisis completado!');
      return { analysisId, finalResponse };
    } catch (error) {
      console.warn('Could not get final analysis status:', error);
      return { analysisId, finalResponse: null };
    }
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

  // Update camera (status, name, location)
  async updateCamera(cameraId: string | number, data: Partial<{
    name: string;
    location: string;
    status: 'active' | 'inactive' | 'maintenance';
    locationId?: number;
    brand?: string;
    model?: string;
    resolution?: string;
    fps?: number;
    lanes?: number;
    coversBothDirections?: boolean;
    notes?: string;
  }>): Promise<Camera> {
    const response = await api.patch(`/api/traffic/cameras/${cameraId}/`, data);
    return response.data;
  }
}

export const trafficService = new TrafficService();
export default trafficService;