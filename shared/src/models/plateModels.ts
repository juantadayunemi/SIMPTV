import { BoundingBox } from "./trafficModels";

// Plate Detection Types
export interface PlateDetection {
  id: string;
  plateNumber: string;
  confidence: number;
  boundingBox: BoundingBox;
  vehicleType?: string;
  trafficAnalysisId: string;
  createdAt: Date;
}

export interface PlateRecognitionResult {
  text: string;
  confidence: number;
  characters: CharacterDetection[];
}

export interface CharacterDetection {
  character: string;
  confidence: number;
  position: BoundingBox;
}

export interface PlateAnalysis {
  id: string;
  plateNumber: string;
  detectionCount: number;
  firstDetected: Date;
  lastDetected: Date;
  locations: string[];
  vehicleType?: string;
}

export interface PlateStatistics {
  totalDetections: number;
  uniquePlates: number;
  avgConfidence: number;
  detectionsByHour: HourlyDetection[];
  topLocations: LocationCount[];
}

export interface HourlyDetection {
  hour: number;
  count: number;
}

export interface LocationCount {
  location: string;
  count: number;
}