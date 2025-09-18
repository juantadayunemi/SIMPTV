/**
 * DTOs para el Frontend
 * Objetos de transferencia de datos optimizados para la presentación
 */

import { UserRoleType } from "../types/roleTypes";
import { AnalysisStatusKey, DensityLevelKey, NotificationTypeKey, VehicleTypeKey } from "../types/trafficTypes";



// ============= AUTH DTOs =============

export interface UserDTO {
  id: string;
  email: string;
  fullName?: string;
  role: UserRoleType;
  permissions: string[];
  isActive: boolean;
  lastLogin?: Date;
  createdAt: Date;
}

export interface LoginResponseDTO {
  accessToken: string;
  refreshToken: string;
  user: UserDTO;
  expiresAt: Date;
}

export interface AuthTokenDTO {
  accessToken: string;
  refreshToken?: string;
  tokenType: 'Bearer';
  expiresIn: number;
}

// ============= TRAFFIC DTOs =============

export interface TrafficAnalysisDTO {
  id: string;
  location: string;
  vehicleCount: number;
  avgSpeed?: number;
  densityLevel: DensityLevelKey;
  status: AnalysisStatusKey;
  progress?: number; // Para análisis en proceso
  weatherConditions?: string;
  vehicleBreakdown: VehicleTypeBreakdownDTO[];
  peakHours: TimeSlotDTO[];
  createdAt: Date;
  estimatedCompletion?: Date;
}

export interface VehicleTypeBreakdownDTO {
  type: VehicleTypeKey;
  count: number;
  percentage: number;
}

export interface TimeSlotDTO {
  startTime: string;
  endTime: string;
  vehicleCount: number;
  avgSpeed?: number;
}

export interface VehicleDetectionDTO {
  id: string;
  vehicleType: VehicleTypeKey;
  confidence: number;
  speed?: number;
  boundingBox: BoundingBoxDTO;
  timestamp: Date;
  plateDetected?: boolean;
}

export interface BoundingBoxDTO {
  x: number;
  y: number;
  width: number;
  height: number;
}

// ============= PLATE DTOs =============

export interface PlateDetectionDTO {
  id: string;
  plateNumber: string;
  confidence: number;
  vehicleType?: VehicleTypeKey;
  location: string;
  boundingBox: BoundingBoxDTO;
  vehicleSpeed?: number;
  createdAt: Date;
  analysisId: string;
}

export interface PlateAnalysisSummaryDTO {
  plateNumber: string;
  totalDetections: number;
  firstSeen: Date;
  lastSeen: Date;
  locations: string[];
  avgConfidence: number;
  vehicleType?: VehicleTypeKey;
  frequentLocations: LocationFrequencyDTO[];
}

export interface LocationFrequencyDTO {
  location: string;
  count: number;
  percentage: number;
  lastSeen: Date;
}

// ============= NOTIFICATION DTOs =============

export interface NotificationDTO {
  id: string;
  type: NotificationTypeKey;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  isRead: boolean;
  readAt?: Date;
  createdAt: Date;
  actionUrl?: string;
  metadata?: Record<string, any>;
}

export interface NotificationSummaryDTO {
  total: number;
  unread: number;
  byType: NotificationTypeCountDTO[];
  recent: NotificationDTO[];
}

export interface NotificationTypeCountDTO {
  type: NotificationTypeKey;
  count: number;
  unreadCount: number;
}

// ============= DASHBOARD DTOs =============

export interface DashboardStatsDTO {
  traffic: TrafficStatsDTO;
  plates: PlateStatsDTO;
  system: SystemStatsDTO;
  notifications: NotificationSummaryDTO;
  lastUpdated: Date;
}

export interface TrafficStatsDTO {
  totalAnalyses: number;
  activeAnalyses: number;
  totalVehicles: number;
  avgDailyTraffic: number;
  topLocations: LocationStatsDTO[];
  hourlyTrend: HourlyTrendDTO[];
}

export interface PlateStatsDTO {
  totalDetections: number;
  uniquePlates: number;
  avgConfidence: number;
  topPlates: PlateFrequencyDTO[];
  detectionTrend: DailyTrendDTO[];
}

export interface SystemStatsDTO {
  uptime: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  activeUsers: number;
  totalUsers: number;
}

export interface LocationStatsDTO {
  location: string;
  analysisCount: number;
  avgVehicles: number;
  lastActivity: Date;
}

export interface HourlyTrendDTO {
  hour: number;
  vehicleCount: number;
  analysisCount: number;
}

export interface DailyTrendDTO {
  date: Date;
  count: number;
}

export interface PlateFrequencyDTO {
  plateNumber: string;
  detectionCount: number;
  locations: string[];
  lastSeen: Date;
}

// ============= ERROR DTOs =============

export interface ErrorDTO {
  code: string;
  message: string;
  details?: string;
  field?: string;
  timestamp: Date;
}

export interface ValidationErrorDTO extends ErrorDTO {
  field: string;
  value: any;
  constraints: string[];
}

// ============= API RESPONSE DTOs =============

export interface ApiResponseDTO<T = any> {
  success: boolean;
  data?: T;
  error?: ErrorDTO;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponseDTO<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  filters?: Record<string, any>;
}

// ============= PAGINATION =============

export interface PaginationQueryDto {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
