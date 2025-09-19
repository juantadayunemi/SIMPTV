/**
 * Entidades de Análisis de Tráfico
 * Modelos para análisis de tráfico vehicular y detección de vehículos
 */

import { AnalysisStatusKey, DensityLevelKey, VehicleTypeKey } from "../types/trafficTypes";

// ============= TRAFFIC ENTITIES =============

export interface TrafficAnalysisEntity {
  id: number;
  location: string;
  videoPath?: string;
  vehicleCount: number;
  avgSpeed?: number;
  densityLevel: DensityLevelKey;
  analysisData?: string; // JSON serialized
  status: AnalysisStatusKey;
  weatherConditions?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface VehicleDetectionEntity {
  id: number;
  trafficAnalysisId: string;
  vehicleType: VehicleTypeKey;
  confidence: number;
  speed?: number;
  boundingBoxX: number;
  boundingBoxY: number;
  boundingBoxWidth: number;
  boundingBoxHeight: number;
  timestamp: Date;
}