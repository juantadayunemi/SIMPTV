// User Roles Constants
// shared/src/types/roleTypes.ts

export const USER_ROLES = {
  ADMIN: 'ADMIN' as const,
  OPERATOR: 'OPERATOR' as const,
  VIEWER: 'VIEWER' as const
} as const;

export const PERMISSIONS = {
  // Traffic Analysis
  TRAFFIC_CREATE: 'traffic:create' as const,
  TRAFFIC_READ: 'traffic:read' as const,
  TRAFFIC_UPDATE: 'traffic:update' as const,
  TRAFFIC_DELETE: 'traffic:delete' as const,
  
  // Plate Detection
  PLATE_CREATE: 'plate:create' as const,
  PLATE_READ: 'plate:read' as const,
  PLATE_UPDATE: 'plate:update' as const,
  PLATE_DELETE: 'plate:delete' as const,
  
  // Users Management
  USER_CREATE: 'user:create' as const,
  USER_READ: 'user:read' as const,
  USER_UPDATE: 'user:update' as const,
  USER_DELETE: 'user:delete' as const,
  
  // System
  SYSTEM_ADMIN: 'system:admin' as const,
  SETTINGS_MANAGE: 'settings:manage' as const,
  NOTIFICATIONS_MANAGE: 'notifications:manage' as const,
} as const;

export const ROLE_PERMISSIONS = {
  [USER_ROLES.ADMIN]: [
    PERMISSIONS.TRAFFIC_CREATE,
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.TRAFFIC_UPDATE,
    PERMISSIONS.TRAFFIC_DELETE,
    PERMISSIONS.PLATE_CREATE,
    PERMISSIONS.PLATE_READ,
    PERMISSIONS.PLATE_UPDATE,
    PERMISSIONS.PLATE_DELETE,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_READ,
    PERMISSIONS.USER_UPDATE,
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.SYSTEM_ADMIN,
    PERMISSIONS.SETTINGS_MANAGE,
    PERMISSIONS.NOTIFICATIONS_MANAGE
  ],
  [USER_ROLES.OPERATOR]: [
    PERMISSIONS.TRAFFIC_CREATE,
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.TRAFFIC_UPDATE,
    PERMISSIONS.PLATE_CREATE,
    PERMISSIONS.PLATE_READ,
    PERMISSIONS.PLATE_UPDATE,
    PERMISSIONS.USER_READ,
    PERMISSIONS.NOTIFICATIONS_MANAGE
  ],
  [USER_ROLES.VIEWER]: [
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.PLATE_READ,
    PERMISSIONS.USER_READ
  ]
} as const;


export type UserRoleType = typeof USER_ROLES[keyof typeof USER_ROLES];
export type PermissionType = typeof PERMISSIONS[keyof typeof PERMISSIONS];