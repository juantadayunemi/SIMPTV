/**
 * Entidades de Detección de Placas
 * Modelos para reconocimiento y análisis de placas vehiculares
 */

import { 
  AlertTypeKey, 
  DensityLevelKey, 
  TrafficDirectionKey, 
  VehicleTypeKey 
} from "../types/trafficTypes";

// ============================================
// ENTIDAD: LICENSE PLATE (Placas Detectadas)
// ============================================

export interface LicensePlateEntity {
  id: number; // ID autoincremental
  vehicleId: string; // FK a Vehicle (CUID) - aquí está TODA la info de tracking
  
  // Información de la placa
  plateNumber: string; // Número de placa detectado (Ej: "ABC-1234")
  country: string; // País de la placa (Ej: "EC" para Ecuador)
  confidence: number; // Confianza del OCR (0-1)
  
  // Frame de detección (referencia al mejor frame para OCR)
  bestFrameId: number; // FK a VehicleFrame con mejor calidad para placa
  
  // Validación externa
  isValidated: boolean; // Si se validó contra API externa
  validatedAt?: Date; // Fecha de validación
  validationSource?: string; // Fuente de validación (Ej: "ANT", "Police API")
  validationData?: string; // JSON con respuesta completa de la API externa
  
  // Información del vehículo (de APIs externas)
  vehicleBrand?: string; // Marca del vehículo según registro oficial
  vehicleModel?: string; // Modelo del vehículo según registro oficial
  vehicleYear?: number; // Año del vehículo según registro oficial
  vehicleColor?: string; // Color del vehículo según registro oficial
  ownerName?: string; // Nombre del propietario (si está disponible públicamente)
  registrationStatus?: string; // Estado del registro (vigente, vencido, etc)
  
  // Alertas y procesamiento
  hasAlerts: boolean; // Si tiene alertas asociadas
  processedAt: Date; // Timestamp cuando se procesó el OCR
  
  // Notas
  notes?: string; // Notas adicionales sobre la detección
  
  createdAt: Date; // Fecha de creación del registro
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// ENTIDAD: PLATE ALERT (Alertas de Placas)
// ============================================

export interface PlateAlertEntity {
  id: number; // ID autoincremental
  licensePlateId: number; // FK a LicensePlate (de aquí se obtiene vehicleId)
  
  // Información de la alerta
  alertType: AlertTypeKey; // Tipo de alerta
  severity: number; // Severidad de la alerta (1-10)
  title: string; // Título corto de la alerta (Ej: "Vehículo Robado")
  description: string; // Descripción detallada de la alerta
  
  // Metadatos de la alerta
  source: string; // Fuente de la alerta (Ej: "Police Database", "ANT", "Interpol")
  externalReferenceId?: string; // ID de referencia en sistema externo
  reportDate?: Date; // Fecha del reporte original de la denuncia
  reportedBy?: string; // Quién reportó (si está disponible)
  isActive: boolean; // Si la alerta sigue activa
  resolvedAt?: Date; // Fecha en que se resolvió la alerta
  resolutionNotes?: string; // Notas sobre la resolución
  
  // Notificación y seguimiento
  wasNotified: boolean; // Si se notificó a usuarios/autoridades
  notifiedAt?: Date; // Fecha de notificación
  notifiedTo?: string; // A quién se notificó (Ej: "user@example.com, 911")
  notificationMethod?: string; // Método de notificación (email, SMS, webhook)
  requiresAction: boolean; // Si requiere acción inmediata
  actionTaken?: string; // Descripción de la acción tomada
  actionTakenBy?: string; // Quién tomó la acción
  actionTakenAt?: Date; // Cuándo se tomó la acción
  
