import { DataTypeKey } from "../types/dataTypes";
import { NotificationTypeKey } from "../types/notificationTypes";


// ============= NOTIFICATION INTERFACES =============
export interface NotificationPayload {
  id: string;
  type: NotificationTypeKey;
  title: string;
  message: string;
  data?: any;
  userId?: string;
  createdAt: Date;
  readAt?: Date;
}

export interface EmailNotification {
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  htmlContent: string;
  textContent?: string;
  templateId?: string;
  templateData?: Record<string, any>;
}

export interface WhatsAppNotification {
  to: string;
  message: string;
  mediaUrl?: string;
  templateName?: string;
  templateVariables?: string[];
}

export interface WebSocketNotification {
  event: string;
  data: any;
  room?: string;
  userId?: string;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  type: NotificationTypeKey;
  subject?: string;
  content: string;
  variables: TemplateVariable[];
}

export interface TemplateVariable {
  name: string;
  type: DataTypeKey;
  required: boolean;
  defaultValue?: any;
}

export interface NotificationSettings {
  userId: string;
  emailEnabled: boolean;
  whatsappEnabled: boolean;
  webNotificationsEnabled: boolean;
  trafficAlertsEnabled: boolean;
  plateDetectionEnabled: boolean;
  systemAlertsEnabled: boolean;
}
