/**
 * DTOs Legacy y Específicos
 * DEPRECATED: Usar los nuevos archivos trafficDto.ts, plateDto.ts y commonDto.ts
 * Este archivo se mantiene temporalmente para compatibilidad
 */

import { UserRoleType } from "../types/roleTypes";

// ============= DEPRECATED - Usar commonDto.ts =============

/**
 * @deprecated Usar UserInfoDTO de commonDto.ts
 */
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

/**
 * @deprecated Usar ApiErrorDTO de commonDto.ts
 */
export interface ErrorDTO {
  code: string;
  message: string;
  details?: string;
  field?: string;
  timestamp: Date;
}

// ============= DEPRECATED - Usar trafficDto.ts =============

/**
 * @deprecated Usar TrafficAnalysisResponseDTO de trafficDto.ts
 */
export interface TrafficAnalysisDTO {
  id: string;
  location: string;
  vehicleCount: number;
  avgSpeed?: number;
  densityLevel: any;
  status: any;
  progress?: number;
  weatherConditions?: string;
  vehicleBreakdown: any[];
  peakHours: any[];
  createdAt: Date;
  estimatedCompletion?: Date;
}

// ============= DEPRECATED - Usar plateDto.ts =============

/**
 * @deprecated Usar PlateDetectionResponseDTO de plateDto.ts
 */
export interface PlateDetectionDTO {
  id: string;
  plateNumber: string;
  confidence: number;
  vehicleType?: any;
  location: string;
  boundingBox: any;
  vehicleSpeed?: number;
  createdAt: Date;
  analysisId: string;
}
