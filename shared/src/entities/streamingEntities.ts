/**
 * Streaming Entities
 * Core entities for live streaming detection (no video recording)
 */

// ============================================
// LIVE DETECTION ENTITIES
// ============================================

/**
 * Real-time detection from YOLO + Norfair tracking
 * Sent via WebSocket to frontend during streaming
 */
export interface LiveDetection {
  id: number;                    // Vehicle tracking ID from Norfair
  label: VehicleClass;          // Type of vehicle detected
  confidence: number;           // Detection confidence (0-1)
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  centroid: [number, number];   // [x, y] center point
  in_roi: boolean;              // Whether vehicle is in ROI
  recovered?: boolean;          // True if ID was recovered by re-identification
}

/**
 * Supported vehicle types
 */
export type VehicleClass = 
  | 'car' 
  | 'truck' 
  | 'bus' 
  | 'motorcycle' 
  | 'bicycle';

/**
 * Frame processing data
 * Contains detections for a single video frame
 */
export interface FrameData {
  frame_number: number;
  timestamp: string;            // ISO 8601 format
  detections: LiveDetection[];
  fps: number;
}

/**
 * Detection statistics during streaming
 * Real-time stats sent via WebSocket
 */
export interface DetectionStats {
  unique_objects: number;                      // Total unique vehicle IDs tracked
  total_detections: number;                    // Total detection events
  frames_processed: number;                    // Total frames analyzed
  average_objects_per_frame: number;           // Average detections per frame
  objects_by_class: Record<VehicleClass, number>; // Count by vehicle type
  elapsed_time: number;                        // Seconds since streaming started
}
