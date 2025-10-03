// ============================================
// ENUMS Y TIPOS
// ============================================

export const VEHICLE_TYPES = {
  CAR: 'CAR',
  TRUCK: 'TRUCK',
  MOTORCYCLE: 'MOTORCYCLE',
  BUS: 'BUS',
  BICYCLE: 'BICYCLE',
  OTHER: 'OTHER'
} as const;

export type VehicleTypeKey = keyof typeof VEHICLE_TYPES;

export const DENSITY_LEVELS = {
  LOW: 'LOW',       // Flujo libre
  MEDIUM: 'MEDIUM', // Tráfico moderado
  HIGH: 'HIGH',     // Tráfico denso
  HEAVY: 'HEAVY'    // Congestionamiento
} as const;

export type DensityLevelKey = keyof typeof DENSITY_LEVELS;

export const ANALYSIS_STATUS = {
  PENDING: 'PENDING',       // En cola
  PROCESSING: 'PROCESSING', // Procesando
  COMPLETED: 'COMPLETED',   // Completado
  FAILED: 'FAILED',         // Falló
  CANCELLED: 'CANCELLED'    // Cancelado
} as const;

export type AnalysisStatusKey = keyof typeof ANALYSIS_STATUS;

export const TRACKING_STATUS = {
  ACTIVE: 'ACTIVE',   // Vehículo actualmente en campo de visión
  EXITED: 'EXITED',   // Salió del campo de visión normalmente
  LOST: 'LOST'        // Se perdió el tracking (oclusión, error)
} as const;

export type TrackingStatusKey = keyof typeof TRACKING_STATUS;

export const TRAFFIC_DIRECTION = {
  NORTH: 'NORTH',
  SOUTH: 'SOUTH',
  EAST: 'EAST',
  WEST: 'WEST',
  NORTHEAST: 'NORTHEAST',
  NORTHWEST: 'NORTHWEST',
  SOUTHEAST: 'SOUTHEAST',
  SOUTHWEST: 'SOUTHWEST'
} as const;

export type TrafficDirectionKey = keyof typeof TRAFFIC_DIRECTION;

export const PLATE_PROCESSING_STATUS = {
  PENDING: 'PENDING',       // En cola para procesamiento
  PROCESSING: 'PROCESSING', // Procesando OCR
  DETECTED: 'DETECTED',     // Placa detectada exitosamente
  NOT_DETECTED: 'NOT_DETECTED', // No se pudo detectar placa
  FAILED: 'FAILED'          // Error en el procesamiento
} as const;

export type PlateProcessingStatusKey = keyof typeof PLATE_PROCESSING_STATUS;

export const ALERT_TYPE = {
  STOLEN: 'STOLEN',           // Vehículo reportado como robado
  WANTED: 'WANTED',           // Vehículo buscado
  EXPIRED: 'EXPIRED',         // Documentos vencidos
  VIOLATION: 'VIOLATION',     // Multas pendientes
  OTHER: 'OTHER'              // Otros tipos de alerta
} as const;

export type AlertTypeKey = keyof typeof ALERT_TYPE;

// Notification Types
export const NOTIFICATION_TYPES = {
  TRAFFIC_ALERT: 'TRAFFIC_ALERT',
  PLATE_DETECTION: 'PLATE_DETECTION',
  SYSTEM_ALERT: 'SYSTEM_ALERT',
  USER_ACTION: 'USER_ACTION',
  ANALYSIS_COMPLETE: 'ANALYSIS_COMPLETE',
  ERROR_NOTIFICATION: 'ERROR_NOTIFICATION'
} as const;

export type NotificationTypeKey = keyof typeof NOTIFICATION_TYPES;

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