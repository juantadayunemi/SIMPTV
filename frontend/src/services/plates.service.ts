import api from './api';
import { PlateDetection } from './traffic.service';

export interface PlateSearchResult {
  plateNumber: string;
  detections: PlateDetection[];
  firstSeen: string;
  lastSeen: string;
  detectionCount: number;
  locations: string[];
}

export interface PlateStatistics {
  totalPlatesDetected: number;
  uniquePlates: number;
  avgConfidenceScore: number;
  mostCommonVehicleType: string;
  detectionsToday: number;
  detectionsThisWeek: number;
  topPlates: Array<{
    plateNumber: string;
    count: number;
    lastSeen: string;
  }>;
}

class PlateService {
  // Get all plate detections
  async getDetections(params?: {
    analysisId?: string;
    plateNumber?: string;
    vehicleType?: string;
    minConfidence?: number;
    page?: number;
    limit?: number;
  }): Promise<PlateDetection[]> {
    const response = await api.get('/api/plates/detections', { params });
    return response.data;
  }

  // Get specific plate detection
  async getDetection(detectionId: string): Promise<PlateDetection> {
    const response = await api.get(`/api/plates/detections/${detectionId}`);
    return response.data;
  }

  // Search plates
  async searchPlates(query: string): Promise<PlateSearchResult[]> {
    const response = await api.get('/api/plates/search', {
      params: { q: query }
    });
    return response.data;
  }

  // Get plate detection history
  async getPlateHistory(plateNumber: string): Promise<{
    plateNumber: string;
    detections: PlateDetection[];
    timeline: Array<{
      date: string;
      count: number;
      locations: string[];
    }>;
  }> {
    const response = await api.get(`/api/plates/history/${encodeURIComponent(plateNumber)}`);
    return response.data;
  }

  // Update plate detection
  async updateDetection(detectionId: string, data: {
    plateNumber?: string;
    vehicleType?: string;
  }): Promise<PlateDetection> {
    const response = await api.put(`/api/plates/detections/${detectionId}`, data);
    return response.data;
  }

  // Delete plate detection
  async deleteDetection(detectionId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/plates/detections/${detectionId}`);
    return response.data;
  }

  // Verify plate detection manually
  async verifyDetection(detectionId: string, isValid: boolean): Promise<PlateDetection> {
    const response = await api.post(`/api/plates/verify/${detectionId}`, {
      is_valid: isValid
    });
    return response.data;
  }

  // Get plate statistics
  async getStatistics(): Promise<PlateStatistics> {
    const response = await api.get('/api/plates/statistics');
    return response.data;
  }

  // Export plate data
  async exportPlates(params?: {
    startDate?: string;
    endDate?: string;
    location?: string;
    format?: 'csv' | 'xlsx';
  }): Promise<Blob> {
    const response = await api.get('/api/plates/export', {
      params,
      responseType: 'blob'
    });
    return response.data;
  }

  // Get detection image
  getDetectionImageUrl(detectionId: string): string {
    return `${api.defaults.baseURL}/api/plates/detections/${detectionId}/image`;
  }

  // Batch process detections
  async batchProcess(detectionIds: string[], action: 'verify' | 'delete' | 'update', data?: any): Promise<{
    processed: number;
    failed: number;
    results: Array<{
      detectionId: string;
      success: boolean;
      error?: string;
    }>;
  }> {
    const response = await api.post('/api/plates/batch', {
      detection_ids: detectionIds,
      action,
      data
    });
    return response.data;
  }
}

export const plateService = new PlateService();
export default plateService;