/**
 * Entidades de Detección de Placas y Denuncias Vehiculares
 * Modelos para reconocimiento OCR, consulta de denuncias y evidencias
 * 
 * ANOTACIONES PARA GENERADOR DJANGO (SQL Server):
 * 
 * @db:primary - Campo primary key
 * @db:identity - IDENTITY(1,1) autoincremental en SQL Server
 * @db:foreignKey app_name.ModelName - Foreign Key a otro modelo (formato: app_name.ModelName)
 * @db:varchar(n) - VARCHAR(n) en SQL Server
 * @db:int - INT en SQL Server (default para number)
 * @db:bigint - BIGINT en SQL Server
 * @db:float - FLOAT en SQL Server
 * @db:decimal(p,s) - DECIMAL(precision, scale)
 * @db:text - TEXT/NVARCHAR(MAX)
 * @db:datetime - DATETIME2 en SQL Server
 * @db:unique - Restricción UNIQUE en SQL Server
 * @db:json - JSON en SQL Server
 * @default(value) - Valor por defecto (ej: @default(0), @default(cuid()))
 * 
 * REGLAS AUTOMÁTICAS:
 * - `field?: type` → blank=True, null=True en Django
 * - `field: type` (sin ?) → blank=False, null=False
 * - `id: number` → BigAutoField (IDENTITY) automático
 * - `*Id: number` → IntegerField (FK se define con @db:foreignKey app_name.ModelName)
 */

// ============================================
// ENTIDAD: DETECTED PLATE (Todas las Placas Detectadas)
// ============================================

export interface DetectedPlateEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  trafficAnalysisId: number; // @db:foreignKey traffic_app.TrafficAnalysis @db:int - FK a TrafficAnalysis
  vehicleId?: string; // @db:foreignKey traffic_app.Vehicle @db:varchar(50) - FK a Vehicle (tracking ID único de esa pasada)
  
  // Datos de la placa detectada
  plateNumber: string; // @db:varchar(20) - Número de placa detectado por OCR (Ej: "ABC-1234")
  confidence: number; // @db:decimal(5,4) - Confianza de la detección OCR (0.0-1.0)
  detectionMethod: string; // @db:varchar(50) - Método usado: 'roboflow', 'haarcascade', 'contours', 'color'
  
  // Contexto del frame
  frameNumber: number; // @db:int - Número de frame donde se detectó la placa
  frameQuality: number; // @db:decimal(5,4) - Calidad del frame (0.0-1.0, nitidez/iluminación)
  detectedAt: Date; // @db:datetime - Fecha/hora de detección
  
  // Control de consulta a API gubernamental
  wasCheckedForComplaints: boolean; // @default(false) - Si se consultó en la API de denuncias
  checkedAt?: Date; // @db:datetime - Fecha/hora de consulta a la API
  hasComplaints: boolean; // @default(false) - Si tiene denuncias registradas
  
  // Timestamps
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}

// ============================================
// ENTIDAD: DETECTED PLATE IMAGE (Imágenes Locales de Detección)
// ============================================

export interface DetectedPlateImageEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  detectedPlateId: number; // @db:foreignKey plates_app.DetectedPlate @db:int - FK a DetectedPlate
  
  // Ruta de la imagen (local)
  localImagePath: string; // @db:varchar(500) - Ruta local de la imagen
  imageType: string; // @db:varchar(20) - Tipo: 'VEHICLE_FULL', 'VEHICLE_ROI', 'PLATE_ROI', 'PLATE_PROCESSED'
  
  // Metadatos de la imagen
  frameNumber: number; // @db:int - Número de frame del video
  capturedAt: Date; // @db:datetime - Fecha/hora de captura del frame
  fileSize?: number; // @db:int - Tamaño del archivo en bytes
  resolution?: string; // @db:varchar(20) - Resolución de la imagen (ej: "1920x1080")
  
  // Timestamps
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}

// ============================================
// ENTIDAD: VEHICLE COMPLAINT DETECTION (Cabecera de Denuncia)
// ============================================

export interface VehicleComplaintDetectionEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  detectedPlateId: number; // @db:foreignKey plates_app.DetectedPlate @db:int - FK a DetectedPlate (único)
  
  // Datos del propietario (desde API gubernamental)
  ownerName: string; // @db:varchar(200) - Nombre del propietario
  ownerIdNumber: string; // @db:varchar(32) - Cédula del propietario
  ownerAddress: string; // @db:varchar(400) - Dirección del propietario
  caseNumber: string; // @db:varchar(64) - Número de expediente
  
  // Resumen de denuncias
  totalComplaintsCount: number; // @db:int @default(0) - Cantidad TOTAL de denuncias de esta placa
  severity?: string; // @db:varchar(20) - Severidad (ALTA, MEDIA, BAJA) - calculado según cantidad/tipo
  
  // Control de notificaciones al operador
  wasNotified: boolean; // @default(false) - Si se envió notificación al operador
  notifiedAt?: Date; // @db:datetime - Fecha/hora de notificación
  
  // Metadata
  notes?: string; // @db:text - Notas adicionales del operador
  createdAt: Date; // @db:datetime - Fecha de creación del registro
  updatedAt: Date; // @db:datetime - Fecha de última actualización
}

