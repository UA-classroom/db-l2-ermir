import api from './api';

export interface Review {
    id: string;
    bookingId?: string;
    booking_id?: string; // Backend snake_case
    rating: number;
    comment?: string;
    createdAt?: string;
    created_at?: string; // Backend snake_case
    // User info from backend
    user_id?: string;
    user_name?: string; // Backend: "First Last"
    user_email?: string;
}

export interface CreateReviewData {
    bookingId: string;
    rating: number;
    comment?: string;
}

// Get reviews for a business/location
export async function getBusinessReviews(locationId: string): Promise<Review[]> {
    const response = await api.get(`/reviews/businesses/${locationId}/reviews`);
    return response.data;
}

// Create a review for a completed booking
export async function createReview(data: CreateReviewData): Promise<Review> {
    const response = await api.post('/reviews', {
        booking_id: data.bookingId,
        rating: data.rating,
        comment: data.comment,
    });
    return response.data;
}
