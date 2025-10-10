/**
 * Entidades de Análisis de Tráfico
 * Modelos para análisis de tráfico vehicular y detección de vehículos
 * 
 * ANOTACIONES PARA GENERADOR DJANGO (SQL Server):
 * 
 * @db:primary - Campo primary key
 * @db:identity - IDENTITY(1,1) autoincremental en SQL Server
 * @db:foreignKey ModelName - Foreign Key a otro modelo
 * @db:varchar(n) - VARCHAR(n) en SQL Server
 * @db:int - INT en SQL Server (default para number)
 * @db:bigint - BIGINT en SQL Server
 * @db:float - FLOAT en SQL Server
 * @db:decimal(p,s) - DECIMAL(precision, scale)
 * @db:text - TEXT/NVARCHAR(MAX)
 * @db:datetime - DATETIME2 en SQL Server
 * @default(value) - Valor por defecto (ej: @default(0), @default(cuid()))
 * 
 * REGLAS AUTOMÁTICAS:
 * - `field?: type` → blank=True, null=True en Django
 * - `field: type` (sin ?) → blank=False, null=False
 * - `id: number` → BigAutoField (IDENTITY) automático
 * - `*Id: number` → IntegerField (FK se define con @db:foreignKey)
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
  id: number; // @db:primary @db:identity - ID autoincremental
  description: string; // @db:varchar(500) - Ej: "Ave. 5 de Octubre y Córdova"
  latitude: number; // @db:decimal(11,8) - Latitud GPS (Ej: -2.145960) - Rango: -90 a +90
  longitude: number; // @db:decimal(12,8) - Longitud GPS (Ej: -79.889264) - Rango: -180 a +180
  city?: string; // @db:varchar(100) - Ciudad (Ej: "Milagro")
  province?: string; // @db:varchar(100) - Provincia (Ej: "Guayas")
  country: string; // @db:varchar(100) - País (Ej: "Ecuador")
  notes?: string; // @db:text - Notas adicionales sobre la ubicación
  isActive: boolean; // @default(true) - Si la ubicación está activa
  createdAt: Date; // @db:datetime - Fecha de creación
  updatedAt: Date; // @db:datetime - Fecha de última actualización
}

// ============================================
// ENTIDAD: CAMERA (Cámara de Vigilancia)
// ============================================

export interface CameraEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  name: string; // @db:varchar(100) - Nombre identificador (Ej: "CAM-001-Centro")
  brand?: string; // @db:varchar(50) - Marca de la cámara (Ej: "Hikvision")
  model?: string; // @db:varchar(50) - Modelo (Ej: "DS-2CD2143G0-I")
  resolution?: string; // @db:varchar(20) - Resolución (Ej: "1920x1080")
  fps?: number; // @db:int - Frames por segundo (Ej: 30)
  locationId: number; // @db:foreignKey Location @db:int - FK a Location (se actualiza cuando la cámara se mueve)
  isActive: boolean; // @default(true) - Si la cámara está activa
  lanes: number; // @db:int @default(2) - Número de carriles que cubre (Ej: 2, 4)
  coversBothDirections: boolean; // @default(false) - Si cubre ambas direcciones del tráfico
  notes?: string; // @db:text - Notas adicionales (puede incluir historial de ubicaciones si necesario)
  createdAt: Date; // @db:datetime - Fecha de creación
  updatedAt: Date; // @db:datetime - Fecha de última actualización (se actualiza al mover la cámara)
}

// ============================================
// ENTIDAD: TRAFFIC ANALYSIS (Sesión de Análisis)
// ============================================

export interface TrafficAnalysisEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  cameraId: number; // @db:foreignKey Camera @db:int - FK a Camera
  locationId: number; // @db:foreignKey Location @db:int - FK a Location (ubicación en el momento del análisis)
  videoPath?: string; // @db:varchar(500) - Ruta del video (si es desde archivo)
  userId?: number; // @db:int - FK a User que inició el análisis
  
  // Metadatos de la sesión
  startedAt: Date; // @db:datetime - Fecha/hora de inicio del análisis
  endedAt?: Date; // @db:datetime - Fecha/hora de finalización del análisis
  duration?: number; // @db:int - Duración en segundos
  
  // Estadísticas de procesamiento (agregadas para video analysis)
  totalFrames: number; // @db:int @default(0) - Total de frames en el video
  processedFrames: number; // @db:int @default(0) - Frames procesados hasta ahora
  totalVehicles: number; // @db:int @default(0) - Total de vehículos únicos detectados
  processingDuration: number; // @db:int @default(0) - Duración del procesamiento en segundos
  
  // Estadísticas calculadas
  totalVehicleCount: number; // @db:int @default(0) - Total de vehículos únicos detectados
  avgSpeed?: number; // @db:decimal(6,2) - Velocidad promedio en km/h
  densityLevel: DensityLevelKey; // @db:varchar(10) - Nivel de densidad del tráfico
  
  // Datos adicionales
  weatherConditions?: string; // @db:varchar(100) - Condiciones climáticas (Ej: "Soleado", "Lluvioso")
  analysisData?: string; // @db:text - JSON serializado con datos adicionales del análisis
  status: AnalysisStatusKey; // @db:varchar(20) - Estado del análisis
  errorMessage?: string; // @db:text - Mensaje de error si status = FAILED
  
  // Conteos por tipo de vehículo (calculados)
  carCount: number; // @db:int @default(0) - Cantidad de autos
  truckCount: number; // @db:int @default(0) - Cantidad de camiones
  motorcycleCount: number; // @db:int @default(0) - Cantidad de motocicletas
  busCount: number; // @db:int @default(0) - Cantidad de buses
  bicycleCount: number; // @db:int @default(0) - Cantidad de bicicletas
  otherCount: number; // @db:int @default(0) - Cantidad de otros vehículos
  
  createdAt: Date; // @db:datetime - Fecha de creación del registro
  updatedAt: Date; // @db:datetime - Fecha de última actualización
}

// ============================================
// ENTIDAD: VEHICLE (Vehículo Detectado Único)
// ============================================

export interface VehicleEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID generado en frontend para tracking único
  trafficAnalysisId: number; // @db:foreignKey TrafficAnalysis @db:int - FK a TrafficAnalysis
  
  // Información del vehículo
  vehicleType: VehicleTypeKey; // @db:varchar(20) - Tipo de vehículo detectado
  confidence: number; // @db:decimal(5,4) - Confianza promedio de la detección (0-1)
  
  // Tracking temporal
  firstDetectedAt: Date; // @db:datetime - Primera vez que se detectó
  lastDetectedAt: Date; // @db:datetime - Última vez que se detectó
  trackingStatus: TrackingStatusKey; // @db:varchar(20) - Estado del tracking
  
  // Análisis de movimiento
  avgSpeed?: number; // @db:decimal(6,2) - Velocidad promedio durante su recorrido (km/h)
  direction?: TrafficDirectionKey; // @db:varchar(20) - Dirección de movimiento
  lane?: number; // @db:int - Carril en el que se detectó mayormente (1, 2, 3, etc)
  
  // Frames almacenados
  totalFrames: number; // @db:int @default(0) - Total de frames donde fue detectado
  storedFrames: number; // @db:int @default(0) - Total de frames guardados en BD (muestreo)
  
  // Metadatos
  color?: string; // @db:varchar(50) - Color del vehículo (si se puede detectar)
  brand?: string; // @db:varchar(50) - Marca (si se puede detectar)
  model?: string; // @db:varchar(50) - Modelo (si se puede detectar)
  
  // Procesamiento de placa
  plateProcessingStatus: PlateProcessingStatusKey; // @db:varchar(20) - Estado del procesamiento de placa
  bestFrameForPlate?: number; // @db:int - Número del mejor frame para OCR de placa
  
  // Timestamps
  createdAt: Date; // @db:datetime - Fecha de creación

}


// ============================================
// ENTIDAD: VEHICLE FRAME (Frames del Vehículo)
// ============================================

export interface VehicleFrameEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  vehicleId: string; // @db:foreignKey Vehicle @db:varchar(50) - FK a Vehicle (CUID)
  
  // Información del frame
  frameNumber: number; // @db:int - Número de frame en el video
  timestamp: Date; // @db:datetime - Timestamp exacto del frame
  
  // Bounding Box (coordenadas del rectángulo de detección)
  boundingBoxX: number; // @db:int - Posición X (esquina superior izquierda)
  boundingBoxY: number; // @db:int - Posición Y (esquina superior izquierda)
  boundingBoxWidth: number; // @db:int - Ancho del rectángulo de detección
  boundingBoxHeight: number; // @db:int - Alto del rectángulo de detección
  
  // Calidad del frame
  confidence: number; // @db:decimal(5,4) - Nivel de confianza de detección en este frame (0-1)
  frameQuality: number; // @db:decimal(5,4) - Calidad del frame para OCR (0-1, calculado por nitidez/iluminación)
  
  // Datos adicionales
  speed?: number; // @db:decimal(6,2) - Velocidad instantánea en este frame (km/h)
  imagePath?: string; // @db:varchar(500) - Ruta de la imagen del frame (si se guarda)
  
  createdAt: Date; // @db:datetime - Fecha de creación
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

