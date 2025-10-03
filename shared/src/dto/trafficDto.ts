/**
 * DTOs para Análisis de Tráfico
 * Objetos de transferencia de datos específicos para análisis de tráfico
 */

import { 
  AnalysisStatusKey, 
  DensityLevelKey, 
  TrafficDirectionKey, 
  TrackingStatusKey, 
  VehicleTypeKey 
} from "../types/trafficTypes";

// ============================================
// RESPONSE DTOs (Para Frontend)
// ============================================

// DTO optimizado para mostrar análisis en listas/dashboards
export interface TrafficAnalysisResponseDTO {
  id: number;
  cameraName: string;
  locationDescription: string; // Ej: "Ave. 5 de Octubre y Córdova"
  locationCoordinates: {
    latitude: number;
    longitude: number;
  };
  
  // Estado del análisis
  status: AnalysisStatusKey;
  progress?: number; // 0-100 para análisis en progreso
  
  // Metadatos de tiempo
  startedAt: Date;
  endedAt?: Date;
  duration?: number; // en segundos
  
  // Estadísticas principales
  totalVehicleCount: number;
  avgSpeed?: number;
  densityLevel: DensityLevelKey;
  
  // Desglose por tipo de vehículo
  vehicleBreakdown: VehicleTypeBreakdownDTO[];
  
  // Datos adicionales
  weatherConditions?: string;
  errorMessage?: string; // Si status = FAILED
  
  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

// Desglose de vehículos por tipo con porcentajes
export interface VehicleTypeBreakdownDTO {
  type: VehicleTypeKey;
  count: number;
  percentage: number;
}

// DTO para mostrar un vehículo detectado individual
export interface VehicleDetectionResponseDTO {
  id: string; // CUID
  vehicleType: VehicleTypeKey;
  confidence: number;
  
  // Información temporal
  firstDetectedAt: Date;
  lastDetectedAt: Date;
  trackingStatus: TrackingStatusKey;
  
  // Análisis de movimiento
  avgSpeed?: number;
  direction?: TrafficDirectionKey;
  lane?: number;
  
  // Frames y evidencia
  totalFrames: number;
  storedFrames: number;
  bestFrameImage?: string; // URL de la mejor imagen
  
  // Metadatos del vehículo
  color?: string;
  brand?: string;
  model?: string;
  
  // Estado de placa
  plateProcessingStatus: string;
  plateDetected?: boolean;
  plateNumber?: string;
  plateConfidence?: number;
}

// DTO para frame individual con bounding box
export interface VehicleFrameResponseDTO {
  id: number;
  frameNumber: number;
  timestamp: Date;
  
  // Bounding Box
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  
  // Calidad y confianza
  confidence: number;
  frameQuality: number;
  
  // Datos adicionales
  speed?: number;
  imagePath?: string;
}

// DTO para estadísticas de ubicación
export interface LocationStatsResponseDTO {
  locationId: number;
  description: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  
  // Estadísticas de análisis
  totalAnalyses: number;
  activeAnalyses: number;
  avgVehiclesPerAnalysis: number;
  avgDailyTraffic: number;
  
  // Tendencias
  hourlyTrend: HourlyTrafficDTO[];
  vehicleTypeTrend: VehicleTypeBreakdownDTO[];
  
  // Última actividad
  lastAnalysisAt?: Date;
}

// DTO para tendencia de tráfico por hora
export interface HourlyTrafficDTO {
  hour: number; // 0-23
  vehicleCount: number;
  avgSpeed?: number;
  densityLevel: DensityLevelKey;
}

// DTO para estadísticas de cámara
export interface CameraStatsResponseDTO {
  id: number;
  name: string;
  brand?: string;
  model?: string;
  
  // Estado
  isActive: boolean;
  currentLocation: {
    id: number;
    description: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
  };
  
  // Configuración
  lanes: number;
  coversBothDirections: boolean;
  
  // Estadísticas de uso
  totalAnalyses: number;
  totalVehiclesDetected: number;
  avgAnalysisDuration: number;
  
  // Última actividad
  lastUsedAt?: Date;
}

// ============================================
// REQUEST DTOs (Para Backend)
// ============================================

// DTO para crear nuevo análisis
export interface CreateTrafficAnalysisRequestDTO {
  cameraId: number;
  locationId?: number; // Opcional si la cámara ya tiene ubicación fija
  videoPath?: string; // Para análisis de archivo de video
  weatherConditions?: string;
  