  createdAt: Date; // Fecha de creación del registro
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// TIPOS AUXILIARES PARA FRONTEND
// ============================================

/**
 * NOTA IMPORTANTE SOBRE RELACIONES:
 * 
 * Para obtener información completa de una detección de placa con alerta:
 * 
 * PlateAlert -> LicensePlate -> Vehicle -> TrafficAnalysis -> Camera/Location
 *                                  |
 *                                  └-> VehicleFrame (múltiples)
 * 
 * Desde PlateAlert puedes acceder a:
 * - licensePlateId -> LicensePlate.vehicleId -> Vehicle (TODA la info de tracking)
 * - Vehicle.trafficAnalysisId -> TrafficAnalysis (info de sesión, cámara, ubicación)
 * - Vehicle.id -> VehicleFrame[] (todos los frames guardados)
 * - LicensePlate.bestFrameId -> VehicleFrame (mejor frame para placa)
 * 
 * NO duplicamos datos porque:
 * - direction, speed, lane -> ya están en Vehicle
 * - detectedAt, location, camera -> ya están en TrafficAnalysis/Vehicle
 * - frames, evidencia -> ya están en VehicleFrame
 * - GPS coordinates -> ya están en Location (via TrafficAnalysis)
 */

// DTO para resultado de detección de placa
export interface DetectPlateResultDTO {
  vehicleId: string;
  frameId: number;
  plateNumber: string;
  country: string;
  confidence: number;
  detectedAt: Date;
}

// DTO para reporte de alerta de placa (con información relacionada)
export interface PlateAlertReportDTO {
  // Información de la alerta
  alertId: number;
  alertType: AlertTypeKey;
  severity: number;
  title: string;
  description: string;
  source: string;
  externalReferenceId?: string;
  
  // Información de la placa
  plateNumber: string;
  plateCountry: string;
  plateConfidence: number;
  
  // Información del vehículo (desde VehicleEntity via vehicleId)
  vehicleId: string; // CUID del tracking
  vehicleType: VehicleTypeKey;
  vehicleColor?: string;
  vehicleBrand?: string; // Detectado por IA
  vehicleModel?: string; // Detectado por IA
  vehicleDirection?: TrafficDirectionKey;
  vehicleSpeed?: number;
  vehicleLane?: number;
  
  // Información de detección (desde VehicleEntity)
  firstDetectedAt: Date;
  lastDetectedAt: Date;
  totalFrames: number;
  
  // Información de ubicación (desde TrafficAnalysisEntity -> LocationEntity)
  locationDescription: string; // Ej: "Ave. 5 de Octubre y Córdova"
  locationLatitude: number;
  locationLongitude: number;
  locationCity?: string;
  
  // Información de la cámara (desde TrafficAnalysisEntity -> CameraEntity)
  cameraId: number;
  cameraName: string;
  
  // Información del análisis (desde TrafficAnalysisEntity)
  trafficAnalysisId: number;
  analysisStartedAt: Date;
  
  // Frames de evidencia (desde VehicleFrameEntity)
  bestFrameForPlate: {
    frameId: number;
    frameNumber: number;
    timestamp: Date;
    imagePath?: string;
    confidence: number;
    frameQuality: number;
  };
  
  // Información de validación oficial (desde LicensePlateEntity)
  officialVehicleBrand?: string; // De registro oficial
  officialVehicleModel?: string;
  officialVehicleYear?: number;
  officialVehicleColor?: string;
  ownerName?: string;
  registrationStatus?: string;
  
  // Estado de la alerta
  isActive: boolean;
  requiresAction: boolean;
  wasNotified: boolean;
  notifiedAt?: Date;
  notifiedTo?: string;
  actionTaken?: string;
  resolvedAt?: Date;
  
  createdAt: Date;
}

// DTO para búsqueda de placas detectadas
export interface SearchPlatesDTO {
  plateNumber?: string; // Búsqueda por número de placa
  cameraId?: number; // Filtrar por cámara
  locationId?: number; // Filtrar por ubicación
  startDate?: Date; // Rango de fechas inicio
  endDate?: Date; // Rango de fechas fin
  hasAlerts?: boolean; // Solo placas con alertas
  alertType?: AlertTypeKey; // Filtrar por tipo de alerta
  country?: string; // Filtrar por país
}

