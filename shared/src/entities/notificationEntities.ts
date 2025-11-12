/**
 * Entidades de Notificaciones
 * Modelos para sistema de notificaciones FCM y registro de logs
 * shared/src/entities/notificationEntities.ts
 * 
 * ANOTACIONES PARA GENERADOR DJANGO (SQL Server):
 * 
 * @db:primary - Campo primary key
 * @db:identity - IDENTITY(1,1) autoincremental en SQL Server
 * @db:unique - Restricción UNIQUE en SQL Server
 * @db:foreignKey ModelName - Foreign Key a otro modelo (on_delete=CASCADE)
 * @db:varchar(n) - VARCHAR(n) en SQL Server
 * @db:int - INT en SQL Server (default para number)
 * @db:datetime - DATETIME2 en SQL Server
 * @db:bit - BIT (boolean) en SQL Server
 * @db:json - JSON en SQL Server
 * @db:text - TEXT/NVARCHAR(MAX)
 * @default(value) - Valor por defecto (ej: @default(true), @default(false))
 * 
 * REGLAS AUTOMÁTICAS:
 * - `field?: type` → blank=True, null=True en Django
 * - `field: type` (sin ?) → blank=False, null=False
 * - `id: number` → BigAutoField (IDENTITY) automático
 * 
 * CONVENCIÓN: camelCase (estándar TypeScript)
 * El backend (Django) usa snake_case internamente.
 * La conversión es automática en la capa API (CamelCaseJSONRenderer).
 * 
 * Ejemplo:
 * - Frontend: deviceName, isActive, createdAt
 * - Backend:  device_name, is_active, created_at
 * - API JSON: deviceName, isActive, createdAt (camelCase)
 */

import { NotificationTypeKey } from "../types/notificationTypes";

// ============= FCM DEVICE ENTITY =============
// Almacena tokens de dispositivos registrados para enviar notificaciones push

export interface FCMDeviceEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  user_id: number; // @db:foreignKey auth_app.User @db:int - Foreign Key a auth_app.User.id (CASCADE delete)
  token: string; // @db:varchar(255) @db:unique - Token FCM único de Firebase Cloud Messaging
  deviceName?: string; // @db:varchar(100) - Nombre del dispositivo (ej: "iPhone de Juan", "Laptop Oficina")
  deviceType?: string; // @db:varchar(50) - Tipo: 'ios', 'android', 'web'
  isActive: boolean; // @db:bit @default(true) - Si el dispositivo está activo para recibir notificaciones
  createdAt: Date; // @db:datetime - Fecha de registro del dispositivo (auto_now_add)
  updatedAt: Date; // @db:datetime - Fecha de última actualización (auto_now)
  lastUsedAt?: Date; // @db:datetime - Última vez que se usó este token para enviar notificación (opcional)
  
  // ÍNDICES EN TABLA:
  // - INDEX(user, isActive) - Para queries: "dame tokens activos de este usuario"
  // - INDEX(token) - Para queries: "busca este token específico"
}

// ============= NOTIFICATION LOG ENTITY =============
// Registro histórico de todas las notificaciones enviadas (auditoría y debugging)

export interface NotificationData {
  type?: string;
  plate_number?: string;
  owner_name?: string;
  complaints_count?: string;
  severity?: string;
  case_number?: string;
  location?: string;
  time?: string;
  is_grouped?: string;
  detection_count?: string;
  time_window_minutes?: string;
  locations?: string;
  detected_plate_id?: number;
  // Datos cacheados de la denuncia (se obtienen al expandir)
  complaintDetails?: {
    detection: {
      id: number;
      ownerName: string;
      ownerIdNumber: string;
      ownerAddress: string;
      caseNumber: string;
      severity: string;
    };
    complaints: Array<{
      id: number;
      complaintText: string;
      complaintType: string | null;
      complaintDate: string | null;
      severity: string;
      sequenceNumber: number;
      createdAt: string;
    }>;
    complaintsCount: number;
  };
}


export interface NotificationLogEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  user_id: number; // @db:foreignKey auth_app.User @db:int - Foreign Key a auth_app.User.id (CASCADE delete)
  notificationType: NotificationTypeKey; // @db:varchar(50) @default(SYSTEM_ALERT) - Tipo: 'stolen_vehicle', 'traffic_violation', 'system_alert', 'test'
  title: string; // @db:varchar(200) - Título de la notificación (máx 20s0 caracteres)
  body: string; // @db:text - Cuerpo/mensaje de la notificación
  data?: NotificationData; // @db:json - Datos adicionales en JSON (ej: {placa: "ABC-123", location: "..."})
  fcmResponse?: object; // @db:json - Respuesta completa de Firebase (para debugging)
  success: boolean; // @db:bit @default(false) - Si se envió exitosamente
  sentAt: Date; // @db:datetime - Fecha/hora de envío (auto_now_add)
  createdAt: Date; // @db:datetime - Fecha de creación del registro (auto_now_add)
   
  // ÍNDICES EN TABLA:
  // - INDEX(user, notificationType) - Para queries: "notificaciones de tipo X para usuario Y"
  // - INDEX(sentAt) - Para queries: "notificaciones enviadas entre fechas"
}




export interface NotificationSettingsEntity {
  id: number;
  userId: number;
  emailEnabled: boolean;
  whatsappEnabled: boolean;
  webNotificationsEnabled: boolean;
  trafficAlertsEnabled: boolean;
  plateDetectionEnabled: boolean;
  systemAlertsEnabled: boolean;
  updatedAt: Date;
}


// ============= NOTIFICATION BOTTLENECK ENTITIES =============
// Notificaciones específicas para cuellos de botella detectados en cámaras de tráfico  
// ============================================

export interface NotificationBottleNeckEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  userId: number; // @db:foreignKey auth_app.User @db:int - FK al usuario que recibe la notificación
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la cámara)
  cameraId: number; // @db:foreignKey traffic_app.Camera @db:int - FK a Camera (cámara específica)
  isActive: boolean; // @default(true) - Si la notificación está activa
  createdAt: Date; // @db:datetime - Fecha de creación
  updatedAt: Date; // @db:datetime - Fecha de actualización
}

export interface NotificationBottleNeckLogEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  notificationBottleNeckId: number; // @db:foreignKey notifications_app.NotificationBottleNeck @db:int - FK a NotificationBottleNeck
  sentAt: Date; // @db:datetime - Fecha/hora de envío
  message: string; // @db:text - Mensaje enviado
  createdAt: Date; // @db:datetime - Fecha de creación
  wasSuccessful: boolean; // @default(true) - Si el envío fue exitoso
}

export interface NotificationTaskEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  notificationBottleNeckId: number; // @db:foreignKey notifications_app.NotificationBottleNeck @db:int - FK a NotificationBottleNeck
  taskId: string; // @db:varchar(255) @db:unique - ID de la tarea programada (scheduler task ID) unique
  scheduleFor: Date; // @db:datetime - Fecha/hora programada para la notificación
  createdAt: Date; // @db:datetime - Fecha de creación
  isActive: boolean; // @default(true) - Si la tarea está activa
}


