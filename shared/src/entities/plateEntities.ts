/**
 * Entidades de Detección de Placas
 * Modelos para reconocimiento y análisis de placas vehiculares
 */

import { VehicleTypeKey } from "../types/trafficTypes";

// ============= PLATE ENTITIES =============

export interface PlateDetectionEntity {
  id: string;
  trafficAnalysisId: string;
  plateNumber: string;
  confidence: number;
  vehicleType?: VehicleTypeKey;
  boundingBoxX: number;
  boundingBoxY: number;
  boundingBoxWidth: number;
  boundingBoxHeight: number;
  createdAt: Date;
}

export interface PlateAnalysisEntity {
  id: string;
  plateNumber: string;
  detectionCount: number;
  firstDetected: Date;
  lastDetected: Date;
  locations: string; // JSON array
  vehicleType?: VehicleTypeKey;
}