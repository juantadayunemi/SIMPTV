/**
 * Entidades de Usuario y Roles
 * Modelos para autenticación, usuarios y sistema de roles
 * shared/src/entities/authEntities.ts
 * 
 * ANOTACIONES PARA GENERADOR DJANGO (SQL Server):
 * 
 * @db:primary - Campo primary key
 * @db:identity - IDENTITY(1,1) autoincremental en SQL Server
 * @db:unique - Restricción UNIQUE en SQL Server
 * @db:foreignKey ModelName - Foreign Key a otro modelo (on_delete=CASCADE)
 * @db:varchar(n) - VARCHAR(n) en SQL Server
 * @db:int - INT en SQL Server (default para number)
 * @db:bigint - BIGINT en SQL Server
 * @db:datetime - DATETIME2 en SQL Server
 * @db:text - TEXT/NVARCHAR(MAX)
 * @default(value) - Valor por defecto (ej: @default(false), @default(0))
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
 * - Frontend: firstName, isActive, createdAt
 * - Backend:  first_name, is_active, created_at
 * - API JSON: firstName, isActive, createdAt (camelCase)
 */

import { UserRoleType } from "../types/roleTypes";

// ============= USER ENTITY =============

export interface UserEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental (BigAutoField en Django)
  email: string; // @db:varchar(255) @db:unique - Email único para login (USERNAME_FIELD en Django)
  passwordHash: string; // @db:varchar(255) - Hash bcrypt de la contraseña
  firstName: string; // @db:varchar(255) - Nombre del usuario
  lastName: string; // @db:varchar(255) - Apellido del usuario
  phoneNumber?: string; // @db:varchar(255) - Número de teléfono (opcional)
  profileImage?: string; // @db:varchar(255) - URL de imagen de perfil (opcional)
  isActive: boolean; // @db:bit @default(true) - Usuario activo (is_active en Django)
  emailConfirmed: boolean; // @default(false) - Si el email ha sido confirmado
  lastLogin?: Date; // @db:datetime - Última vez que inició sesión (opcional)
  failedLoginAttempts?: number; // @db:int @default(0) - Contador de intentos fallidos (opcional)
  isLockedOut?: boolean; // @db:bit @default(false) - Si la cuenta está bloqueada por intentos (opcional)
  lockoutUntil?: Date; // @db:datetime - Fecha hasta la que está bloqueada (opcional)
  createdAt: Date; // @db:datetime - Fecha de creación (auto_now_add)
  updatedAt: Date; // @db:datetime - Fecha de última actualización (auto_now)
}

// ============= USER ROLE ENTITY =============

export interface UserRoleEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  user: number; // @db:foreignKey auth_app.User @db:bigint - Foreign Key a auth_app.User.id (CASCADE delete)
  role: UserRoleType; // @db:varchar(50) - Rol del usuario (ADMIN, OPERATOR, VIEWER)
  assignedBy?: string; // @db:varchar(255) - Usuario que asignó el rol (opcional)
  assignedAt: Date; // @db:datetime - Fecha de asignación del rol
  isActive: boolean; // @db:bit @default(true) - Si el rol está activo
  createdAt: Date; // @db:datetime - Fecha de creación (auto_now_add)
  updatedAt: Date; // @db:datetime - Fecha de última actualización (auto_now)
  
  // ÍNDICES EN TABLA:
  // - UNIQUE(user, role) - Un usuario no puede tener el mismo rol dos veces
  // - INDEX(user, isActive) - Para queries rápidas por usuario y rol activo
}

// ============= ROLE PERMISSION ENTITY =============

export interface RolePermissionEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  role: UserRoleType; // @db:varchar(50) - Rol (ADMIN, OPERATOR, VIEWER, CUSTOM)
  permission: string; // @db:varchar(100) - Permiso específico (ej: traffic:create, user:read)
  isGranted: boolean; // @db:bit @default(true) - Si el permiso está concedido o revocado
  grantedBy?: string; // @db:varchar(255) - Usuario que otorgó el permiso (opcional)
  grantedAt: Date; // @db:datetime - Fecha de otorgamiento
  expiresAt?: Date; // @db:datetime - Fecha de expiración del permiso (opcional)
  createdAt: Date; // @db:datetime - Fecha de creación (auto_now_add)
  updatedAt: Date; // @db:datetime - Fecha de última actualización (auto_now)
  
  // ÍNDICES EN TABLA:
  // - UNIQUE(role, permission) - Un rol no puede tener el mismo permiso duplicado
  // - INDEX(role, isGranted) - Para queries rápidas por rol y permisos activos
}

// ============= USER PERMISSION OVERRIDE ENTITY =============

export interface UserPermissionOverrideEntity {
  id: number; // @db:primary @db:identity @db:bigint - ID autoincremental
  user: number; // @db:foreignKey auth_app.User @db:bigint - Foreign Key a auth_app.User.id (CASCADE delete)
  permission: string; // @db:varchar(100) - Permiso específico a sobrescribir
  isGranted: boolean; // @db:bit - Si se concede (true) o se revoca (false) el permiso
  overrideReason?: string; // @db:text - Razón de la sobrescritura (opcional)
  grantedBy: string; // @db:varchar(255) - Usuario que hizo la sobrescritura
  grantedAt: Date; // @db:datetime - Fecha de sobrescritura
  expiresAt?: Date; // @db:datetime - Fecha de expiración (opcional)
  createdAt: Date; // @db:datetime - Fecha de creación (auto_now_add)
  updatedAt: Date; // @db:datetime - Fecha de última actualización (auto_now)
  
  // ÍNDICES EN TABLA:
  // - UNIQUE(user, permission) - Un usuario no puede tener el mismo permiso sobrescrito dos veces
  // - INDEX(user, isGranted) - Para queries rápidas por usuario y permisos activos
  
  // LÓGICA DE PERMISOS:
  // 1. Si existe UserPermissionOverride, se usa ese valor (isGranted)
  // 2. Si no existe override, se usan los permisos del rol (RolePermission)
  // 3. Si el rol no tiene RolePermission custom, se usan los permisos por defecto (ROLE_PERMISSIONS)
}

// ============= CUSTOMER ENTITY =============

export interface CustomerEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID único
  name: string; // @db:varchar(255) - Nombre de cliente/organización
}