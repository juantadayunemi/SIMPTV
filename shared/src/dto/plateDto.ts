/**
 * DTOs para Detección de Placas
 * Objetos de transferencia de datos específicos para placas vehiculares
 */

import { 
  AlertTypeKey, 
  TrafficDirectionKey, 
  VehicleTypeKey 
} from "../types/trafficTypes";

// ============================================
// RESPONSE DTOs (Para Frontend)
// ============================================

// DTO optimizado para mostrar detecciones de placas en listas
export interface PlateDetectionResponseDTO {
  id: number;
  plateNumber: string;
  country: string;
  confidence: number;
  
  // Información del vehículo relacionado
  vehicle: {
    id: string; // CUID
    type: VehicleTypeKey;
    confidence: number;
    direction?: TrafficDirectionKey;
    speed?: number;
    lane?: number;
    color?: string;
    brand?: string; // Detectado por IA
    model?: string; // Detectado por IA
  };
  
  // Frame de mejor detección
  bestFrame: {
    id: number;
    frameNumber: number;
    timestamp: Date;
    frameQuality: number;
    imagePath?: string;
    boundingBox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };
  
  // Información de ubicación y sesión
  location: {
    id: number;
    description: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
  };
  
  camera: {
    id: number;
    name: string;
  };
  
  analysis: {
    id: number;
    startedAt: Date;
  };
  
  // Validación oficial
  validation: {
    isValidated: boolean;
    validatedAt?: Date;
    source?: string;
    officialData?: {
      vehicleBrand?: string;
      vehicleModel?: string;
      vehicleYear?: number;
      vehicleColor?: string;
      ownerName?: string;
      registrationStatus?: string;
    };
  };
  
  // Alertas
  hasAlerts: boolean;
  alertCount?: number;
  highestAlertSeverity?: number;
  
  // Timestamps
  processedAt: Date;
  createdAt: Date;
}

// DTO para mostrar alertas de placas
export interface PlateAlertResponseDTO {
  id: number;
  
  // Información de la alerta
  alertType: AlertTypeKey;
  severity: number; // 1-10
  title: string;
  description: string;
  source: string;
  externalReferenceId?: string;
  
  // Información de la placa detectada
  plate: {
    id: number;
    plateNumber: string;
    country: string;
    confidence: number;
  };
  
  // Información del vehículo y ubicación
  detection: {
    vehicleId: string;
    vehicleType: VehicleTypeKey;
    location: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
    cameraName: string;
    detectedAt: Date;
    direction?: TrafficDirectionKey;
    speed?: number;
    lane?: number;
  };
  
  // Evidencia
  evidence: {
    bestFrameImage?: string;
    frameQuality: number;
    totalFrames: number;
  };
  
  // Estado de la alerta
  status: {
    isActive: boolean;
    requiresAction: boolean;
    resolvedAt?: Date;
    resolutionNotes?: string;
  };
  
  // Notificaciones y acciones
  notifications: {
    wasNotified: boolean;
    notifiedAt?: Date;
    notifiedTo?: string[];
    method?: string;
  };
  
  actions: {
    actionTaken?: string;
    actionTakenBy?: string;
    actionTakenAt?: Date;
  };
  
  // Metadatos de la denuncia original
  report: {
    reportDate?: Date;
    reportedBy?: string;
  };
  
  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

// DTO para reporte completo de alerta (para autoridades)
export interface PlateAlertFullReportDTO {
  // Información básica de la alerta
  alert: PlateAlertResponseDTO;
  
  // Información completa del vehículo detectado
  vehicleTracking: {
    vehicleId: string;
    firstDetectedAt: Date;
    lastDetectedAt: Date;
    totalFrames: number;
    avgSpeed?: number;
    trackingPath?: {
      frameNumber: number;
      timestamp: Date;
      position: {
        x: number;
        y: number;
      };
      speed?: number;
    }[];
  };
  
  // Información oficial del vehículo (si está disponible)
  officialVehicleData?: {
    brand: string;
    model: string;
    year: number;
    color: string;
    ownerName?: string;
    registrationStatus: string;
    validationSource: string;
    validatedAt: Date;
  };
  
  // Contexto del análisis
  analysisContext: {
    analysisId: number;
    sessionDuration: number;
    totalVehiclesInSession: number;
    trafficDensity: string;
    weatherConditions?: string;
  };
  
  // Todas las imágenes disponibles
  evidenceImages: {
    frameId: number;
    frameNumber: number;
    timestamp: Date;
    imagePath: string;
    frameQuality: number;
    confidence: number;
  }[];
  
  // Historial de acciones
  actionHistory: {
    action: string;
    performedBy: string;
    performedAt: Date;
    notes?: string;
  }[];
}

// DTO para estadísticas de placas
export interface PlateStatsResponseDTO {
  // Estadísticas generales
  totalDetections: number;
  uniquePlates: number;
  avgConfidence: number;
  
  // Estadísticas de alertas
  totalAlerts: number;
  activeAlerts: number;
  alertsBySeverity: {
    severity: number;
    count: number;
  }[];
  
  alertsByType: {
    type: AlertTypeKey;
    count: number;
    percentage: number;
  }[];
  
  // Tendencias temporales
  dailyTrend: {
    date: Date;
    detections: number;
    alerts: number;
  }[];
  
