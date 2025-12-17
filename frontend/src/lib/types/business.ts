// API types for businesses and locations

export interface Business {
    id: string;
    name: string;
    slug: string;
    orgNumber?: string;
    ownerId: string;
    createdAt: string;
    averageRating?: number;
    reviewCount: number;
    primaryCategory?: string;
}

export interface Location {
    id: string;
    businessId: string;
    name: string;
    address: string;
    city: string;
    postalCode: string;
    latitude?: number;
    longitude?: number;
}

export interface LocationSearchResult extends Location {
    businessName: string;
    primaryCategory?: string;
    averageRating: number;
    reviewCount: number;
    primaryImage?: string;
}

export interface LocationImage {
    id: string;
    locationId: string;
    url: string;
    altText?: string;
    displayOrder: number;
    isPrimary: boolean;
}

export interface Service {
    id: string;
    businessId: string;
    categoryId: number;
    name: string;
    description?: string;
    isActive: boolean;
    variants?: ServiceVariant[];
}

export interface ServiceVariant {
    id: string;
    serviceId?: string;
    service_id?: string; // Backend snake_case
    name: string;
    price: number;
    durationMinutes?: number;
    duration_minutes?: number; // Backend snake_case
}

export interface Category {
    id: number;
    parentId?: number;
    name: string;
    slug: string;
}

export interface Contact {
    id: number;
    locationId: string;
    contactType: string;
    phoneNumber: string;
    createdAt?: string;
}
