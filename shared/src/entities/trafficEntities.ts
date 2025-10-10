/**
 * Entidades de Análisis de Tráfico
 * Modelos para análisis de tráfico vehicular y detección de vehículos
 */

import { 
  AlertTypeKey, 
  AnalysisStatusKey, 
  DensityLevelKey, 
  PlateProcessingStatusKey, 
  TrackingStatusKey, 
  TrafficDirectionKey, 
  VehicleTypeKey 
} from "../types/trafficTypes";

// ============================================
// ENTIDAD: LOCATION (Ubicación de Cámara)
// ============================================

export interface LocationEntity {
  id: number; // ID autoincremental
  description: string; // Ej: "Ave. 5 de Octubre y Córdova"
  latitude: number; // Latitud GPS (Ej: -2.145960)
  longitude: number; // Longitud GPS (Ej: -79.889264)
  city?: string; // Ciudad (Ej: "Milagro")
  province?: string; // Provincia (Ej: "Guayas")
  country: string; // País (Ej: "Ecuador")
  notes?: string; // Notas adicionales sobre la ubicación
  isActive: boolean; // Si la ubicación está activa
  createdAt: Date; // Fecha de creación
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// ENTIDAD: CAMERA (Cámara de Vigilancia)
// ============================================

export interface CameraEntity {
  id: number; // ID autoincremental
  name: string; // Nombre identificador (Ej: "CAM-001-Centro")
  brand?: string; // Marca de la cámara (Ej: "Hikvision")
  model?: string; // Modelo (Ej: "DS-2CD2143G0-I")
  resolution?: string; // Resolución (Ej: "1920x1080")
  fps?: number; // Frames por segundo (Ej: 30)
  locationId: number; // FK a Location
  currentLocationId?: number; // FK a Location actual (si es móvil)
  isActive: boolean; // Si la cámara está activa
  isMobile: boolean; // Si la cámara puede cambiar de ubicación
  lanes: number; // Número de carriles que cubre (Ej: 2, 4)
  coversBothDirections: boolean; // Si cubre ambas direcciones del tráfico
  notes?: string; // Notas adicionales
  createdAt: Date; // Fecha de creación
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// ENTIDAD: TRAFFIC ANALYSIS (Sesión de Análisis)
// ============================================

export interface TrafficAnalysisEntity {
  id: number; // ID autoincremental
  cameraId: number; // FK a Camera
  locationId: number; // FK a Location (ubicación en el momento del análisis)
  videoPath?: string; // Ruta del video (si es desde archivo)
  userId?: number; // FK a User que inició el análisis
  
  // Metadatos de la sesión
  startedAt: Date; // Fecha/hora de inicio del análisis
  endedAt?: Date; // Fecha/hora de finalización del análisis
  duration?: number; // Duración en segundos
  
  // Estadísticas calculadas
  totalVehicleCount: number; // Total de vehículos únicos detectados // @default: 0
  avgSpeed?: number; // Velocidad promedio en km/h
  densityLevel: DensityLevelKey; // Nivel de densidad del tráfico
  
  // Datos adicionales
  weatherConditions?: string; // Condiciones climáticas (Ej: "Soleado", "Lluvioso")
  analysisData?: string; // JSON serializado con datos adicionales del análisis
  status: AnalysisStatusKey; // Estado del análisis
  errorMessage?: string; // Mensaje de error si status = FAILED
  
  // Conteos por tipo de vehículo (calculados)
  carCount: number; // Cantidad de autos // @default: 0
  truckCount: number; // Cantidad de camiones // @default: 0
  motorcycleCount: number; // Cantidad de motocicletas // @default: 0
  busCount: number; // Cantidad de buses // @default: 0
  bicycleCount: number; // Cantidad de bicicletas // @default: 0
  otherCount: number; // Cantidad de otros vehículos // @default: 0
  
  createdAt: Date; // Fecha de creación del registro
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// ENTIDAD: VEHICLE (Vehículo Detectado Único)
// ============================================

export interface VehicleEntity {
  id: string; // CUID generado en frontend para tracking único
  trafficAnalysisId: number; // FK a TrafficAnalysis
  
