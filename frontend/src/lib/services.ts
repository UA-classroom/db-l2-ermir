import api from './api';

export interface ServiceVariant {
    id: string;
    service_id: string;
    name: string;
    price: number;
    duration_minutes: number;
    is_active: boolean;
}

export interface Category {
    id: number;
    name: string;
    slug: string;
    parent_id?: number | null;
}

export interface Service {
    id: string;
    business_id: string;
    category_id: number | null;
    name: string;
    description: string | null;
    is_active: boolean;
    variants: ServiceVariant[];
}

export interface CreateServiceData {
    business_id: string;
    category_id?: number | null;
    name: string;
    description?: string;
    is_active?: boolean;
}

export interface UpdateServiceData {
    name?: string;
    description?: string;
    category_id?: number | null;
    is_active?: boolean;
}

export interface CreateVariantData {
    service_id: string;
    name: string;
    price: number;
    duration_minutes: number;
}

export interface UpdateVariantData {
    name?: string;
    price?: number;
    duration_minutes?: number;
}

// Get all services (can filter by business)
export async function getServices(businessId?: string): Promise<Service[]> {
    const params = businessId ? { business_id: businessId } : {};
    const response = await api.get<Service[]>('/services', { params });
    return response.data;
}

// Get categories
export async function getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/services/categories');
    return response.data;
}

// Create a new service
export async function createService(data: CreateServiceData): Promise<Service> {
    const response = await api.post<Service>('/services', data);
    return response.data;
}

// Update a service
export async function updateService(id: string, data: UpdateServiceData): Promise<Service> {
    const response = await api.put<Service>(`/services/${id}`, data);
    return response.data;
}

// Create a service variant
export async function createServiceVariant(data: CreateVariantData): Promise<ServiceVariant> {
    const response = await api.post<ServiceVariant>('/services/service-variants', data);
    return response.data;
}

// Update a service variant
export async function updateServiceVariant(id: string, data: UpdateVariantData): Promise<ServiceVariant> {
    const response = await api.put<ServiceVariant>(`/services/service-variants/${id}`, data);
    return response.data;
}

// Delete a service variant
export async function deleteServiceVariant(id: string): Promise<void> {
    await api.delete(`/services/service-variants/${id}`);
}
