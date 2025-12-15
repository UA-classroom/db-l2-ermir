import api from './api';

export interface Booking {
    id: string;
    customer_id: string;
    location_id: string;
    employee_id: string;
    service_variant_id: string;
    status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
    start_time: string;
    end_time: string;
    total_price: number;
    customer_note?: string;
    created_at: string;

    // Expanded fields from API (if available)
    location_name?: string;
    business_name?: string;
    service_name?: string;
    employee_name?: string;
}

export interface BookingDetail extends Booking {
    customer: {
        id: string;
        firstName: string;
        lastName: string;
        email: string;
    };
    employee: {
        id: string;
        jobTitle: string;
        bio?: string;
    };
    service: {
        id: string;
        name: string;
        price: number;
        durationMinutes: number;
    };
}

export interface CreateBookingData {
    customerId: string;       // User ID
    locationId: string;
    serviceVariantId: string;
    employeeId: string;
    startTime: string;        // ISO string
    endTime: string;          // ISO string (start + duration)
    customerNote?: string;
}

export interface TimeSlot {
    // Backend sends snake_case
    start_time?: string;
    employee_ids?: string[];
    // Frontend camelCase (for compatibility)
    startTime?: string;
    availableEmployeeIds?: string[];
}

// Get user's bookings
export async function getUserBookings(status?: string): Promise<Booking[]> {
    const response = await api.get('/bookings/', {
        params: { status },
    });
    return response.data;
}

// Get single booking
export async function getBooking(bookingId: string): Promise<BookingDetail> {
    const response = await api.get(`/bookings/${bookingId}`);
    return response.data;
}

// Create new booking
export async function createBooking(data: CreateBookingData): Promise<Booking> {
    // Convert to snake_case for backend
    const response = await api.post('/bookings', {
        customer_id: data.customerId,
        location_id: data.locationId,
        employee_id: data.employeeId,
        service_variant_id: data.serviceVariantId,
        start_time: data.startTime,
        end_time: data.endTime,
        customer_note: data.customerNote,
    });
    return response.data;
}

// Cancel booking
export async function cancelBooking(bookingId: string): Promise<void> {
    await api.patch(`/bookings/${bookingId}/status`, { status: 'cancelled' });
}

// Get available time slots
export async function getAvailableSlots(
    date: string,
    serviceVariantId: string,
    locationId: string,
    employeeId?: string
): Promise<TimeSlot[]> {
    const response = await api.get('/bookings/slots', {
        params: {
            date,
            service_variant_id: serviceVariantId,
            location_id: locationId,
            employee_id: employeeId,
        },
    });
    return response.data;
}
