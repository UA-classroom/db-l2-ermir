import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// API base URL - adjust for production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // Only access localStorage in browser environment
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('access_token');
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// Response interceptor - handle errors
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        // Handle 401 - unauthorized (token expired)
        if (error.response?.status === 401) {
            // TODO: Implement token refresh or redirect to login
            if (typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                // Optionally redirect to login
                // window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;

// Export typed API methods for convenience
export const apiClient = {
    get: <T>(url: string, params?: object) =>
        api.get<T>(url, { params }).then(res => res.data),

    post: <T>(url: string, data?: object) =>
        api.post<T>(url, data).then(res => res.data),

    put: <T>(url: string, data?: object) =>
        api.put<T>(url, data).then(res => res.data),

    patch: <T>(url: string, data?: object) =>
        api.patch<T>(url, data).then(res => res.data),

    delete: <T>(url: string) =>
        api.delete<T>(url).then(res => res.data),
};
