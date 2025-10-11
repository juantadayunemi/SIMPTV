// ============================================
// ENUMS Y TIPOS
// ============================================

export const VEHICLE_TYPES = {
  CAR: 'CAR' as const,
  TRUCK: 'TRUCK' as const,
  MOTORCYCLE: 'MOTORCYCLE' as const,
  BUS: 'BUS' as const,
  BICYCLE: 'BICYCLE' as const,
  OTHER: 'OTHER' as const
} as const;

export type VehicleTypeKey = typeof VEHICLE_TYPES[keyof typeof VEHICLE_TYPES];

export const DENSITY_LEVELS = {
  LOW: 'LOW' as const,       // Flujo libre
  MEDIUM: 'MEDIUM' as const, // Tráfico moderado
  HIGH: 'HIGH' as const,     // Tráfico denso
  HEAVY: 'HEAVY' as const    // Congestionamiento
} as const;

export type DensityLevelKey = typeof DENSITY_LEVELS[keyof typeof DENSITY_LEVELS];

export const StatusCameraKey = {
  ACTIVE: 'ACTIVE' as const,       // active
  INACTIVE: 'INACTIVE' as const, // inactive
  MAINTENANCE: 'MAINTENANCE' as const,    // maintenance
} as const;

export type StatusCameraKey = typeof StatusCameraKey[keyof typeof StatusCameraKey];

export const ANALYSIS_STATUS = {
  PENDING: 'PENDING' as const,       // En cola
  PROCESSING: 'PROCESSING' as const, // Procesando
  COMPLETED: 'COMPLETED' as const,   // Completado
  FAILED: 'FAILED' as const,         // Falló
  CANCELLED: 'CANCELLED' as const    // Cancelado
} as const;

export type AnalysisStatusKey = typeof ANALYSIS_STATUS[keyof typeof ANALYSIS_STATUS];

export const TRACKING_STATUS = {
  ACTIVE: 'ACTIVE' as const,   // Vehículo actualmente en campo de visión
  EXITED: 'EXITED' as const,   // Salió del campo de visión normalmente
  LOST: 'LOST' as const        // Se perdió el tracking (oclusión, error)
} as const;

export type TrackingStatusKey = typeof TRACKING_STATUS[keyof typeof TRACKING_STATUS];

export const TRAFFIC_DIRECTION = {
  NORTH: 'NORTH' as const,
  SOUTH: 'SOUTH' as const,
  EAST: 'EAST' as const,
  WEST: 'WEST' as const,
  NORTHEAST: 'NORTHEAST' as const,
  NORTHWEST: 'NORTHWEST' as const,
  SOUTHEAST: 'SOUTHEAST' as const,
  SOUTHWEST: 'SOUTHWEST' as const
} as const;

export type TrafficDirectionKey = typeof TRAFFIC_DIRECTION[keyof typeof TRAFFIC_DIRECTION];

export const PLATE_PROCESSING_STATUS = {
  PENDING: 'PENDING' as const,       // En cola para procesamiento
  PROCESSING: 'PROCESSING' as const, // Procesando OCR
  DETECTED: 'DETECTED' as const,     // Placa detectada exitosamente
  NOT_DETECTED: 'NOT_DETECTED' as const, // No se pudo detectar placa
  FAILED: 'FAILED' as const          // Error en el procesamiento
} as const;

export type PlateProcessingStatusKey = typeof PLATE_PROCESSING_STATUS[keyof typeof PLATE_PROCESSING_STATUS];

export const ALERT_TYPE = {
  STOLEN: 'STOLEN' as const,           // Vehículo reportado como robado
  WANTED: 'WANTED' as const,           // Vehículo buscado
  EXPIRED: 'EXPIRED' as const,         // Documentos vencidos
  VIOLATION: 'VIOLATION' as const,     // Multas pendientes
  OTHER: 'OTHER' as const              // Otros tipos de alerta
} as const;

export type AlertTypeKey = typeof ALERT_TYPE[keyof typeof ALERT_TYPE];

// Notification Types
export const NOTIFICATION_TYPES = {
  TRAFFIC_ALERT: 'TRAFFIC_ALERT' as const,
  PLATE_DETECTION: 'PLATE_DETECTION' as const,
  SYSTEM_ALERT: 'SYSTEM_ALERT' as const,
  USER_ACTION: 'USER_ACTION' as const,
  ANALYSIS_COMPLETE: 'ANALYSIS_COMPLETE' as const,
  ERROR_NOTIFICATION: 'ERROR_NOTIFICATION' as const
} as const;

export type NotificationTypeKey = typeof NOTIFICATION_TYPES[keyof typeof NOTIFICATION_TYPES];

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