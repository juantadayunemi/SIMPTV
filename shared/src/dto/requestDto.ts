/**
 * DTOs de Request Legacy
 * DEPRECATED: Usar los nuevos archivos trafficDto.ts, plateDto.ts y commonDto.ts
 * Este archivo se mantiene temporalmente para compatibilidad
 */

// ============= DEPRECATED - Usar commonDto.ts =============

/**
 * @deprecated Usar LoginRequestDTO de commonDto.ts
 */
export interface LoginRequestDto {
  email: string;
  password: string;
  rememberMe?: boolean;
}

/**
 * @deprecated Usar RefreshTokenRequestDTO de commonDto.ts
 */
export interface RefreshTokenRequestDto {
  refreshToken: string;
}

/**
 * @deprecated Usar ChangePasswordRequestDTO de commonDto.ts
 */
export interface ChangePasswordRequestDto {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

/**
 * @deprecated Usar UserSearchQueryDTO de commonDto.ts
 */
export interface UserQueryDto {
  search?: string;
  role?: string;
  isActive?: boolean;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * @deprecated Usar ApiErrorDTO de commonDto.ts
 */
export interface APIError {
  code: string;
  message: string;
  details?: any;
  field?: string;
}

/**
 * @deprecated Usar WebSocketMessageDTO de commonDto.ts
 */
export interface WebSocketMessage<T = any> {
  type: string;
  payload: T;
  timestamp: Date;
}

/**
 * @deprecated Usar BaseQueryDTO de commonDto.ts
 */
export interface BaseQuery {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  search?: string;
}

// ============= DEPRECATED - Usar trafficDto.ts =============

/**
 * @deprecated Usar CreateTrafficAnalysisRequestDTO de trafficDto.ts
 */
export interface CreateTrafficAnalysisDto {
  location: string;
  startTime?: Date;
  endTime?: Date;
  weatherConditions?: string;
  notes?: string;
}

/**
 * @deprecated Usar TrafficSearchQueryDTO de trafficDto.ts
 */
export interface TrafficQueryDto {
  location?: string;
  startDate?: Date;
  endDate?: Date;
  status?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ============= DEPRECATED - Usar plateDto.ts =============

/**
 * @deprecated Usar PlateSearchQueryDTO de plateDto.ts
 */
export interface PlateQueryDto {
  plateNumber?: string;
  location?: string;
  minConfidence?: number;
  startDate?: Date;
  endDate?: Date;
  vehicleType?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

