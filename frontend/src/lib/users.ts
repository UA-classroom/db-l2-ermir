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
