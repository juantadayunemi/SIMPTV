/**
 * Entidades de Notificaciones
 * Modelos para sistema de notificaciones y configuraciones de usuario
 */

import { NotificationTypeKey } from "../types/trafficTypes";

// ============= NOTIFICATION ENTITIES =============

export interface NotificationEntity {
  id: string;
  type: NotificationTypeKey;
  title: string;
  message: string;
  data?: string; // JSON serialized
  userId?: string;
  isRead: boolean;
  readAt?: Date;
  createdAt: Date;
}

export interface NotificationSettingsEntity {
  id: string;
  userId: string;
  emailEnabled: boolean;
  whatsappEnabled: boolean;
  webNotificationsEnabled: boolean;
  trafficAlertsEnabled: boolean;
  plateDetectionEnabled: boolean;
  systemAlertsEnabled: boolean;
  updatedAt: Date;
}