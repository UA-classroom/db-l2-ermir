import api from './api';
import { LocationSearchResult, Business, Category } from './types/business';

// Get locations with search/filter
export async function getLocations(params?: {
    query?: string;
    city?: string;
    category?: string;
    limit?: number;
    offset?: number;
}): Promise<LocationSearchResult[]> {
    const response = await api.get('/businesses/locations', { params });
    return response.data;
}

// Get all businesses
export async function getBusinesses(params?: {
    city?: string;
    name?: string;
    category?: string;
    minRating?: number;
    limit?: number;
    offset?: number;
}): Promise<Business[]> {
    const response = await api.get('/businesses', { params });
    return response.data;
}

// Get single business by ID or slug
export async function getBusiness(idOrSlug: string): Promise<Business> {
    const response = await api.get(`/businesses/${idOrSlug}`);
    return response.data;
}

// Get business with locations
export async function getBusinessWithLocations(businessId: string) {
    const response = await api.get(`/businesses/${businessId}/details`);
    return response.data;
}

// Get location images
export async function getLocationImages(locationId: string) {
    const response = await api.get(`/businesses/locations/${locationId}/images`);
    return response.data;
}

// Get single location details
export async function getLocation(locationId: string): Promise<LocationSearchResult> {
    const response = await api.get(`/businesses/locations/${locationId}`);
    return response.data;
}

// Get location services (via business)
export async function getLocationServices(businessId: string) {
    const response = await api.get(`/businesses/${businessId}/services?include_variants=true`);
    return response.data;
}

// Get categories
export async function getCategories(): Promise<Category[]> {
    const response = await api.get('/services/categories');
    return response.data;
}

// Get location contacts
export async function getLocationContacts(locationId: string) {
    const response = await api.get(`/businesses/locations/${locationId}/contacts`);
    return response.data;
}
