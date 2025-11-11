import { AnalysisStatusKey, DensityLevelKey, VehicleTypeKey } from "../types/trafficTypes";
import { PlateDetection } from "./plateModels";


// ============= BOUNDING BOX =============
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// Traffic Analysis Types
export interface TrafficAnalysis {
  id: string;
  location: string;
  videoPath?: string;
  vehicleCount: number;
  analysisData?: TrafficData;
  status: AnalysisStatusKey;
  plateDetections: PlateDetection[];
  createdAt: Date;
}

export interface TrafficData {
  totalVehicles: number;
  vehicleTypes: VehicleTypeCount[];
  avgSpeed: number;
  peakHours: TimeSlot[];
  densityLevel: DensityLevelKey;
  weatherConditions?: string;
}

export interface VehicleTypeCount {
  type: VehicleTypeKey;
  count: number;
}

export interface VehicleDetection {
  id: string;
  type: VehicleTypeKey;
  confidence: number;
  boundingBox: BoundingBox;
  speed?: number;
  timestamp: Date;
}

export interface TimeSlot {
  startTime: string;
  endTime: string;
  vehicleCount: number;
}

export interface PredictiveAnalysis {
  id: string;
  location: string;
  predictedTraffic: TrafficPrediction[];
  confidence: number;
  createdAt: Date;
}

export interface TrafficPrediction {
  timeSlot: string;
  predictedVehicles: number;
  densityLevel:DensityLevelKey;
  confidence: number;
}


// ============================================
// INTERFACES DE DETECCIÓN EN TIEMPO REAL
// ============================================

export interface RealtimeDetectionEvent {
  timestamp: Date;                  // Timestamp de la detección
  frameNumber: number;              // Número de frame
  vehicleType: VehicleTypeKey;      // Tipo de vehículo
  plateNumber?: string;             // Número de placa (si se detectó)
  confidence: number;               // Confianza de detección de vehículo (0-1)
  plateConfidence?: number;         // Confianza de detección de placa (0-1)
  trackId: string;                  // ID único de tracking del vehículo
  bbox: {
    x: number;                      // Posición X del bounding box
    y: number;                      // Posición Y del bounding box
    width: number;                  // Ancho del bounding box
    height: number;                 // Alto del bounding box
  };
}

export interface VideoAnalysisProgress {
  analysisId: number;               // ID del análisis
  currentFrame: number;             // Frame actual
  totalFrames: number;              // Total de frames
  progress: number;                 // Progreso en porcentaje (0-100)
  vehiclesDetected: number;         // Vehículos detectados hasta ahora
  platesDetected: number;           // Placas detectadas hasta ahora
  currentTimestamp: number;         // Timestamp actual del video en segundos
  fps: number;                      // FPS de procesamiento
  isPlaying: boolean;               // Si está reproduciéndose
  isPaused: boolean;                // Si está pausado
}