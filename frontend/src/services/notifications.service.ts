import api from './api';

export type NotificationType = 'EMAIL' | 'SMS' | 'PUSH';
export type NotificationStatus = 'PENDING' | 'SENT' | 'FAILED' | 'DELIVERED';

export interface Notification {
  id: string;
  type: NotificationType;
  recipient: string;
  subject?: string;
  message: string;
  status: NotificationStatus;
  sentAt?: string;
  deliveredAt?: string;
  errorMessage?: string;
  metadata?: Record<string, any>;
  createdAt: string;
}

export interface CreateNotificationData {
  type: NotificationType;
  recipient: string;
  subject?: string;
  message: string;
  metadata?: Record<string, any>;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  type: NotificationType;
  subject?: string;
  template: string;
  variables: string[];
  isActive: boolean;
  createdAt: string;
}

export interface CreateTemplateData {
  name: string;
  type: NotificationType;
  subject?: string;
  template: string;
  variables: string[];
}

export interface NotificationSettings {
  emailEnabled: boolean;
  smsEnabled: boolean;
  pushEnabled: boolean;
  emailProvider: 'sendgrid' | 'smtp';
  smsProvider: 'twilio' | 'aws';
  emailConfig?: Record<string, any>;
  smsConfig?: Record<string, any>;
}

class NotificationService {
  // Send notification
  async sendNotification(data: CreateNotificationData): Promise<Notification> {
    const response = await api.post('/api/notifications/send', data);
    return response.data;
  }

  // Send bulk notifications
  async sendBulkNotifications(notifications: CreateNotificationData[]): Promise<{
    sent: number;
    failed: number;
    results: Array<{
      recipient: string;
      success: boolean;
      notificationId?: string;
      error?: string;
    }>;
  }> {
    const response = await api.post('/api/notifications/bulk-send', { notifications });
    return response.data;
  }

  // Get notifications
  async getNotifications(params?: {
    type?: NotificationType;
    status?: NotificationStatus;
    recipient?: string;
    startDate?: string;
    endDate?: string;
    page?: number;
    limit?: number;
  }): Promise<Notification[]> {
    const response = await api.get('/api/notifications', { params });
    return response.data;
  }

  // Get specific notification
  async getNotification(notificationId: string): Promise<Notification> {
    const response = await api.get(`/api/notifications/${notificationId}`);
    return response.data;
  }

  // Retry failed notification
  async retryNotification(notificationId: string): Promise<Notification> {
    const response = await api.post(`/api/notifications/${notificationId}/retry`);
    return response.data;
  }

  // Cancel pending notification
  async cancelNotification(notificationId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/notifications/${notificationId}`);
    return response.data;
  }

  // Get notification templates
  async getTemplates(type?: NotificationType): Promise<NotificationTemplate[]> {
    const response = await api.get('/api/notifications/templates', {
      params: { type }
    });
    return response.data;
  }

  // Get specific template
  async getTemplate(templateId: string): Promise<NotificationTemplate> {
    const response = await api.get(`/api/notifications/templates/${templateId}`);
    return response.data;
  }

  // Create notification template
  async createTemplate(templateData: CreateTemplateData): Promise<NotificationTemplate> {
    const response = await api.post('/api/notifications/templates', templateData);
    return response.data;
  }

  // Update template
  async updateTemplate(templateId: string, templateData: Partial<CreateTemplateData>): Promise<NotificationTemplate> {
    const response = await api.put(`/api/notifications/templates/${templateId}`, templateData);
    return response.data;
  }

  // Delete template
  async deleteTemplate(templateId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/notifications/templates/${templateId}`);
    return response.data;
  }

  // Send notification from template
  async sendFromTemplate(templateId: string, data: {
    recipient: string;
    variables: Record<string, any>;
  }): Promise<Notification> {
    const response = await api.post(`/api/notifications/templates/${templateId}/send`, data);
    return response.data;
  }

  // Get notification settings
  async getSettings(): Promise<NotificationSettings> {
    const response = await api.get('/api/notifications/settings');
    return response.data;
  }

  // Update notification settings
  async updateSettings(settings: Partial<NotificationSettings>): Promise<NotificationSettings> {
    const response = await api.put('/api/notifications/settings', settings);
    return response.data;
  }

  // Test notification settings
  async testSettings(type: NotificationType, recipient: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post('/api/notifications/test', {
      type,
      recipient
    });
    return response.data;
  }

  // Get notification statistics
  async getStatistics(params?: {
    startDate?: string;
    endDate?: string;
    type?: NotificationType;
  }): Promise<{
    totalSent: number;
    totalFailed: number;
    successRate: number;
    typeBreakdown: Record<NotificationType, number>;
    statusBreakdown: Record<NotificationStatus, number>;
    dailyStats: Array<{
      date: string;
      sent: number;
      failed: number;
    }>;
  }> {
    const response = await api.get('/api/notifications/statistics', { params });
    return response.data;
  }
}

export const notificationService = new NotificationService();
export default notificationService;