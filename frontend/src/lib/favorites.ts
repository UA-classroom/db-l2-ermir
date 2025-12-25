import api from './api';

export interface FavoriteResponse {
    id: string;
    userId: string;
    locationId: string;
    createdAt: string;
}

// Get user's favorite locations
export async function getFavorites(): Promise<FavoriteResponse[]> {
    const response = await api.get('/reviews/users/me/favorites');
    return response.data;
}

// Add location to favorites
export async function addFavorite(locationId: string): Promise<FavoriteResponse> {
    const response = await api.post('/reviews/users/me/favorites', {
        location_id: locationId,
    });
    return response.data;
}

// Remove location from favorites
export async function removeFavorite(locationId: string): Promise<void> {
    await api.delete(`/reviews/users/me/favorites/${locationId}`);
}
