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

