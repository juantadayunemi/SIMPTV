// Vehicle Types
export const VEHICLE_TYPES = {
  CAR: 'CAR',
  TRUCK: 'TRUCK',
  MOTORCYCLE: 'MOTORCYCLE',
  BUS: 'BUS',
  BICYCLE: 'BICYCLE',
  OTHER: 'OTHER'
} as const;

// Analysis Status
export const ANALYSIS_STATUS = {
  PENDING: 'PENDING',
  PROCESSING: 'PROCESSING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED'
} as const;

// Traffic Density Levels
export const DENSITY_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH'
} as const;

// Notification Types
export const NOTIFICATION_TYPES = {
  TRAFFIC_ALERT: 'TRAFFIC_ALERT',
  PLATE_DETECTION: 'PLATE_DETECTION',
  SYSTEM_ALERT: 'SYSTEM_ALERT',
  USER_ACTION: 'USER_ACTION',
  ANALYSIS_COMPLETE: 'ANALYSIS_COMPLETE',
  ERROR_NOTIFICATION: 'ERROR_NOTIFICATION'
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
  PROFILE: '/auth/profile',
  
  // Traffic
  TRAFFIC_ANALYSIS: '/traffic/analysis',
  TRAFFIC_PREDICTIONS: '/traffic/predictions',
  TRAFFIC_STATISTICS: '/traffic/statistics',
  
  // Plates
  PLATE_DETECTIONS: '/plates/detections',
  PLATE_SEARCH: '/plates/search',
  PLATE_STATISTICS: '/plates/statistics',
  
  // Notifications
  NOTIFICATIONS: '/notifications',
  NOTIFICATION_SETTINGS: '/notifications/settings',
  
  // WebSocket
  WEBSOCKET: '/ws'
} as const;

// File Upload Constants
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_VIDEO_TYPES: ['video/mp4', 'video/avi', 'video/mov', 'video/wmv'],
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  VIDEO_EXTENSIONS: ['.mp4', '.avi', '.mov', '.wmv'],
  IMAGE_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.webp']
} as const;

// Pagination Constants
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100
} as const;

// Time Constants
export const TIME = {
  ACCESS_TOKEN_EXPIRE_MINUTES: 30,
  REFRESH_TOKEN_EXPIRE_DAYS: 7,
  SESSION_TIMEOUT_MINUTES: 60
} as const;

// System Limits
export const SYSTEM_LIMITS = {
  MAX_CONCURRENT_USERS: 10,
  MAX_CONCURRENT_ANALYSIS: 5,
  MAX_VIDEO_DURATION_MINUTES: 60
} as const;

export type VehicleTypeKey = keyof typeof VEHICLE_TYPES;
export type AnalysisStatusKey = keyof typeof ANALYSIS_STATUS;
export type DensityLevelKey = keyof typeof DENSITY_LEVELS;
export type NotificationTypeKey = keyof typeof NOTIFICATION_TYPES;