// ============================================
// ENTIDAD: VEHICLE COMPLAINT (Denuncia Individual)
// ============================================

export interface VehicleComplaintEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  detectionId: number; // @db:foreignKey plates_app.VehicleComplaintDetection @db:int - FK a VehicleComplaintDetection
  
  // Contenido de la denuncia
  complaintText: string; // @db:text - Texto de la denuncia (ej: "Exceso de velocidad el 01/10/2025")
  complaintType?: string; // @db:varchar(50) - Tipo de denuncia extraído (VELOCIDAD, ESTACIONAMIENTO, ROBO, etc.)
  complaintDate?: Date; // @db:datetime - Fecha de la denuncia (si se puede extraer del texto)
  
  // Severidad individual de esta denuncia
  severity?: string; // @db:varchar(20) - Severidad individual (ALTA, MEDIA, BAJA)
  
  // Orden en la lista de denuncias (1, 2, 3...)
  sequenceNumber: number; // @db:int @default(1) - Orden de esta denuncia en la lista
  
  // Timestamps
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}

// ============================================
// ENTIDAD: COMPLAINT EVIDENCE IMAGE (Evidencias Subidas a Azure)
// ============================================

export interface ComplaintEvidenceImageEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  complaintDetectionId: number; // @db:foreignKey plates_app.VehicleComplaintDetection @db:int - FK a VehicleComplaintDetection
  detectedPlateImageId: number; // @db:foreignKey plates_app.DetectedPlateImage @db:int - FK a la imagen local original
  
  // URLs de Azure Blob Storage (evidencia en la nube)
  cloudUrl: string; // @db:varchar(500) - URL pública de Azure Blob Storage
  cloudBlobName: string; // @db:varchar(200) - Nombre del blob en Azure (ej: "evidence_123_vehicle.jpg")
  cloudContainerName: string; // @db:varchar(100) - Nombre del contenedor en Azure (ej: "traffic-evidence")
  
  // Control de subida
  uploadedAt: Date; // @db:datetime - Fecha/hora de subida a Azure
  uploadStatus: string; // @db:varchar(20) - Estado: 'PENDING', 'UPLOADING', 'COMPLETED', 'FAILED'
  uploadError?: string; // @db:text - Mensaje de error si falla la subida
  
  // Metadatos opcionales
  cloudFileSize?: number; // @db:int - Tamaño en bytes del archivo en Azure
  expiresAt?: Date; // @db:datetime - Fecha de expiración de la URL (si es temporal)
  notes?: string; // @db:text - Notas adicionales
  
  // Timestamps
  createdAt: Date; // @db:datetime - Fecha de creación del registro
  updatedAt: Date; // @db:datetime - Última actualización
}

// ============================================
// TIPOS AUXILIARES PARA FRONTEND (DTOs)
// ============================================

// DTO para crear registro de detección de placa
export interface CreateDetectedPlateDTO {
  trafficAnalysisId: number;
  vehicleId: string;
  plateNumber: string;
  confidence: number;
  detectionMethod: string; // 'roboflow', 'haarcascade', 'contours', 'color'
  frameNumber: number;
  frameQuality: number;
}

// DTO para crear imagen de placa detectada
export interface CreateDetectedPlateImageDTO {
  detectedPlateId: number;
  localImagePath: string;
  imageType: string; // 'VEHICLE_FULL', 'VEHICLE_ROI', 'PLATE_ROI', 'PLATE_PROCESSED'
  frameNumber: number;
  capturedAt: Date;
  fileSize?: number;
  resolution?: string;
}

// DTO para crear registro de detección de vehículo con denuncia
export interface CreateVehicleComplaintDetectionDTO {
  detectedPlateId: number;
  ownerName: string;
  ownerIdNumber: string;
  ownerAddress: string;
  caseNumber: string;
  totalComplaintsCount: number;
  severity?: string;
}

// DTO para crear una denuncia individual
export interface CreateVehicleComplaintDTO {
  detectionId: number;
  complaintText: string;
  complaintType?: string;
  complaintDate?: Date;
  severity?: string;
  sequenceNumber: number;
}

// DTO para crear imagen de evidencia en Azure
export interface CreateComplaintEvidenceImageDTO {
  complaintDetectionId: number;
  detectedPlateImageId: number; // Referencia a la imagen local original
  cloudUrl: string;
  cloudBlobName: string;
  cloudContainerName: string;
  uploadStatus: string; // 'COMPLETED', 'FAILED', etc.
  cloudFileSize?: number;
  uploadError?: string;
}

// DTO para actualizar notificación de denuncia
export interface UpdateComplaintNotificationDTO {
  id: number;
  wasNotified: boolean;
  notifiedAt: Date;
  notes?: string;
}

// DTO para actualizar subida a Azure
export interface UpdateCloudUploadDTO {
  id: number;
  uploadedToCloud: boolean;
  cloudUrl: string;
  cloudUploadedAt: Date;
  cloudBlobName: string;
  cloudContainerName: string;
}

// DTO para respuesta de la API gubernamental (mapeo directo)
export interface GovernmentAPIComplaintResponse {
  placa: string;
  propietario: {
    nombre: string;
    cedula: string;
  };
  ubicacion: {
    direccion: string;
  };
  denuncias: string[]; // Array de strings con las denuncias
  expediente: string;
}

