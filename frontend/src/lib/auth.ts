import api from './api';

// Types
export interface LoginCredentials {
    email: string;
    password: string;
}

export interface CustomerRegisterData {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
}

export interface ProviderRegisterData extends CustomerRegisterData {
    // Provider has same fields, registered with different endpoint
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface UserResponse {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: 'customer' | 'provider' | 'admin';
    phone_number?: string;
    mobile_number?: string; // Backend snake_case field
    mobileNumber?: string; // Just in case camelCase
    is_active: boolean;
}

// Auth API functions
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
    // Use native fetch to avoid axios Content-Type issues with form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw { response: { data: error, status: response.status } };
    }

    return response.json();
}

export async function registerCustomer(data: CustomerRegisterData): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/register/customer', data);
    return response.data;
}

export async function registerProvider(data: ProviderRegisterData): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/register/provider', data);
    return response.data;
}

export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
        refresh_token: refreshToken,
    });
    return response.data;
}

export async function logout(): Promise<void> {
    await api.post('/auth/logout');
}

export async function getCurrentUser(): Promise<UserResponse> {
    const response = await api.get<UserResponse>('/users/me');
    return response.data;
}