  // Configuración del análisis
  maxDuration?: number; // Límite en segundos
  sampleRate?: number; // Cada cuántos frames procesar
  enablePlateDetection?: boolean;
}

// DTO para actualizar análisis en progreso
export interface UpdateTrafficAnalysisRequestDTO {
  status?: AnalysisStatusKey;
  progress?: number;
  errorMessage?: string;
  
  // Estadísticas parciales (se van actualizando)
  totalVehicleCount?: number;
  avgSpeed?: number;
  densityLevel?: DensityLevelKey;
  
  // Conteos por tipo
  carCount?: number;
  truckCount?: number;
  motorcycleCount?: number;
  busCount?: number;
  bicycleCount?: number;
  otherCount?: number;
}

// DTO para reportar detección de vehículo
export interface ReportVehicleDetectionRequestDTO {
  trafficAnalysisId: number;
  vehicleId: string; // CUID generado en frontend
  vehicleType: VehicleTypeKey;
  confidence: number;
  
  // Frame inicial
  firstFrame: {
    frameNumber: number;
    timestamp: Date;
    boundingBox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    confidence: number;
    frameQuality: number;
  };
  
  // Datos opcionales
  direction?: TrafficDirectionKey;
  lane?: number;
  color?: string;
}

// DTO para agregar frame a vehículo existente
export interface AddVehicleFrameRequestDTO {
  vehicleId: string;
  frameNumber: number;
  timestamp: Date;
  
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  
  confidence: number;
  frameQuality: number;
  speed?: number;
  imagePath?: string;
}

// DTO para finalizar tracking de vehículo
export interface FinalizeVehicleTrackingRequestDTO {
  vehicleId: string;
  lastDetectedAt: Date;
  trackingStatus: TrackingStatusKey;
  
  // Estadísticas finales
  avgSpeed?: number;
  finalDirection?: TrafficDirectionKey;
  finalLane?: number;
  
  // Metadatos finales
  color?: string;
  brand?: string;
  model?: string;
}

// ============================================
// QUERY DTOs (Para filtros y búsquedas)
// ============================================

// DTO para filtrar análisis de tráfico
export interface TrafficAnalysisQueryDTO {
  // Filtros básicos
  cameraId?: number;
  locationId?: number;
  status?: AnalysisStatusKey[];
  
  // Filtros de tiempo
  startDate?: Date;
  endDate?: Date;
  
  // Filtros de resultados
  minVehicleCount?: number;
  maxVehicleCount?: number;
  densityLevel?: DensityLevelKey[];
  
  // Filtros adicionales
  hasVideoFile?: boolean;
  weatherConditions?: string[];
  
  // Paginación y ordenamiento
  page?: number;
  limit?: number;
  sortBy?: 'startedAt' | 'totalVehicleCount' | 'avgSpeed' | 'duration';
  sortOrder?: 'asc' | 'desc';
}

// DTO para buscar vehículos detectados
export interface VehicleSearchQueryDTO {
  // Filtros básicos
  trafficAnalysisId?: number;
  vehicleType?: VehicleTypeKey[];
  trackingStatus?: TrackingStatusKey[];
  
  // Filtros de tiempo
  detectedAfter?: Date;
  detectedBefore?: Date;
  
  // Filtros de características
  minConfidence?: number;
  hasPlateDetection?: boolean;
  direction?: TrafficDirectionKey[];
  lane?: number[];
  
  // Filtros de velocidad
  minSpeed?: number;
  maxSpeed?: number;
  
  // Filtros de frames
  minFrames?: number;
  maxFrames?: number;
  
  // Paginación
  page?: number;
  limit?: number;
  sortBy?: 'firstDetectedAt' | 'confidence' | 'totalFrames' | 'avgSpeed';
  sortOrder?: 'asc' | 'desc';
}

// DTO para estadísticas agregadas
export interface TrafficStatsQueryDTO {
  // Rango de tiempo
  startDate: Date;
  endDate: Date;
  
  // Filtros de ubicación
  locationIds?: number[];
  cameraIds?: number[];
  
  // Agrupación
  groupBy?: 'hour' | 'day' | 'week' | 'month' | 'location' | 'camera';
  
  // Métricas específicas
  includeVehicleTypes?: boolean;
  includeSpeedStats?: boolean;
  includeDensityStats?: boolean;
}