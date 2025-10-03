/**
 * Entidades de Usuario y Roles
 * Modelos para autenticación, usuarios y sistema de roles
 * shared/src/entities/authEntities.ts
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