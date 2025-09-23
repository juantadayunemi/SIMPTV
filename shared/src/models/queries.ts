/**
 * Modelos para Queries y Búsquedas
 * Interfaces para operaciones de consulta en la base de datos
 */

import { GroupByDataKey } from "../types/dataTypes";
import { UserRoleType } from "../types/roleTypes";
import { AnalysisStatusKey, DensityLevelKey, NotificationTypeKey, VehicleTypeKey } from "../types/trafficTypes";


// ============= AUTH QUERIES =============

export interface LoginQuery {
  email: string;
  password: string;
}

export interface UserSearchQuery {
  email?: string;
  role?: UserRoleType;
  isActive?: boolean;
  createdAfter?: Date;
  createdBefore?: Date;
  limit?: number;
  offset?: number;
}

// ============= TRAFFIC QUERIES =============

export interface TrafficAnalysisSearchQuery {
  location?: string;
  status?: AnalysisStatusKey;
  densityLevel?: DensityLevelKey;
  vehicleCountMin?: number;
  vehicleCountMax?: number;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
}

export interface VehicleSearchQuery {
  trafficAnalysisId?: string;
  vehicleType?: VehicleTypeKey;
  minConfidence?: number;
  minSpeed?: number;
  maxSpeed?: number;
  startTime?: Date;
  endTime?: Date;
  limit?: number;
  offset?: number;
}

// ============= PLATE QUERIES =============

export interface PlateSearchQuery {
  plateNumber?: string;
  location?: string;
  vehicleType?: VehicleTypeKey;
  minConfidence?: number;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
}

export interface PlateAnalysisQuery {
  plateNumber: string;
  groupByLocation?: boolean;
  groupByDate?: boolean;
  startDate?: Date;
  endDate?: Date;
}

// ============= NOTIFICATION QUERIES =============

export interface NotificationSearchQuery {
  userId?: string;
  type?: NotificationTypeKey;
  isRead?: boolean;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
}

// ============= STATISTICS QUERIES =============

export interface TrafficStatsQuery {
  location?: string;
  startDate: Date;
  endDate: Date;
  groupBy: GroupByDataKey;
}

export interface PlateStatsQuery {
  startDate: Date;
  endDate: Date;
  location?: string;
  vehicleType?: VehicleTypeKey;
  groupBy: GroupByDataKey;
}


