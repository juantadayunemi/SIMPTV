// API Response Types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: APIError;
  timestamp: Date;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  data: T[];
  pagination: PaginationInfo;
  message?: string;
  error?: APIError;
  timestamp: Date;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
}

export interface APIError {
  code: string;
  message: string;
  details?: any;
  field?: string;
}

export interface WebSocketMessage<T = any> {
  type: string;
  payload: T;
  timestamp: Date;
}

// Common query parameters
export interface BaseQuery {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  search?: string;
}

