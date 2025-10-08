/**
 * Entidades de Usuario y Roles
 * Modelos para autenticación, usuarios y sistema de roles
 * shared/src/entities/authEntities.ts
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

// ============= USER ENTITIES =============

export interface UserEntity {
  id: string;
  email: string;
  passwordHash: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  isActive: boolean;
  emailConfirmed: boolean;
  lastLogin?: Date;
  failedLoginAttempts?: number;
  isLockedOut?: boolean;
  lockoutUntil?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserRoleEntity {
  id: string;
  userId: string;
  role: UserRoleType;
  assignedBy?: string;
  assignedAt: Date;
  isActive: boolean;
}

export interface  CustomerEntity {
  id: string;
  name: string;
}