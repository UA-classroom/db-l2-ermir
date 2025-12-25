// Common types used across the application

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    limit: number;
    pages: number;
}

export interface ApiError {
    detail: string;
    status_code?: number;
}

// Re-export types from store
export type { User, UserRole } from './store';
