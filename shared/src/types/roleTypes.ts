// User Roles Constants
// shared/src/types/roleTypes.ts

export const USER_ROLES = {
  ADMIN: 'ADMIN' as const,
  OPERATOR: 'OPERATOR' as const,
  VIEWER: 'VIEWER' as const
} as const;

export const PERMISSIONS = {
  // Traffic Analysis
  TRAFFIC_CREATE: 'traffic:create',
  TRAFFIC_READ: 'traffic:read',
  TRAFFIC_UPDATE: 'traffic:update',
  TRAFFIC_DELETE: 'traffic:delete',
  
  // Plate Detection
  PLATE_CREATE: 'plate:create',
  PLATE_READ: 'plate:read',
  PLATE_UPDATE: 'plate:update',
  PLATE_DELETE: 'plate:delete',
  
  // Users Management
  USER_CREATE: 'user:create',
  USER_READ: 'user:read',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  
  // System
  SYSTEM_ADMIN: 'system:admin',
  SETTINGS_MANAGE: 'settings:manage',
  NOTIFICATIONS_MANAGE: 'notifications:manage'
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