  hourlyTrend: {
    hour: number;
    detections: number;
    alerts: number;
  }[];
  
  // Top ubicaciones
  topLocations: {
    locationId: number;
    description: string;
    detectionCount: number;
    alertCount: number;
    lastActivity: Date;
  }[];
  
  // Placas más frecuentes
  frequentPlates: {
    plateNumber: string;
    detectionCount: number;
    locations: string[];
    hasAlerts: boolean;
    lastSeen: Date;
  }[];
}

// ============================================
// REQUEST DTOs (Para Backend)
// ============================================

// DTO para procesar detección de placa
export interface ProcessPlateDetectionRequestDTO {
  vehicleId: string; // CUID del vehículo
  bestFrameId: number; // FK al mejor frame para OCR
  
  // Resultado del OCR
  plateNumber: string;
  country: string;
  confidence: number;
  
  // Configuración de validación
  validateAgainstOfficialDB?: boolean;
  checkForAlerts?: boolean;
  
  // Notas adicionales
  notes?: string;
}

// DTO para crear alerta de placa
export interface CreatePlateAlertRequestDTO {
  licensePlateId: number;
  
  // Información de la alerta
  alertType: AlertTypeKey;
  severity: number; // 1-10
  title: string;
  description: string;
  source: string;
  externalReferenceId?: string;
  
  // Metadatos de la denuncia
  reportDate?: Date;
  reportedBy?: string;
  
  // Configuración de notificación
  requiresAction: boolean;
  notifyTo?: string[]; // emails, teléfonos, etc.
  notificationMethod?: string;
}

// DTO para actualizar alerta
export interface UpdatePlateAlertRequestDTO {
  // Estado
  isActive?: boolean;
  
  // Resolución
  resolvedAt?: Date;
  resolutionNotes?: string;
  
  // Acciones tomadas
  actionTaken?: string;
  actionTakenBy?: string;
  actionTakenAt?: Date;
  
  // Notificaciones
  wasNotified?: boolean;
  notifiedAt?: Date;
  notifiedTo?: string[];
  notificationMethod?: string;
}

// DTO para validación oficial
export interface ValidatePlateRequestDTO {
  licensePlateId: number;
  validationSource: string; // "ANT", "Police API", etc.
  
  // Datos obtenidos de la validación
  vehicleBrand?: string;
  vehicleModel?: string;
  vehicleYear?: number;
  vehicleColor?: string;
  ownerName?: string;
  registrationStatus?: string;
  
  // Respuesta completa de la API (como JSON)
  validationData?: string;
}

// ============================================
// QUERY DTOs (Para filtros y búsquedas)
// ============================================

// DTO para buscar detecciones de placas
export interface PlateSearchQueryDTO {
  // Búsqueda por placa
  plateNumber?: string; // Búsqueda exacta o parcial
  country?: string[];
  
  // Filtros de ubicación y tiempo
  locationIds?: number[];
  cameraIds?: number[];
  startDate?: Date;
  endDate?: Date;
  
  // Filtros de vehículo
  vehicleTypes?: VehicleTypeKey[];
  directions?: TrafficDirectionKey[];
  minSpeed?: number;
  maxSpeed?: number;
  
  // Filtros de calidad
  minConfidence?: number;
  minFrameQuality?: number;
  
  // Filtros de validación y alertas
  isValidated?: boolean;
  validationSources?: string[];
  hasAlerts?: boolean;
  alertTypes?: AlertTypeKey[];
  minAlertSeverity?: number;
  
  // Filtros de estado
  onlyActiveAlerts?: boolean;
  requiresAction?: boolean;
  
  // Paginación y ordenamiento
  page?: number;
  limit?: number;
  sortBy?: 'processedAt' | 'confidence' | 'plateNumber' | 'alertSeverity';
  sortOrder?: 'asc' | 'desc';
}

// DTO para buscar alertas específicamente
export interface PlateAlertQueryDTO {
  // Filtros básicos
  alertTypes?: AlertTypeKey[];
  minSeverity?: number;
  maxSeverity?: number;
  
  // Filtros de estado
  isActive?: boolean;
  requiresAction?: boolean;
  wasNotified?: boolean;
  
  // Filtros de fuente
  sources?: string[];
  
  // Filtros de tiempo
  alertsAfter?: Date;
  alertsBefore?: Date;
  reportedAfter?: Date;
  reportedBefore?: Date;
  
  // Filtros de ubicación
  locationIds?: number[];
  cameraIds?: number[];
  
  // Filtros de placa
  plateNumbers?: string[];
  countries?: string[];
  
  // Paginación
  page?: number;
  limit?: number;
  sortBy?: 'createdAt' | 'severity' | 'reportDate';
  sortOrder?: 'asc' | 'desc';
}

// DTO para estadísticas agregadas
export interface PlateStatsQueryDTO {
  // Rango de tiempo
  startDate: Date;
  endDate: Date;
  
  // Filtros de ubicación
  locationIds?: number[];
  cameraIds?: number[];
  
  // Agrupación temporal
  groupBy?: 'hour' | 'day' | 'week' | 'month';
  
  // Métricas específicas
  includeAlertBreakdown?: boolean;
  includeLocationStats?: boolean;
  includeFrequentPlates?: boolean;
  maxFrequentPlates?: number;
}