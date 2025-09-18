// Import all services
import { authService } from './auth.service';
import { trafficService } from './traffic.service';
import { plateService } from './plates.service';
import { userService } from './users.service';
import { notificationService } from './notifications.service';

// Re-export all services for easy importing
export { authService } from './auth.service';
export { trafficService } from './traffic.service';
export { plateService } from './plates.service';
export { userService } from './users.service';
export { notificationService } from './notifications.service';

// Re-export types
export type { User, LoginCredentials, RegisterData } from './auth.service';
export type { TrafficAnalysis, PlateDetection, CreateAnalysisData, TrafficPrediction, TrafficStatistics } from './traffic.service';
export type { PlateSearchResult, PlateStatistics } from './plates.service';
export type { UserRole, CreateUserData, UpdateUserData, UserWithRoles } from './users.service';
export type { 
  Notification, 
  NotificationType, 
  NotificationStatus, 
  CreateNotificationData, 
  NotificationTemplate, 
  CreateTemplateData, 
  NotificationSettings 
} from './notifications.service';

// Default export with all services
const services = {
  auth: authService,
  traffic: trafficService,
  plates: plateService,
  users: userService,
  notifications: notificationService
} as const;

export default services;