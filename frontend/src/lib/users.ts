import api from './api';

export interface UpdateProfileData {
    firstName?: string;
    lastName?: string;
    phoneNumber?: string;
}

export interface ChangePasswordData {
    currentPassword: string;
    newPassword: string;
}

// Update user profile
export async function updateProfile(data: UpdateProfileData) {
    const response = await api.put('/users/me', {
        first_name: data.firstName,
        last_name: data.lastName,
        phone_number: data.phoneNumber,
    });
    return response.data;
}

// Change password
export async function changePassword(data: ChangePasswordData) {
    const response = await api.patch('/users/me/password', {
        current_password: data.currentPassword,
        new_password: data.newPassword,
    });
    return response.data;
}
// Address interfaces
export interface Address {
    id: string;
    street_address: string;
    postal_code: string;
    city: string;
    country: string;
    is_default: boolean;
}

export interface CreateAddressData {
    street_address: string;
    postal_code: string;
    city: string;
    country?: string;
    is_default?: boolean;
}

export interface UpdateAddressData {
    street_address?: string;
    postal_code?: string;
    city?: string;
    country?: string;
    is_default?: boolean;
}

// ... existing code ...

// Get user addresses
export async function getAddresses(): Promise<Address[]> {
    const response = await api.get('/users/me/addresses');
    return response.data;
}

// Create address
export async function createAddress(data: CreateAddressData): Promise<Address> {
    const response = await api.post('/users/me/addresses', data);
    return response.data;
}

// Update address
export async function updateAddress(addressId: string, data: UpdateAddressData): Promise<Address> {
    const response = await api.put(`/users/me/addresses/${addressId}`, data);
    return response.data;
}

// Delete address
export async function deleteAddress(addressId: string): Promise<void> {
    await api.delete(`/users/me/addresses/${addressId}`);
}

// Delete user account
export async function deleteUser(): Promise<void> {
    await api.delete('/users/me');
}
