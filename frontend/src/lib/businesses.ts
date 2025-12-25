import api from './api';
import { LocationSearchResult, Business, Category } from './types/business';

// Interfaces for CRUD operations
export interface UpdateBusinessData {
    name?: string;
    org_number?: string;
    slug?: string;
}

export interface CreateLocationData {
    business_id?: string;
    name?: string;
    address?: string;
    city?: string;
    postal_code?: string;
    latitude?: number;
    longitude?: number;
}

export interface UpdateLocationData {
    name?: string;
    address?: string;
    city?: string;
    postal_code?: string;
    latitude?: number;
    longitude?: number;
}

export interface CreateContactData {
    location_id?: string;
    contact_type: string;
    phone_number: string;
}

export interface UpdateContactData {
    contact_type?: string;
    phone_number?: string;
}

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
    ownerId?: string;
    limit?: number;
    offset?: number;
}): Promise<Business[]> {
    const response = await api.get('/businesses', {
        params: {
            ...params,
            owner_id: params?.ownerId,
        }
    });
    return response.data;
}

// Get single business by ID or slug
export async function getBusiness(idOrSlug: string): Promise<Business> {
    const response = await api.get(`/businesses/${idOrSlug}`);
    return response.data;
}

// Get business with locations
export async function getBusinessWithLocations(businessId: string) {
    const [business, locations] = await Promise.all([
        api.get(`/businesses/${businessId}`),
        api.get(`/businesses/${businessId}/locations`)
    ]);

    return {
        ...business.data,
        locations: locations.data
    };
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

// Update Business
export async function updateBusiness(businessId: string, data: UpdateBusinessData) {
    const response = await api.put(`/businesses/${businessId}`, data);
    return response.data;
}

// Create Location
export async function createLocation(businessId: string, data: CreateLocationData) {
    const response = await api.post(`/businesses/${businessId}/locations`, data);
    return response.data;
}

// Update Location
export async function updateLocation(locationId: string, data: UpdateLocationData) {
    const response = await api.put(`/businesses/locations/${locationId}`, data);
    return response.data;
}

// Create Location Contact
export async function createLocationContact(locationId: string, data: CreateContactData) {
    const response = await api.post(`/businesses/locations/${locationId}/contacts`, data);
    return response.data;
}

// Update Location Contact
export async function updateLocationContact(contactId: number, data: UpdateContactData) {
    const response = await api.put(`/businesses/location-contacts/${contactId}`, data);
    return response.data;
}

// Delete Location Contact
export async function deleteLocationContact(contactId: number) {
    await api.delete(`/businesses/location-contacts/${contactId}`);
}
