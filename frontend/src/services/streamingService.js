/**
 * Streaming API Service
 * Client for Live Monitoring & Recording endpoints
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/streaming';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// CAMERA ENDPOINTS
// ============================================================================

/**
 * Get all cameras
 */
export const getCameras = async () => {
  const response = await api.get('/cameras/');
  return response.data;
};

/**
 * Get camera details
 * @param {string} cameraId 
 */
export const getCamera = async (cameraId) => {
  const response = await api.get(`/cameras/${cameraId}/`);
  return response.data;
};

/**
 * Create new camera
 * @param {Object} cameraData - Camera configuration
 */
export const createCamera = async (cameraData) => {
  const response = await api.post('/cameras/create/', cameraData);
  return response.data;
};

// ============================================================================
// STREAM CONTROL ENDPOINTS
// ============================================================================

/**
 * Start streaming from camera
 * @param {string} cameraId
 */
export const startStream = async (cameraId) => {
  const response = await api.post('/stream/start/', { camera_id: cameraId });
  return response.data;
};

/**
 * Stop streaming and save recording
 * @param {string} cameraId
 * @param {boolean} uploadToS3 - Whether to upload to S3
 */
export const stopStream = async (cameraId, uploadToS3 = true) => {
  const response = await api.post('/stream/stop/', {
    camera_id: cameraId,
    upload_to_s3: uploadToS3,
  });
  return response.data;
};

/**
 * Get stream status and statistics
 * @param {string} cameraId
 */
export const getStreamStatus = async (cameraId) => {
  const response = await api.get(`/stream/status/${cameraId}/`);
  return response.data;
};

// ============================================================================
// RECORDING ENDPOINTS
// ============================================================================

/**
 * Get all recordings (optionally filtered by camera)
 * @param {string} cameraId - Optional camera filter
 */
export const getRecordings = async (cameraId = null) => {
  const params = cameraId ? { camera_id: cameraId } : {};
  const response = await api.get('/recordings/', { params });
  return response.data;
};

/**
 * Get recording details
 * @param {string} recordingId
 */
export const getRecording = async (recordingId) => {
  const response = await api.get(`/recordings/${recordingId}/`);
  return response.data;
};

// ============================================================================
// SYSTEM ENDPOINTS
// ============================================================================

/**
 * Get all active streams
 */
export const getActiveStreams = async () => {
  const response = await api.get('/system/active-streams/');
  return response.data;
};

// ============================================================================
// NEW: LIVE RECORDING ENDPOINTS
// ============================================================================

/**
 * Process a single frame with YOLO detection
 * @param {Object} data - Frame data
 * @param {string} data.frame - Base64 encoded frame
 * @param {string} data.cameraId - Camera ID
 */
export const processFrame = async (data) => {
  const response = await api.post('/process-frame/', {
    frame: data.frame,
    camera_id: data.cameraId
  });
  return response.data;
};

/**
 * Start a new recording
 * @param {Object} data
 * @param {string} data.cameraId - Camera ID
 */
export const startRecording = async (data) => {
  const response = await api.post('/recordings/start/', {
    camera_id: data.camera_id
  });
  return response.data;
};

/**
 * Finalize a recording and upload to S3
 * @param {string} recordingId - Recording ID
 * @param {Object} data
 * @param {Array} data.frames - Array of frame data with detections
 */
export const finalizeRecording = async (recordingId, data) => {
  const response = await api.post(`/recordings/${recordingId}/finalize/`, {
    frames: data.frames
  });
  return response.data;
};

/**
 * Upload video recording (MediaRecorder Blob) to S3
 * @param {string} recordingId - Recording ID
 * @param {Blob} videoBlob - Video Blob from MediaRecorder
 */
export const uploadRecording = async (recordingId, videoBlob) => {
  const formData = new FormData();
  formData.append('video', videoBlob, 'recording.webm');
  
  const response = await api.post(`/recordings/${recordingId}/upload/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Get list of completed recordings
 */
export const getCompletedRecordings = async () => {
  const response = await api.get('/recordings/');
  return response.data;
};

/**
 * Delete a recording from S3 and JSON
 * @param {string} recordingId - Recording ID
 */
export const deleteRecording = async (recordingId) => {
  const response = await api.delete(`/recordings/${recordingId}/delete/`);
  return response.data;
};

/**
 * Start a new detection session
 * @param {string} cameraId - Camera ID
 * @param {string} recordingId - Recording ID
 */
export const startDetectionSession = async (cameraId, recordingId) => {
  const response = await api.post('/detection-sessions/start/', {
    camera_id: cameraId,
    recording_id: recordingId,
  });
  return response.data;
};

/**
 * Save a detection to the active session
 * @param {string} cameraId - Camera ID
 * @param {string} sessionId - Session ID
 * @param {object} detectionData - Detection data (vehicle_type, plate_number, confidence, etc.)
 */
export const saveDetection = async (cameraId, sessionId, detectionData) => {
  const response = await api.post('/detection-sessions/save-detection/', {
    camera_id: cameraId,
    session_id: sessionId,
    ...detectionData,
  });
  return response.data;
};

/**
 * Finalize detection session with video URL
 * @param {string} cameraId - Camera ID
 * @param {string} sessionId - Session ID
 * @param {string} videoUrl - Video URL from S3
 */
export const finalizeDetectionSession = async (cameraId, sessionId, videoUrl) => {
  const response = await api.post('/detection-sessions/finalize/', {
    camera_id: cameraId,
    session_id: sessionId,
    video_url: videoUrl,
  });
  return response.data;
};

export default {
  getCameras,
  getCamera,
  createCamera,
  startStream,
  stopStream,
  getStreamStatus,
  getRecordings,
  getRecording,
  getActiveStreams,
  // NEW
  processFrame,
  startRecording,
  finalizeRecording,
  uploadRecording,
  deleteRecording,
  getCompletedRecordings,
  // Detection sessions
  startDetectionSession,
  saveDetection,
  finalizeDetectionSession,
};
