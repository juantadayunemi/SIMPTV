/**
 * Streaming Models
 * Models for live detection sessions (JSON export system)
 * NO video recording - only detection data saved to JSON
 */

import {
  LiveDetection,
  FrameData,
  DetectionStats,
  VehicleClass
} from '../entities/streamingEntities';

// ============================================
// DETECTION SESSION MODELS (NEW SYSTEM)
// ============================================

/**
 * Structure of the JSON file saved by detection sessions
 * Matches backend: backend/apps/streaming/services/yolo_processor.py
 */
export interface DetectionSessionData {
  video_name: string;           // Camera name
  analysis_id: string;          // Session ID (stream_YYYYMMDDHHMMSS)
  detections: VehicleDetection[];
}

/**
 * Individual vehicle detection saved in JSON
 * Each detection includes a snapshot image saved separately
 */
export interface VehicleDetection {
  vehicle_id: number;
  vehicle_type: VehicleClass;
  plate_number: string;         // "UNREADABLE" or actual plate
  confidence: number;           // 0-1
  detection_method: DetectionMethod;
  image_path: string;           // Full path to vehicle snapshot
  timestamp: string;            // ISO 8601 format
}

export type DetectionMethod = 
  | 'rejected'      // No plate detected (goes to ROI YOLO Streaming)
  | 'triple'        // Plate detected with triple check (goes to Placas Streaming)
  | 'yolo_tracking' // Basic YOLO tracking
  | 'recovered';    // ID recovered by re-identification system

// ============================================
// LIVE STREAMING API MODELS
// ============================================

export interface ProcessFrameRequest {
  frame: string; // base64 encoded image
  cameraId: string;
}

export interface ProcessFrameResponse {
  success: boolean;
  detections: LiveDetection[];
  processingTime: number;
  stats?: DetectionStats;
}

export interface StartSessionRequest {
  cameraId: string;
  cameraName: string;
}

export interface StartSessionResponse {
  sessionId: string;
  message: string;
  paths: {
    json_file: string;
    placas_dir: string;
    roi_dir: string;
  };
}

export interface EndSessionRequest {
  sessionId: string;
}

export interface EndSessionResponse {
  success: boolean;
  json_path: string;
  total_detections: number;
  stats: DetectionStats;
}

// ============================================
// HELPER CLASSES
// ============================================

/**
 * Helper class for working with detection session data
 */
export class DetectionSession {
  video_name: string;
  analysis_id: string;
  detections: VehicleDetection[];

  constructor(data: Partial<DetectionSessionData>) {
    this.video_name = data.video_name || '';
    this.analysis_id = data.analysis_id || '';
    this.detections = data.detections || [];
  }

  get totalDetections(): number {
    return this.detections.length;
  }

  get uniqueVehicles(): number {
    const uniqueIds = new Set(this.detections.map(d => d.vehicle_id));
    return uniqueIds.size;
  }

  get detectionsByType(): Record<VehicleClass, number> {
    return this.detections.reduce((acc, detection) => {
      acc[detection.vehicle_type] = (acc[detection.vehicle_type] || 0) + 1;
      return acc;
    }, {} as Record<VehicleClass, number>);
  }

  get detectionsWithPlate(): VehicleDetection[] {
    return this.detections.filter(d => 
      d.plate_number !== 'UNREADABLE' && 
      d.detection_method === 'triple'
    );
  }

  get detectionsWithoutPlate(): VehicleDetection[] {
    return this.detections.filter(d => 
      d.plate_number === 'UNREADABLE' || 
      d.detection_method === 'rejected'
    );
  }

  get startTime(): string | null {
    if (this.detections.length === 0) return null;
    return this.detections[0].timestamp;
  }

  get endTime(): string | null {
    if (this.detections.length === 0) return null;
    return this.detections[this.detections.length - 1].timestamp;
  }

  get duration(): number {
    const start = this.startTime;
    const end = this.endTime;
    if (!start || !end) return 0;
    
    const startDate = new Date(start);
    const endDate = new Date(end);
    return (endDate.getTime() - startDate.getTime()) / 1000; // seconds
  }

  get durationFormatted(): string {
    const mins = Math.floor(this.duration / 60);
    const secs = Math.floor(this.duration % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
}

/**
 * Helper class for working with individual vehicle detections
 */
export class VehicleDetectionModel implements VehicleDetection {
  vehicle_id: number;
  vehicle_type: VehicleClass;
  plate_number: string;
  confidence: number;
  detection_method: DetectionMethod;
  image_path: string;
  timestamp: string;

  constructor(data: Partial<VehicleDetection>) {
    this.vehicle_id = data.vehicle_id || 0;
    this.vehicle_type = data.vehicle_type || 'car';
    this.plate_number = data.plate_number || 'UNREADABLE';
    this.confidence = data.confidence || 0;
    this.detection_method = data.detection_method || 'rejected';
    this.image_path = data.image_path || '';
    this.timestamp = data.timestamp || new Date().toISOString();
  }

  get hasPlate(): boolean {
    return this.plate_number !== 'UNREADABLE' && 
           this.detection_method === 'triple';
  }

  get confidencePercentage(): string {
    return `${(this.confidence * 100).toFixed(1)}%`;
  }

  get formattedTimestamp(): string {
    const date = new Date(this.timestamp);
    return date.toLocaleString('es-EC', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  get imageFilename(): string {
    return this.image_path.split('\\').pop() || this.image_path.split('/').pop() || '';
  }
}
