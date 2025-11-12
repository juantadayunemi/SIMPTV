"""
YOLO Processor for Real-Time Streaming with Norfair Tracking
Detects vehicles, tracks them with unique IDs using centroid-based tracking
Optimized for toy vehicles (Hot Wheels) and real vehicles
"""
import cv2
import numpy as np
import logging
from typing import Optional
import base64
from ultralytics import YOLO
import torch
from django.conf import settings
import os
import json
from pathlib import Path
from datetime import datetime
from norfair import Detection, Tracker
from norfair.distances import mean_euclidean
from norfair.filter import OptimizedKalmanFilterFactory

os.environ["ULTRALYTICS_NO_UPDATE"] = "1"

logger = logging.getLogger(__name__)


class YOLOProcessor:
    """
    Real-time YOLO detection processor with vehicle tracking
    Processes frames, applies filters, tracks objects with persistent IDs
    """
    
    VEHICLE_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
        1: "bicycle",
    }
    
    COLORS = {
        "car": (0, 255, 0),
        "motorcycle": (255, 0, 0),
        "bus": (0, 0, 255),
        "truck": (0, 165, 255),
        "bicycle": (255, 255, 0),
        "other": (128, 128, 128),
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.80,  # Aumentado de 0.75 a 0.80 para reducir falsos positivos
        device: str = "auto"
    ):
        """
        Initialize YOLO processor with Norfair tracking
        Higher confidence threshold reduces false positives
        """
        self.confidence_threshold = confidence_threshold
        
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"YOLOProcessor initializing on device: {self.device}")
        logger.info(f"Confidence threshold: {self.confidence_threshold}")
        
        if model_path is None:
            model_path = str(settings.YOLO_STREAMING_MODEL_PATH)
        
        logger.info(f"Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        # Initialize Norfair Tracker with Optimized Kalman Filter
        # Kalman Filter adds motion prediction for better ID stability
        # Parameters optimized for rapid movements and direction changes
        self.tracker = Tracker(
            distance_function=mean_euclidean,
            distance_threshold=100,     # ⬆️ Increased from 50 (more permissive for rapid movements)
            hit_counter_max=30,         # ⬆️ Increased from 15 (keeps IDs longer during occlusions)
            initialization_delay=2,     # ⬆️ Increased from 1 (more conservative, reduces false IDs)
            past_detections_length=10,  # ⬆️ Increased from 5 (better velocity estimation for turns)
            filter_factory=OptimizedKalmanFilterFactory()  # ⭐ KALMAN FILTER
        )
        
        # Lost tracks history for ID recovery (re-identification)
        self.lost_tracks_history = {}
        self.max_lost_frames = 30  # Keep lost IDs for 30 frames (~1 second at 30fps)
        self.tracked_bboxes = {}   # Store last known bbox for each ID
        
        logger.info("Norfair Tracker initialized with Kalman Filter + ID Recovery")
        logger.info("- Distance function: Euclidean (centroid-based)")
        logger.info("- Distance threshold: 100 pixels (optimized for rapid movements)")
        logger.info("- Hit counter max: 30 frames (better occlusion handling)")
        logger.info("- Initialization delay: 2 frames (reduces false positives)")
        logger.info("- Past detections: 10 frames (better velocity for turns)")
        logger.info("- Kalman Filter: ENABLED (motion prediction + smoothing)")
        logger.info("- ID Recovery: ENABLED (re-identifies lost tracks within 30 frames)")
        
        self.frame_count = 0
        self.detection_count = 0
        self.unique_vehicles = set()
        
        # ROI (Region of Interest) configuration
        # Default: Lower 65% of frame (from 35% height to bottom)
        self.roi_enabled = True
        self.roi_y_min = 0.35  # Start ROI at 35% of frame height
        
        # Streaming session data (for JSON export)
        self.session_id = None
        self.camera_name = None
        self.session_detections = []  # List of all detections for JSON export
        self.session_start_time = None
        
        logger.info("YOLO model loaded successfully")
        logger.info(f"Available classes: {self.model.names}")
        logger.info(f"ROI enabled: {self.roi_enabled} (y >= {self.roi_y_min * 100:.0f}%)")
    
    def es_carro_valido(self, box, frame_height, class_name="car"):
        """
        Validate vehicle detection with intelligent filters
        Supports both lateral and frontal views with adaptive thresholds
        """
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        ratio = w / h
        area = w * h

        # Detect vehicle orientation
        # Frontal view: height > width (h/w > 1.2)
        # Lateral view: width > height (w/h > 1.2)
        is_frontal = h > w * 1.2  # Vehicle facing camera (more vertical)
        is_lateral = w > h * 1.2  # Vehicle from side (more horizontal)
        
        # Filter 3: Vertical zone (focus on road area) - APPLIES TO ALL
        if y2 < frame_height * 0.35:
            logger.debug(f"Rejected - high zone: y2={y2} < {frame_height * 0.35:.0f}")
            return False
        
        # FRONTAL VIEW DETECTION (relaxed filters for Hot Wheels frontal)
        if is_frontal:
            # Filter 1F: Minimum area for frontal view (RELAXED)
            min_area_frontal = 4000  # Was 8000, now 4000 (allows 60x90 = 5400px²)
            if area < min_area_frontal:
                logger.debug(f"Rejected - small frontal area: {area:.0f} < {min_area_frontal}")
                return False
            
            # Filter 2F: Frontal aspect ratio (h/w should be > 1.2)
            if ratio > 0.9:  # If ratio w/h > 0.9, it's too square/wide for frontal
                logger.debug(f"Rejected - frontal not vertical enough: ratio={ratio:.2f} > 0.9")
                return False
            
            # Filter 3F: Minimum width for frontal (RELAXED)
            min_width_frontal = 40  # Was 80, now 40 (allows thin frontal view)
            if w < min_width_frontal:
                logger.debug(f"Rejected - frontal too thin: width={w:.0f} < {min_width_frontal}")
                return False
            
            # Filter 4F: Minimum height for frontal
            if h < 60:
                logger.debug(f"Rejected - frontal too short: height={h:.0f} < 60")
                return False
            
            # Filter 5F: Maximum height (avoid very tall objects)
            if h > 150:
                logger.debug(f"Rejected - frontal too tall: height={h:.0f} > 150")
                return False
            
            logger.debug(f"✅ Frontal detection: {class_name} @ ({int(x1)},{int(y1)}) size=({int(w)}x{int(h)}), area={int(area)}px²")
            return True
        
        # LATERAL VIEW DETECTION (strict filters as before)
        else:
            # Filter 1L: Minimum area for lateral view (STRICT)
            if area < 8000:  # Mantiene filtro estricto para vista lateral
                logger.debug(f"Rejected - small lateral area: {area:.0f} < 8000")
                return False
            
            # Filter 2L: Lateral aspect ratio (w/h should be > 1.2)
            if ratio < 1.2 or ratio > 3.2:
                logger.debug(f"Rejected - invalid lateral ratio: {ratio:.2f} outside 1.2-3.2")
                return False
            
            # Filter 3L: Anti-square objects (faces, non-vehicles)
            if 0.85 < ratio < 1.25 and area < 12000:
                logger.debug(f"Rejected - square object: ratio={ratio:.2f}, area={area:.0f}")
                return False
            
            # Filter 4L: Excessive height (vertical objects - but allow some tolerance)
            if h > w * 1.5:  # Increased from 1.3 to 1.5 for tolerance
                logger.debug(f"Rejected - excessive height: h={h:.0f} > w*1.5={w*1.5:.0f}")
                return False
            
            # Filter 5L: Minimum width for lateral (STRICT)
            if w < 80:
                logger.debug(f"Rejected - lateral too thin: width={w:.0f} < 80")
                return False
            
            # Filter 6L: Minimum height for lateral
            if h < 50:
                logger.debug(f"Rejected - lateral too short: height={h:.0f} < 50")
                return False
            
            logger.debug(f"✅ Lateral detection: {class_name} @ ({int(x1)},{int(y1)}) size=({int(w)}x{int(h)}), area={int(area)}px²")
            return True
    
    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, list]:
        """
        Process frame with YOLO detection and Norfair tracking
        Returns annotated frame and detection list with persistent IDs using centroid tracking
        """
        self.frame_count += 1
        
        # Run YOLO inference (optimized for speed)
        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            verbose=False,
            agnostic_nms=True,
            max_det=10
        )
        
        # Prepare detections for Norfair (centroid-based tracking)
        norfair_detections = []
        detection_metadata = []  # Store class and confidence separately
        
        logger.info(f"Frame {self.frame_count} processing...")
        
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = self.model.names[cls]
                
                logger.debug(f"Raw detection: {label} conf={conf:.2f} bbox=[{int(x1)},{int(y1)},{int(x2)},{int(y2)}]")
                
                # Apply validation filters
                if not self.es_carro_valido((x1, y1, x2, y2), frame.shape[0]):
                    logger.debug(f"Filtered: {label} failed validation")
                    continue
                
                logger.debug(f"Accepted: {label} {conf:.2f}")
                
                # Calculate centroid for Norfair tracking
                centroid_x = (x1 + x2) / 2
                centroid_y = (y1 + y2) / 2
                
                # Create Norfair Detection with centroid
                norfair_detection = Detection(
                    points=np.array([[centroid_x, centroid_y]]),
                    scores=np.array([conf])
                )
                
                norfair_detections.append(norfair_detection)
                detection_metadata.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "class": label,
                    "confidence": conf
                })
        
        # Update Norfair tracker with centroid detections
        tracked_objects = self.tracker.update(detections=norfair_detections)
        
        logger.info(f"YOLO detections: {len(norfair_detections)} -> Tracked objects: {len(tracked_objects)}")
        
        # Draw tracked objects with persistent IDs
        annotated_frame = frame.copy()
        detections = []
        
        # Draw ROI (Region of Interest) rectangle
        if self.roi_enabled:
            frame_height = frame.shape[0]
            roi_y_start = int(frame_height * self.roi_y_min)
            # Draw semi-transparent ROI overlay
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (0, roi_y_start), (frame.shape[1], frame_height), (0, 255, 0), 2)
            cv2.putText(overlay, "ROI: Detection Zone", (10, roi_y_start - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # Blend with original
            cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
        
        # Match tracked objects with detection metadata
        for idx, track in enumerate(tracked_objects):
            # Norfair tracks are always active if returned
            track_id = track.id
            
            # Get metadata if available (fallback for new tracks)
            if idx < len(detection_metadata):
                metadata = detection_metadata[idx]
                x1, y1, x2, y2 = metadata["bbox"]
                label = metadata["class"]
                confidence = metadata["confidence"]
            else:
                # Track sin detección actual - NO DIBUJAR (evita cuadraditos falsos)
                logger.debug(f"Track {track_id} without current detection - skipping draw")
                continue
            
            # RE-VALIDAR bbox antes de dibujar (elimina cuadraditos pequeños residuales)
            if not self.es_carro_valido((x1, y1, x2, y2), frame.shape[0]):
                logger.debug(f"Track {track_id} bbox failed validation - skipping")
                continue
            
            self.unique_vehicles.add(track_id)
            color = self._get_color_for_id(track_id)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with ID and confidence
            confidence_pct = int(confidence * 100)
            text = f"ID#{track_id} {label} {confidence_pct}%"
            cv2.putText(
                annotated_frame,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
            
            detections.append({
                "id": int(track_id),
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "class": label,
                "confidence": float(confidence),
                "age": track.age  # Frames since track was created
            })
        
        # ⭐ APPLY ID RECOVERY: Attempt to recover lost IDs before finalizing
        detections = self._recover_lost_ids(detections)
        
        # ⭐ SAVE DETECTIONS TO SESSION (for JSON export)
        for detection in detections:
            self.add_detection_to_session(frame, detection)
        
        if len(detections) > 0:
            logger.info(f"Tracked: {len(detections)} objects | Unique total: {len(self.unique_vehicles)}")
        
        self.detection_count += len(detections)
        
        return annotated_frame, detections
    
    def _bbox_distance(self, bbox1: tuple, bbox2: tuple) -> float:
        """
        Calculate Euclidean distance between centroids of two bounding boxes
        Used for lost track re-identification
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate centroids
        cx1 = (x1_1 + x2_1) / 2
        cy1 = (y1_1 + y2_1) / 2
        cx2 = (x1_2 + x2_2) / 2
        cy2 = (y1_2 + y2_2) / 2
        
        # Euclidean distance
        return np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
    
    def _calculate_bbox_features(self, bbox_xyxy: tuple) -> dict:
        """
        Calculate physical features of a bounding box
        Used for intelligent ID recovery matching
        """
        x1, y1, x2, y2 = bbox_xyxy
        width = x2 - x1
        height = y2 - y1
        area = width * height
        aspect_ratio = width / height if height > 0 else 0
        
        return {
            'area': area,
            'aspect_ratio': aspect_ratio,
            'width': width,
            'height': height
        }
    
    def _calculate_matching_score(self, bbox1: tuple, bbox2: tuple, frames_lost: int) -> tuple:
        """
        Calculate intelligent matching score between two bboxes
        Uses multiple features: position, area, aspect ratio, time
        
        Returns: (score, details_dict)
        Score range: 0.0 (no match) to 1.0 (perfect match)
        """
        # 1. Position similarity (centroid distance)
        distance = self._bbox_distance(bbox1, bbox2)
        max_distance = 200  # Maximum acceptable distance in pixels
        position_score = max(0, 1 - (distance / max_distance))
        
        # 2. Area similarity
        features1 = self._calculate_bbox_features(bbox1)
        features2 = self._calculate_bbox_features(bbox2)
        
        area_diff = abs(features1['area'] - features2['area'])
        max_area = max(features1['area'], features2['area'])
        area_score = max(0, 1 - (area_diff / max_area)) if max_area > 0 else 0
        
        # 3. Aspect ratio similarity
        ratio_diff = abs(features1['aspect_ratio'] - features2['aspect_ratio'])
        max_ratio_diff = 2.0  # Maximum acceptable difference
        aspect_score = max(0, 1 - (ratio_diff / max_ratio_diff))
        
        # 4. Time penalty (prefer recently lost tracks)
        time_score = max(0, 1 - (frames_lost / self.max_lost_frames))
        
        # Weighted combination
        # Position is most important (30%), then area and aspect (25% each), time (20%)
        final_score = (
            0.30 * position_score +
            0.25 * area_score +
            0.25 * aspect_score +
            0.20 * time_score
        )
        
        details = {
            'position': round(position_score, 2),
            'area': round(area_score, 2),
            'aspect': round(aspect_score, 2),
            'time': round(time_score, 2),
            'distance_px': round(distance, 1),
            'area_diff': round(area_diff, 0),
            'ratio_diff': round(ratio_diff, 2)
        }
        
        return final_score, details
    
    def _recover_lost_ids(self, detections: list) -> list:
        """
        Intelligent ID recovery using multiple features
        Prevents ID switches when vehicles temporarily lose tracking
        
        Strategy:
        1. Check if current detection is "new" (first time seen)
        2. Search in lost_tracks_history for recently lost IDs
        3. Calculate matching score using position, area, aspect ratio, time
        4. If score > 0.65 (65% confidence), recover old ID
        5. Otherwise, accept new ID
        """
        current_ids = {det["id"] for det in detections}
        recovered_detections = []
        
        # Update lost_tracks_history: increment frames_lost for all lost tracks
        for lost_id in list(self.lost_tracks_history.keys()):
            if lost_id in current_ids:
                # ID recovered by tracker, remove from lost
                del self.lost_tracks_history[lost_id]
                logger.debug(f"ID {lost_id} naturally recovered by tracker")
            else:
                # Increment lost frame counter
                self.lost_tracks_history[lost_id]['frames_lost'] += 1
                
                # Remove if lost for too long
                if self.lost_tracks_history[lost_id]['frames_lost'] > self.max_lost_frames:
                    logger.debug(f"ID {lost_id} expired after {self.max_lost_frames} frames")
                    del self.lost_tracks_history[lost_id]
        
        # Process each detection
        for det in detections:
            track_id = det["id"]
            bbox = det["bbox"]
            
            # Convert bbox from [x, y, w, h] to [x1, y1, x2, y2]
            x1, y1, w, h = bbox
            x2, y2 = x1 + w, y1 + h
            bbox_xyxy = (x1, y1, x2, y2)
            
            # Calculate features for current detection
            current_features = self._calculate_bbox_features(bbox_xyxy)
            
            # Check if this is a NEW ID (never seen before)
            if track_id not in self.tracked_bboxes:
                # Search for recently lost IDs that might match
                best_match_id = None
                best_score = 0.0
                best_details = None
                
                for lost_id, lost_data in self.lost_tracks_history.items():
                    last_bbox = lost_data['last_bbox']
                    frames_lost = lost_data['frames_lost']
                    
                    # Calculate intelligent matching score
                    score, details = self._calculate_matching_score(
                        bbox_xyxy, 
                        last_bbox, 
                        frames_lost
                    )
                    
                    # Keep best match
                    if score > best_score:
                        best_score = score
                        best_match_id = lost_id
                        best_details = details
                
                # Recovery threshold: 0.65 (65% confidence)
                RECOVERY_THRESHOLD = 0.65
                
                # If found a good match, RECOVER the old ID
                if best_match_id is not None and best_score > RECOVERY_THRESHOLD:
                    logger.info(
                        f"🔄 Recovered ID {best_match_id} (was {track_id}, score={best_score:.2f}, "
                        f"pos={best_details['position']}, area={best_details['area']}, "
                        f"aspect={best_details['aspect']}, time={best_details['time']})"
                    )
                    det["id"] = best_match_id
                    det["recovered"] = True
                    
                    # Remove from lost_tracks (now recovered)
                    del self.lost_tracks_history[best_match_id]
                    
                    # Update tracked_bboxes with recovered ID
                    self.tracked_bboxes[best_match_id] = {
                        'bbox': bbox_xyxy,
                        'features': current_features
                    }
                else:
                    # Accept as genuinely new ID
                    if best_match_id is not None:
                        logger.debug(
                            f"⚠️ Low recovery confidence: ID {best_match_id} score={best_score:.2f} < {RECOVERY_THRESHOLD} (not recovered)"
                        )
                    logger.debug(f"✅ New ID {track_id} accepted (no lost match)")
                    self.tracked_bboxes[track_id] = {
                        'bbox': bbox_xyxy,
                        'features': current_features
                    }
            else:
                # Existing ID, update bbox and features
                self.tracked_bboxes[track_id] = {
                    'bbox': bbox_xyxy,
                    'features': current_features
                }
            
            recovered_detections.append(det)
        
        # Add disappeared IDs to lost_tracks_history
        previous_ids = set(self.tracked_bboxes.keys())
        disappeared_ids = previous_ids - current_ids
        
        for disappeared_id in disappeared_ids:
            if disappeared_id not in self.lost_tracks_history:
                bbox_data = self.tracked_bboxes[disappeared_id]
                logger.debug(f"ID {disappeared_id} lost - adding to recovery history")
                self.lost_tracks_history[disappeared_id] = {
                    'last_bbox': bbox_data['bbox'] if isinstance(bbox_data, dict) else bbox_data,
                    'frames_lost': 1
                }
        
        return recovered_detections
    
    def _get_color_for_id(self, obj_id: int) -> tuple:
        """
        Generate consistent color for each object ID
        Same ID always returns same color (BGR format)
        """
        colors = [
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 255, 255),
            (255, 0, 255),
            (255, 255, 0),
            (128, 0, 128),
            (0, 165, 255),
            (203, 192, 255),
            (0, 128, 0),
        ]
        return colors[obj_id % len(colors)]
    
    def encode_frame_to_base64(self, frame: np.ndarray, quality: int = 80) -> str:
        """
        Encode frame to base64 JPEG for WebSocket transmission
        Lower quality for faster processing and transmission
        """
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text
    
    def process_and_encode(self, frame: np.ndarray, quality: int = 80) -> dict:
        """
        Process frame with YOLO detection and tracking, then encode for transmission
        Optimized for performance with reduced quality
        """
        annotated_frame, detections = self.process_frame(frame)
        encoded_frame = self.encode_frame_to_base64(annotated_frame, quality)
        
        return {
            "frame": encoded_frame,
            "detections": detections,
            "frame_count": self.frame_count,
            "detection_count": len(detections)
        }
    
    def start_session(self, camera_name: str):
        """
        Start a new streaming session
        Initialize session variables for data collection
        """
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.camera_name = camera_name
        self.session_start_time = datetime.now()
        self.session_detections = []
        self.session_vehicle_ids = set()  # Track which vehicle IDs have been saved
        
        # Create session directories
        session_folder_name = f"{camera_name}_stream_{self.session_id}"
        self.session_placas_dir = settings.STREAMING_PLACAS_DIR / session_folder_name
        self.session_roi_dir = settings.STREAMING_ROI_DIR / session_folder_name
        
        self.session_placas_dir.mkdir(parents=True, exist_ok=True)
        self.session_roi_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📝 Session {self.session_id} started for {camera_name}")
    
    def _save_vehicle_snapshot(self, frame: np.ndarray, detection: dict) -> str:
        """
        Save vehicle snapshot image to appropriate directory
        Returns the full path to saved image
        """
        if not hasattr(self, 'session_id') or self.session_id is None:
            logger.warning("No active session - snapshot not saved")
            return ""
        
        vehicle_id = detection["id"]
        vehicle_type = detection["class"]
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Extract bbox from detection
        x, y, w, h = detection["bbox"]
        x1, y1, x2, y2 = int(x), int(y), int(x + w), int(y + h)
        
        # Crop vehicle from frame
        vehicle_crop = frame[y1:y2, x1:x2]
        
        # For now, all go to ROI YOLO Streaming (rejected)
        # In future: if plate_detected → Placas Streaming
        detection_method = "rejected"  # Default until OCR integration
        suffix = "vehiculo"
        save_dir = self.session_roi_dir
        
        # Generate filename: ID_type_timestamp_suffix.jpg
        filename = f"{vehicle_id}_{vehicle_type}_{timestamp_str}_{suffix}.jpg"
        filepath = save_dir / filename
        
        # Save image
        cv2.imwrite(str(filepath), vehicle_crop)
        
        logger.debug(f"📸 Snapshot saved: {filename}")
        
        return str(filepath)
    
    def add_detection_to_session(self, frame: np.ndarray, detection: dict):
        """
        Add detection to session data and save snapshot
        Only saves ONE detection per unique vehicle ID
        """
        # Check if session is active
        if not hasattr(self, 'session_id') or self.session_id is None:
            return
        
        vehicle_id = detection["id"]
        
        # ✅ FILTRO: Solo guardar si es la primera vez que vemos este ID
        if vehicle_id in self.session_vehicle_ids:
            logger.debug(f"⏭️ Vehicle ID#{vehicle_id} already saved, skipping...")
            return
        
        # Marcar este ID como guardado
        self.session_vehicle_ids.add(vehicle_id)
        
        logger.info(f"✅ NEW vehicle ID#{vehicle_id} detected - saving to session")
        
        # Save vehicle snapshot
        image_path = self._save_vehicle_snapshot(frame, detection)
        
        # Create detection entry (compatible with analysis format)
        detection_entry = {
            "vehicle_id": vehicle_id,
            "vehicle_type": detection["class"],
            "plate_number": "UNREADABLE",  # Default until OCR integration
            "confidence": detection["confidence"],
            "detection_method": "rejected",  # Default until OCR integration
            "image_path": image_path,
            "timestamp": datetime.now().isoformat()
        }
        
        self.session_detections.append(detection_entry)
        logger.info(f"📊 Unique vehicles saved in session: {len(self.session_detections)}")
    
    def save_session_data(self) -> str:
        """
        Save session detection data to JSON file
        Compatible with video analysis format
        Returns path to saved JSON file
        """
        if not hasattr(self, 'session_id') or self.session_id is None:
            logger.warning("No active session - data not saved")
            return ""
        
        # Generate JSON filename: detections_[CameraName]_stream_[timestamp].json
        json_filename = f"detections_{self.camera_name}_stream_{self.session_id}.json"
        json_filepath = settings.STREAMING_DATA_DIR / json_filename
        
        # Prepare JSON structure (compatible with analysis format)
        session_data = {
            "video_name": self.camera_name,
            "analysis_id": f"stream_{self.session_id}",
            "detections": self.session_detections
        }
        
        # Save JSON file
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Session data saved: {json_filename}")
        logger.info(f"   Total detections: {len(self.session_detections)}")
        logger.info(f"   File: {json_filepath}")
        
        return str(json_filepath)
    
    def end_session(self) -> str:
        """
        End streaming session and save all data
        Returns path to saved JSON file
        """
        if not hasattr(self, 'session_id') or self.session_id is None:
            logger.warning("No active session to end")
            return ""
        
        logger.info(f"📊 Ending streaming session: {self.session_id}")
        json_path = self.save_session_data()
        
        # Reset session variables
        self.session_id = None
        self.camera_name = None
        self.session_detections = []
        self.session_vehicle_ids = set()
        self.session_start_time = None
        
        return json_path
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            "frames_processed": self.frame_count,
            "total_detections": self.detection_count,
            "unique_vehicles": len(self.unique_vehicles),
            "avg_detections_per_frame": self.detection_count / max(self.frame_count, 1)
        }
    
    def reset_stats(self):
        """Reset all statistics and tracking data"""
        self.frame_count = 0
        self.detection_count = 0
        self.unique_vehicles.clear()
        self.lost_tracks_history.clear()
        self.tracked_bboxes.clear()
        
        # Reset session data
        self.session_id = None
        self.camera_name = None
        self.session_detections = []
        self.session_vehicle_ids = set()
        self.session_start_time = None
        
        logger.info("Statistics, ID recovery history, and session data reset")
