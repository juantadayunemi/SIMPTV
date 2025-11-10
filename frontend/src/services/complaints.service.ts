import api from './api';

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface VehicleComplaint {
  id: number;
  complaintText: string;
  complaintType: string | null;
  complaintDate: string | null;
  severity: SeverityLevel | null;
  sequenceNumber: number;
  createdAt: string;
}

export interface DetectionLocation {
  latitude: number;
  longitude: number;
  description: string;
  city?: string;
  province?: string;
  address?: string;
}

export interface VehicleImage {
  path: string;
  capturedAt: string;
  resolution?: string;
}

export interface PlateImage {
  path: string;
  capturedAt: string;
}

export interface DetectionHistoryItem {
  id: number;
  detectedAt: string;
  confidence: number;
  frameNumber: number;
  location: DetectionLocation | null;
}

export interface VehicleComplaintDetection {
  id: number;
  plateNumber: string | null;
  vehicleType: string;
  ownerName: string;
  ownerIdNumber: string;
  ownerAddress: string;
  caseNumber: string;
  totalComplaintsCount: number;
  severity: SeverityLevel | null;
  wasNotified: boolean;
  notifiedAt: string | null;
  notes: string | null;
  detectionDate: string | null;
  createdAt: string;
  complaints: VehicleComplaint[];
}

export interface VehicleComplaintDetectionDetail extends VehicleComplaintDetection {
  location: DetectionLocation | null;
  vehicleImage: VehicleImage | null;
  plateImage: PlateImage | null;
  detectionHistory: DetectionHistoryItem[];
}

export interface ComplaintStats {
  totalComplaints: number;
  mediumPriority: number;
  highPriority: number;
  alertsToday: number;
}

export interface ComplaintFilters {
  search?: string;
  severity?: 'all' | 'LOW' | 'MEDIUM' | 'HIGH';
  notified?: 'all' | 'true' | 'false';
  page?: number;
  limit?: number;
}

class ComplaintsService {
  /**
   * Obtener todas las denuncias de vehículos con filtros opcionales
   */
  async getComplaints(filters?: ComplaintFilters): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: VehicleComplaintDetection[];
  }> {
    const params: any = {};
    
    if (filters?.search) {
      params.search = filters.search;
    }
    
    if (filters?.severity && filters.severity !== 'all') {
      params.severity = filters.severity;
    }
    
    if (filters?.notified && filters.notified !== 'all') {
      params.notified = filters.notified;
    }
    
    if (filters?.page) {
      params.page = filters.page;
    }
    
    if (filters?.limit) {
      params.page_size = filters.limit;
    }

    const response = await api.get('/api/notifications/complaints/', { params });
    return response.data;
  }

  /**
   * Obtener una denuncia específica por ID con todos los detalles
   */
  async getComplaint(complaintId: number): Promise<VehicleComplaintDetectionDetail> {
    const response = await api.get(`/api/notifications/complaints/${complaintId}/`);
    return response.data;
  }

  /**
   * Obtener estadísticas de denuncias
   */
  async getComplaintStats(): Promise<ComplaintStats> {
    const response = await api.get('/api/notifications/complaints/stats/');
    return response.data;
  }
}

export const complaintsService = new ComplaintsService();
export default complaintsService;
