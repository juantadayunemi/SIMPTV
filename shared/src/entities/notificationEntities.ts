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

export interface NotificationLogEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  user_id: number; // @db:foreignKey auth_app.User @db:int - Foreign Key a auth_app.User.id (CASCADE delete)
  notificationType: string; // @db:varchar(50) - Tipo: 'stolen_vehicle', 'traffic_violation', 'system_alert', 'test'
  title: string; // @db:varchar(200) - Título de la notificación (máx 200 caracteres)
  body: string; // @db:text - Cuerpo/mensaje de la notificación
  data?: object; // @db:json - Datos adicionales en JSON (ej: {placa: "ABC-123", location: "..."})
  fcmResponse?: object; // @db:json - Respuesta completa de Firebase (para debugging)
  success: boolean; // @db:bit @default(false) - Si se envió exitosamente
  sentAt: Date; // @db:datetime - Fecha/hora de envío (auto_now_add)
  createdAt: Date; // @db:datetime - Fecha de creación del registro (auto_now_add)
  
  // ÍNDICES EN TABLA:
  // - INDEX(user, notificationType) - Para queries: "notificaciones de tipo X para usuario Y"
  // - INDEX(sentAt) - Para queries: "notificaciones enviadas entre fechas"
}