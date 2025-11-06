import { CameraEntity } from '@traffic-analysis/shared';
import api from './api';
import { AnalysisStatusKey, DensityLevelKey } from '@shared/types/trafficTypes';

export interface TrafficAnalysis {
  id: string;
  location: string;
  videoPath?: string;
  vehicleCount: number;
  analysisData?: any;
  status: AnalysisStatusKey;
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
  densityLevel: DensityLevelKey;
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
  
  async createCamera(data: CreateCameraData): Promise<CameraEntity> {
    const response = await api.post('/api/traffic/cameras/', data);
    return response.data;
  }

  async getCameras(): Promise<CameraEntity[]> {
    const response = await api.get('/api/traffic/cameras/');
    // DRF devuelve un objeto paginado: { count, next, previous, results }
    return response.data.results || response.data;
  }

  async getCamera(cameraId: number): Promise<CameraEntity> {
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
  async startVideoAnalysis(formData: FormData): Promise<{ analysisId: number; message: string }> {
    const response = await api.post('/api/traffic/analyze-video/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  
/**
 * Método actualizado para traffic.service.ts
 */

async uploadVideoInChunks(
  videoFile: File,
  cameraId: number,
  locationId: number,
  userId: number,
  onProgress: (progress: number, message: string) => void,
  onChunkComplete: (chunkIndex: number, response: any) => void
): Promise<{ analysisId: string; totalChunks: number }> {
  const CHUNK_SIZE = 1 * 1024 * 1024; // 1MB por chunk
  const totalChunks = Math.ceil(videoFile.size / CHUNK_SIZE);
  
  console.log(`📦 Subiendo video: ${videoFile.name} (${(videoFile.size / (1024 * 1024)).toFixed(2)} MB)`);
  console.log(`📦 Total chunks: ${totalChunks}`);
  
  let analysisId: string | null = null;
  
  for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
    const start = chunkIndex * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, videoFile.size);
    const chunk = videoFile.slice(start, end);
    
    const formData = new FormData();
    formData.append('chunk', chunk);
    formData.append('chunkIndex', chunkIndex.toString());
    formData.append('totalChunks', totalChunks.toString());
    formData.append('fileName', videoFile.name);
    formData.append('cameraId', cameraId.toString());
    formData.append('locationId', locationId.toString());
    formData.append('userId', userId.toString());
    
    // Incluir analysisId después del primer chunk
    if (analysisId) {
      formData.append('analysisId', analysisId);
    }
    
    try {
      const response = await api.post('/api/traffic/upload-chunk/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Guardar analysisId del primer chunk
  
      if (chunkIndex === 0 && response.data.analysisId) {
        analysisId = response.data.analysisId;
        console.log(`✅ TrafficAnalysis creado: ID=${analysisId}`);
      }
      
      // Calcular progreso
      const progress = Math.round(((chunkIndex + 1) / totalChunks) * 100);
      onProgress(progress, `Chunk ${chunkIndex + 1}/${totalChunks} subido`);
      
      onChunkComplete(chunkIndex, response.data);
      
      console.log(`✅ Chunk ${chunkIndex + 1}/${totalChunks} subido (${progress}%)`);
      
    } catch (error) {
      console.error(`❌ Error subiendo chunk ${chunkIndex}:`, error);
      throw error;
    }
  }
  
  if (!analysisId) {
    throw new Error('No se pudo obtener el ID del análisis');
  }
  
  console.log(`✅ Upload completo: analysisId=${analysisId}`);
  
  return {
    analysisId,
    totalChunks
  };
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

   // ============================================
  // ANALYSIS CONTROL (Play/Pause/Resume)
  // ============================================

  // Start analysis (iniciar procesamiento)
  async startAnalysis(analysisId: number): Promise<{
    message: string;
    analysis_id: number;
    task_id: string;
    status: string;
    isPlaying: boolean;
    isPaused: boolean;
  }> {
    const response = await api.post(`/api/traffic/analysis/${analysisId}/start/`);
    return response.data;
  }

  // Clone/Duplicate analysis (crear nuevo análisis con los mismos datos)
  async cloneAnalysis(analysisId: number): Promise<{
    message: string;
    original_analysis_id: number;
    new_analysis_id: number;
    analysis: TrafficAnalysis;
  }> {
    const response = await api.post(`/api/traffic/analysis/${analysisId}/clone/`);
    return response.data;
  }

   // Pause analysis (pausar procesamiento)
  async pauseAnalysis(analysisId: number): Promise<{
    message: string;
    analysis_id: number;
    status: string;
    isPaused: boolean;
    isPlaying: boolean;
  }> {
    const response = await api.post(`/api/traffic/analysis/${analysisId}/pause/`);
    return response.data;
  }


    // Resume analysis (reanudar procesamiento)
  async resumeAnalysis(analysisId: number): Promise<{
    message: string;
    analysis_id: number;
    task_id: string;
    status: string;
    isPaused: boolean;
    isPlaying: boolean;
    resumeFrom: number;
  }> {
    const response = await api.post(`/api/traffic/analysis/${analysisId}/resume/`);
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
  }>): Promise<CameraEntity> {
    const response = await api.patch(`/api/traffic/cameras/${cameraId}/`, data);
    return response.data;
  }
}

export const trafficService = new TrafficService();
export default trafficService;