  // Información del vehículo
  vehicleType: VehicleTypeKey; // Tipo de vehículo detectado
  confidence: number; // Confianza promedio de la detección (0-1)
  
  // Tracking temporal
  firstDetectedAt: Date; // Primera vez que se detectó
  lastDetectedAt: Date; // Última vez que se detectó
  trackingStatus: TrackingStatusKey; // Estado del tracking
  
  // Análisis de movimiento
  avgSpeed?: number; // Velocidad promedio durante su recorrido (km/h)
  direction?: TrafficDirectionKey; // Dirección de movimiento
  lane?: number; // Carril en el que se detectó mayormente (1, 2, 3, etc)
  
  // Frames almacenados
  totalFrames: number; // Total de frames donde fue detectado // @default: 0
  storedFrames: number; // Total de frames guardados en BD (muestreo) // @default: 0
  
  // Metadatos
  color?: string; // Color del vehículo (si se puede detectar)
  brand?: string; // Marca (si se puede detectar)
  model?: string; // Modelo (si se puede detectar)
  
  // Procesamiento de placa
  plateProcessingStatus: PlateProcessingStatusKey; // Estado del procesamiento de placa
  bestFrameForPlate?: number; // Número del mejor frame para OCR de placa
  
  // Timestamps
  createdAt: Date; // Fecha de creación
  updatedAt: Date; // Fecha de última actualización
}

// ============================================
// ENTIDAD: VEHICLE FRAME (Frames del Vehículo)
// ============================================

export interface VehicleFrameEntity {
  id: number; // ID autoincremental
  vehicleId: string; // FK a Vehicle (CUID)
  
  // Información del frame
  frameNumber: number; // Número de frame en el video
  timestamp: Date; // Timestamp exacto del frame
  
  // Bounding Box (coordenadas del rectángulo de detección)
  boundingBoxX: number; // Posición X (esquina superior izquierda)
  boundingBoxY: number; // Posición Y (esquina superior izquierda)
  boundingBoxWidth: number; // Ancho del rectángulo de detección
  boundingBoxHeight: number; // Alto del rectángulo de detección
  
  // Calidad del frame
  confidence: number; // Nivel de confianza de detección en este frame (0-1)
  frameQuality: number; // Calidad del frame para OCR (0-1, calculado por nitidez/iluminación)
  
  // Datos adicionales
  speed?: number; // Velocidad instantánea en este frame (km/h)
  imagePath?: string; // Ruta de la imagen del frame (si se guarda)
  
  createdAt: Date; // Fecha de creación
}

// ============================================
// TIPOS AUXILIARES PARA FRONTEND
// ============================================

// DTO para crear un nuevo análisis de tráfico
export interface CreateTrafficAnalysisDTO {
  cameraId: number;
  locationId: number;
  videoPath?: string;
  userId?: number;
  weatherConditions?: string;
}

// DTO para actualizar estadísticas del análisis
export interface UpdateTrafficAnalysisStatsDTO {
  totalVehicleCount: number;
  avgSpeed?: number;
  densityLevel: DensityLevelKey;
  carCount: number;
  truckCount: number;
  motorcycleCount: number;
  busCount: number;
  bicycleCount: number;
  otherCount: number;
}

// DTO para crear detección de vehículo
export interface CreateVehicleDTO {
  id: string; // CUID generado en frontend
  trafficAnalysisId: number;
  vehicleType: VehicleTypeKey;
  confidence: number;
  firstDetectedAt: Date;
  direction?: TrafficDirectionKey;
  lane?: number;
}

// DTO para crear frame de vehículo
export interface CreateVehicleFrameDTO {
  vehicleId: string;
  frameNumber: number;
  timestamp: Date;
  boundingBoxX: number;
  boundingBoxY: number;
  boundingBoxWidth: number;
  boundingBoxHeight: number;
  confidence: number;
  frameQuality: number;
  speed?: number;
  imagePath?: string;
}

