import api from './api';
import { Product, ProductCreate, ProductUpdate } from './types/product';

export const getProducts = async (locationId?: string, businessId?: string) => {
    // If locationId is 'all', we might filter by business_id instead
    const params = new URLSearchParams();

    if (locationId && locationId !== 'all') {
        params.append('location_id', locationId);
    } else if (businessId) {
        params.append('business_id', businessId);
    }

    const response = await api.get(`/products?${params.toString()}`);
    return response.data;
};

export const createProduct = async (data: ProductCreate) => {
    const response = await api.post('/products', data);
    return response.data;
};

export const updateProduct = async (id: string, data: ProductUpdate) => {
    const response = await api.put(`/products/${id}`, data);
    return response.data;
};

export const deleteProduct = async (id: string) => {
    // Assuming DELETE endpoint exists or will exist. 
    // If not implemented in backend yet, this will 404/405, but good to have prepared.
    const response = await api.delete(`/products/${id}`);
    return response.data;
};
