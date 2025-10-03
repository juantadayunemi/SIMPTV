/**
 * DTOs Comunes para API
 * Objetos de transferencia de datos compartidos entre todos los módulos
 */

import { NotificationTypeKey } from "../types/trafficTypes";

// ============================================
// API RESPONSE WRAPPER DTOs
// ============================================

// Respuesta estándar de la API
export interface ApiResponseDTO<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: ApiErrorDTO;
  timestamp: Date;
  requestId?: string; // Para debugging
}

// Respuesta paginada estándar
export interface PaginatedResponseDTO<T = any> {
  success: boolean;
  data: T[];
  pagination: PaginationInfoDTO;
  filters?: Record<string, any>;
  message?: string;
  error?: ApiErrorDTO;
  timestamp: Date;
  requestId?: string;
}

// Información de paginación
export interface PaginationInfoDTO {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
  startIndex: number;
  endIndex: number;
}

// ============================================
// ERROR DTOs
// ============================================

// Error estándar de la API
export interface ApiErrorDTO {
  code: string;
  message: string;
  details?: string;
  field?: string;
  statusCode: number;
  timestamp: Date;
  path?: string;
}

// Error de validación específico
export interface ValidationErrorDTO extends ApiErrorDTO {
  field: string;
  value: any;
  constraints: string[];
  children?: ValidationErrorDTO[];
}

// Error de negocio/lógica
export interface BusinessErrorDTO extends ApiErrorDTO {
  businessRule: string;
  context?: Record<string, any>;
}

// ============================================
// QUERY DTOs BASE
// ============================================

// Query base para paginación y ordenamiento
export interface BaseQueryDTO {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  search?: string;
}

// Query con filtros de fecha
export interface DateRangeQueryDTO extends BaseQueryDTO {
  startDate?: Date;
  endDate?: Date;
  timezone?: string;
}

// ============================================
// WEBSOCKET DTOs
// ============================================

// Mensaje genérico de WebSocket
export interface WebSocketMessageDTO<T = any> {
  type: string;
  payload: T;
  timestamp: Date;
  userId?: string;
  sessionId?: string;
}

// Mensaje de notificación en tiempo real
export interface RealtimeNotificationDTO {
  id: string;
  type: NotificationTypeKey;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  actionUrl?: string;
  metadata?: Record<string, any>;
  userId?: string;
  createdAt: Date;
}

// Mensaje de actualización de análisis en tiempo real
export interface RealtimeAnalysisUpdateDTO {
  analysisId: number;
  status: string;
  progress?: number;
  vehicleCount: number;
  newDetections?: {
    vehicleId: string;
    vehicleType: string;
    confidence: number;
    timestamp: Date;
  }[];
  plateDetections?: {
    plateNumber: string;
    confidence: number;
    vehicleId: string;
    hasAlerts: boolean;
    timestamp: Date;
  }[];
}

// ============================================
// AUTHENTICATION DTOs
// ============================================

// DTO para login
export interface LoginRequestDTO {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// DTO para respuesta de login
export interface LoginResponseDTO {
  accessToken: string;
  refreshToken: string;
  user: UserInfoDTO;
  expiresAt: Date;
  tokenType: 'Bearer';
}

// DTO para información de usuario
export interface UserInfoDTO {
  id: string;
  email: string;
  fullName?: string;
  role: string;
  permissions: string[];
  isActive: boolean;
  lastLogin?: Date;
  profileImage?: string;
  preferences?: UserPreferencesDTO;
  createdAt: Date;
}

// DTO para preferencias de usuario
export interface UserPreferencesDTO {
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  dashboard: {
    autoRefresh: boolean;
    refreshInterval: number; // en segundos
    defaultView: string;
  };
}

// DTO para actualizar perfil
export interface UpdateProfileRequestDTO {
  fullName?: string;
  currentPassword?: string; // Requerido para cambio de contraseña
  newPassword?: string;
  confirmPassword?: string;
  preferences?: Partial<UserPreferencesDTO>;
}

// ============================================
// NOTIFICATION DTOs
// ============================================

// DTO para notificación individual
export interface NotificationDTO {
  id: string;
  type: NotificationTypeKey;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  isRead: boolean;
  readAt?: Date;
  createdAt: Date;
  actionUrl?: string;
  metadata?: Record<string, any>;
  userId: string;
}

// DTO para resumen de notificaciones
export interface NotificationSummaryDTO {
  total: number;
  unread: number;
  byType: {
    type: NotificationTypeKey;
    count: number;
    unreadCount: number;
  }[];
  byPriority: {
    priority: 'low' | 'medium' | 'high' | 'urgent';
    count: number;
    unreadCount: number;
  }[];
  recent: NotificationDTO[];
}

// DTO para marcar notificaciones como leídas
export interface MarkNotificationsReadDTO {
  notificationIds?: string[]; // Si no se especifica, marca todas como leídas
  markAllAsRead?: boolean;
}

// ============================================
// DASHBOARD DTOs
// ============================================

// DTO para estadísticas del dashboard
export interface DashboardStatsDTO {
  overview: {
    totalAnalyses: number;
    activeAnalyses: number;
    totalVehiclesDetected: number;
    totalPlatesDetected: number;
    activeAlerts: number;
  };
  
  traffic: {
    avgDailyTraffic: number;
    topBusyLocations: {
      location: string;
      vehicleCount: number;
    }[];
    hourlyTrend: {
      hour: number;
      vehicleCount: number;
    }[];
  };
  
  plates: {
    dailyDetections: number;
    uniquePlatesCount: number;
    avgConfidence: number;
    alertsByType: {
      type: string;
      count: number;
    }[];
  };
  
  system: {
    uptime: number;
    activeCameras: number;
    totalCameras: number;
    activeUsers: number;
  };
  
  notifications: NotificationSummaryDTO;
  
  lastUpdated: Date;
}

// ============================================
// FILE UPLOAD DTOs
// ============================================

// DTO para subida de archivo
export interface FileUploadRequestDTO {
  file: File | Buffer;
  filename: string;
  mimetype: string;
  size: number;
  metadata?: Record<string, any>;
}

// DTO para respuesta de subida
export interface FileUploadResponseDTO {
  id: string;
  filename: string;
  originalName: string;
  mimetype: string;
  size: number;
  url: string;
  publicUrl?: string;
  metadata?: Record<string, any>;
  uploadedAt: Date;
}

// ============================================
// HEALTH CHECK DTOs
// ============================================

// DTO para health check
export interface HealthCheckDTO {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: Date;
  uptime: number;
  version: string;
  environment: string;
  
  checks: {
    database: {
      status: 'up' | 'down';
      responseTime?: number;
      error?: string;
    };
    redis?: {
      status: 'up' | 'down';
      responseTime?: number;
      error?: string;
    };
    storage: {
      status: 'up' | 'down';
      responseTime?: number;
      error?: string;
    };
    externalApis?: {
      name: string;
      status: 'up' | 'down';
      responseTime?: number;
      error?: string;
    }[];
  };
  
  metrics: {
    memoryUsage: {
      used: number;
      total: number;
      percentage: number;
    };
    cpuUsage: number;
    activeConnections: number;
  };
}