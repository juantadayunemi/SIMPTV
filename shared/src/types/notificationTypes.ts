/**
 * Tipos y Enums para el sistema de notificaciones
 */

// ============= NOTIFICATION TYPES =============
export const NOTIFICATION_TYPES = {
  TRAFFIC_ALERT: 'TRAFFIC_ALERT' as const,
  TRAFFIC_VIOLATION: 'TRAFFIC_VIOLATION' as const,
  STOLEN_VEHICLE: 'STOLEN_VEHICLE' as const,
  VEHICLE_COMPLAINT: 'VEHICLE_COMPLAINT' as const,
  PLATE_DETECTION: 'PLATE_DETECTION' as const,
  SYSTEM_ALERT: 'SYSTEM_ALERT' as const,
  USER_ACTION: 'USER_ACTION' as const,
  ANALYSIS_COMPLETE: 'ANALYSIS_COMPLETE' as const,
  ERROR_NOTIFICATION: 'ERROR_NOTIFICATION' as const
} as const;


export type NotificationTypeKey = typeof NOTIFICATION_TYPES[keyof typeof NOTIFICATION_TYPES];



