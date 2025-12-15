'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { ProtectedRoute } from '@/components/common';
import { getUserBookings, cancelBooking, rescheduleBooking, getAvailableSlots, Booking, TimeSlot } from '@/lib/bookings';
import { createReview } from '@/lib/reviews';
import { Calendar, History, Clock, X, Star } from 'lucide-react';

export default function BookingsPage() {
    const router = useRouter();
    const { logout } = useAuthStore();
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');

    // Reschedule State
    const [reschedulingBooking, setReschedulingBooking] = useState<Booking | null>(null);
    const [newDate, setNewDate] = useState('');
    const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
    const [selectedNewSlot, setSelectedNewSlot] = useState<TimeSlot | null>(null);
    const [isRescheduling, setIsRescheduling] = useState(false);
    const [isLoadingSlots, setIsLoadingSlots] = useState(false);

    // Review State
    const [reviewingBooking, setReviewingBooking] = useState<Booking | null>(null);

    useEffect(() => {
        loadBookings();
    }, []);

    const loadBookings = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getUserBookings();
            setBookings(data);
        } catch (err: any) {
            console.error('Error loading bookings:', err);
            setError('Failed to load bookings');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = async (bookingId: string) => {
        if (!confirm('Are you sure you want to cancel this booking?')) return;
        try {
            await cancelBooking(bookingId);
            loadBookings(); // Refresh
        } catch (err) {
            console.error('Error cancelling booking:', err);
            alert('Failed to cancel booking');
        }
    };

    const handleLogout = () => {
        logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
    };

    // --- Reschedule Logic ---

    const handleOpenReschedule = (booking: Booking) => {
        setReschedulingBooking(booking);
        // Default to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        setNewDate(tomorrow.toISOString().split('T')[0]);
        setSelectedNewSlot(null);
        setAvailableSlots([]);
    };

    const handleCloseReschedule = () => {
        setReschedulingBooking(null);
        setSelectedNewSlot(null);
        setAvailableSlots([]);
    };

    useEffect(() => {
        if (reschedulingBooking && newDate) {
            loadRescheduleSlots();
        }
    }, [reschedulingBooking, newDate]);

    const loadRescheduleSlots = async () => {
        if (!reschedulingBooking || !newDate) return;
        setIsLoadingSlots(true);
        try {
            const slots = await getAvailableSlots(
                newDate,
                reschedulingBooking.service_variant_id,
                reschedulingBooking.location_id,
                reschedulingBooking.employee_id
            );
            setAvailableSlots(slots);
        } catch (err) {
            console.error('Error loading slots:', err);
            setAvailableSlots([]);
        } finally {
            setIsLoadingSlots(false);
        }
    };

    const handleConfirmReschedule = async () => {
        if (!reschedulingBooking || !selectedNewSlot) return;

        // Use start_time (snake_case from API) or startTime (camelCase from frontend type)
        const slotStart = selectedNewSlot.start_time || selectedNewSlot.startTime;

        if (!slotStart) {
            alert('Invalid slot selected');
            return;
        }

        // Calculate original duration
        const originalStart = new Date(reschedulingBooking.start_time).getTime();
        const originalEnd = new Date(reschedulingBooking.end_time).getTime();
        const durationMs = originalEnd - originalStart;

        const newStartTime = new Date(slotStart);
        const newEndTime = new Date(newStartTime.getTime() + durationMs);

        setIsRescheduling(true);
        try {
            await rescheduleBooking(reschedulingBooking.id, {
                startTime: newStartTime.toISOString(),
                endTime: newEndTime.toISOString(),
            });

            // Success
            handleCloseReschedule();
            loadBookings();
            alert('Booking rescheduled successfully!');
        } catch (err) {
            console.error('Error rescheduling:', err);
            alert('Failed to reschedule. Please try another time.');
        } finally {
            setIsRescheduling(false);
        }
    };

    // --- Review Logic ---

    const handleOpenReview = (booking: Booking) => {
        setReviewingBooking(booking);
    };

    const handleCloseReview = () => {
        setReviewingBooking(null);
    };

    const handleSubmitReview = async (data: { rating: number; comment: string }) => {
        if (!reviewingBooking) return;
        try {
            await createReview({
                bookingId: reviewingBooking.id,
                rating: data.rating,
                comment: data.comment
            });
            alert('Review submitted successfully!');
            handleCloseReview();
        } catch (err: any) {
            console.error('Error submitting review:', err);
            if (err.response?.status === 409 || err.response?.data?.detail?.includes('already reviewed')) {
                alert('You have already reviewed this booking.');
            } else {
                alert('Failed to submit review. Please try again.');
            }
        }
    };

    // --- Filtering ---

    const now = new Date();
    const upcomingBookings = bookings.filter(
        (b) => new Date(b.start_time) >= now && b.status !== 'cancelled'
    );
    const pastBookings = bookings.filter(
        (b) => new Date(b.start_time) < now || b.status === 'cancelled'
    );

    const displayBookings = activeTab === 'upcoming' ? upcomingBookings : pastBookings;

    return (
        <ProtectedRoute allowedRoles={['customer', 'provider', 'admin']}>
            <div className="min-h-screen bg-[#0f0f1a] relative">
                {/* Navigation */}
                <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0f0f1a]/80 backdrop-blur-lg border-b border-white/10">
                    <div className="max-w-7xl mx-auto px-6 lg:px-8">
                        <div className="flex justify-between h-20 items-center">
                            <Link href="/" className="flex items-center gap-2">
                                <span className="text-2xl font-light tracking-wider text-white">
                                    Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
                                </span>
                            </Link>
                            <div className="flex items-center gap-6">
                                <Link
                                    href="/profile"
                                    className="text-gray-400 hover:text-white font-light transition-colors"
                                >
                                    Profile
                                </Link>
                                <button
                                    onClick={handleLogout}
                                    className="text-gray-400 hover:text-red-400 font-light transition-colors"
                                >
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    </div>
                </nav>

                <div className="pt-28 pb-16 max-w-4xl mx-auto px-6 lg:px-8">
                    {/* Header */}
                    <div className="flex justify-between items-center mb-8">
                        <div>
                            <h1 className="text-3xl font-light text-white mb-2">My Bookings</h1>
                            <p className="text-gray-400 font-light">
                                {upcomingBookings.length} upcoming appointment{upcomingBookings.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                        <Link
                            href="/browse"
                            className="px-6 py-3 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                        >
                            Book New
                        </Link>
                    </div>

                    {/* Tabs */}
                    <div className="flex gap-1 p-1 bg-[#1a1a2e]/50 rounded-lg mb-8 w-fit">
                        <button
                            onClick={() => setActiveTab('upcoming')}
                            className={`px-6 py-2 rounded-md font-light transition-all ${activeTab === 'upcoming'
                                ? 'bg-[#d4af37] text-[#0f0f1a]'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Upcoming ({upcomingBookings.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('past')}
                            className={`px-6 py-2 rounded-md font-light transition-all ${activeTab === 'past'
                                ? 'bg-[#d4af37] text-[#0f0f1a]'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Past ({pastBookings.length})
                        </button>
                    </div>

                    {/* Loading */}
                    {isLoading && (
                        <div className="flex items-center justify-center py-20">
                            <div className="w-8 h-8 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div className="text-center py-20">
                            <p className="text-red-400 mb-4">{error}</p>
                            <button
                                onClick={loadBookings}
                                className="text-[#d4af37] hover:underline"
                            >
                                Try again
                            </button>
                        </div>
                    )}

                    {/* Bookings List */}
                    {!isLoading && !error && displayBookings.length > 0 && (
                        <div className="space-y-4">
                            {displayBookings.map((booking) => (
                                <BookingCard
                                    key={booking.id}
                                    booking={booking}
                                    onCancel={handleCancel}
                                    onReschedule={handleOpenReschedule}
                                    onReview={handleOpenReview}
                                    isPast={activeTab === 'past'}
                                />
                            ))}
                        </div>
                    )}

                    {/* Empty State */}
                    {!isLoading && !error && displayBookings.length === 0 && (
                        <div className="text-center py-20 bg-[#1a1a2e]/30 rounded-2xl border border-white/5">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                {activeTab === 'upcoming' ? (
                                    <Calendar className="w-8 h-8 text-[#d4af37]" />
                                ) : (
                                    <History className="w-8 h-8 text-[#d4af37]" />
                                )}
                            </div>
                            <h3 className="text-xl text-white font-light mb-2">
                                {activeTab === 'upcoming' ? 'No upcoming bookings' : 'No past bookings'}
                            </h3>
                            <p className="text-gray-500 mb-6">
                                {activeTab === 'upcoming'
                                    ? "You haven't booked any appointments yet"
                                    : "Your completed bookings will appear here"}
                            </p>
                            {activeTab === 'upcoming' && (
                                <Link
                                    href="/browse"
                                    className="inline-block px-6 py-3 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                                >
                                    Discover Services
                                </Link>
                            )}
                        </div>
                    )}
                </div>

                {/* Reschedule Modal */}
                {reschedulingBooking && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 w-full max-w-lg shadow-xl">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-light text-white">Reschedule Booking</h2>
                                <button
                                    onClick={handleCloseReschedule}
                                    className="text-gray-400 hover:text-white transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="mb-6">
                                <p className="text-gray-400 text-sm mb-1">Current Appointment:</p>
                                <p className="text-white font-medium">
                                    {new Date(reschedulingBooking.start_time).toLocaleString()}
                                </p>
                            </div>

                            <div className="space-y-4 mb-8">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Select New Date</label>
                                    <input
                                        type="date"
                                        value={newDate}
                                        min={new Date().toISOString().split('T')[0]}
                                        onChange={(e) => setNewDate(e.target.value)}
                                        className="w-full px-4 py-3 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Available Slots</label>
                                    {isLoadingSlots ? (
                                        <div className="text-center py-4 bg-[#16213e] rounded-lg">
                                            <div className="w-5 h-5 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin mx-auto"></div>
                                        </div>
                                    ) : availableSlots.length === 0 ? (
                                        <div className="text-center py-4 bg-[#16213e] rounded-lg border border-white/5">
                                            <p className="text-gray-500 text-sm">No slots available for this date</p>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
                                            {availableSlots.map((slot, index) => (
                                                <button
                                                    key={index}
                                                    onClick={() => setSelectedNewSlot(slot)}
                                                    className={`px-3 py-2 text-sm rounded-lg border transition-all ${selectedNewSlot === slot
                                                        ? 'bg-[#d4af37] text-[#0f0f1a] border-[#d4af37]'
                                                        : 'bg-[#16213e] text-gray-300 border-white/5 hover:border-[#d4af37]/50'
                                                        }`}
                                                >
                                                    {new Date(slot.start_time || slot.startTime!).toLocaleTimeString([], {
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                    })}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={handleCloseReschedule}
                                    className="flex-1 px-4 py-3 bg-[#16213e] text-white rounded-lg hover:bg-[#16213e]/80 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleConfirmReschedule}
                                    disabled={!selectedNewSlot || isRescheduling}
                                    className={`flex-1 px-4 py-3 font-medium rounded-lg transition-all ${!selectedNewSlot || isRescheduling
                                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] hover:shadow-lg'
                                        }`}
                                >
                                    {isRescheduling ? 'Updating...' : 'Confirm New Time'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Review Modal */}
                {reviewingBooking && (
                    <ReviewModal
                        booking={reviewingBooking}
                        onClose={handleCloseReview}
                        onSubmit={handleSubmitReview}
                    />
                )}
            </div>
        </ProtectedRoute>
    );
}

// Review Modal Component
function ReviewModal({
    booking,
    onClose,
    onSubmit
}: {
    booking: Booking;
    onClose: () => void;
    onSubmit: (data: { rating: number; comment: string }) => Promise<void>;
}) {
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async () => {
        setIsSubmitting(true);
        await onSubmit({ rating, comment });
        setIsSubmitting(false);
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 w-full max-w-lg shadow-xl">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-light text-white">Write a Review</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="mb-6 text-center">
                    <p className="text-gray-400 mb-2">How was your experience with</p>
                    <p className="text-white text-lg font-medium">{booking.service_name}</p>
                </div>

                {/* Rating Stars */}
                <div className="flex justify-center gap-3 mb-8">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <button
                            key={star}
                            onClick={() => setRating(star)}
                            className={`p-1 transition-all hover:scale-110 ${star <= rating ? 'text-[#d4af37]' : 'text-gray-600'}`}
                        >
                            <Star className="w-8 h-8 fill-current" />
                        </button>
                    ))}
                </div>

                <div className="mb-6">
                    <label className="block text-sm text-gray-400 mb-2">Comments (Optional)</label>
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        className="w-full h-32 bg-[#16213e] bg-opacity-50 border border-white/10 rounded-lg p-4 text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 resize-none"
                        placeholder="Share your experience..."
                    />
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-3 bg-[#16213e] text-white rounded-lg hover:bg-[#16213e]/80 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className="flex-1 px-4 py-3 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? 'Submitting...' : 'Submit Review'}
                    </button>
                </div>
            </div>
        </div>
    );
}

// Booking Card Component
function BookingCard({
    booking,
    onCancel,
    onReschedule,
    onReview,
    isPast,
}: {
    booking: Booking;
    onCancel: (id: string) => void;
    onReschedule?: (booking: Booking) => void;
    onReview?: (booking: Booking) => void;
    isPast: boolean;
}) {
    const startDate = new Date(booking.start_time);
    const endDate = new Date(booking.end_time);

    const statusColors: Record<string, string> = {
        pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
        confirmed: 'bg-green-500/20 text-green-400 border-green-500/30',
        completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
        cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
        no_show: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };

    const statusLabels: Record<string, string> = {
        pending: 'Pending',
        confirmed: 'Confirmed',
        completed: 'Completed',
        cancelled: 'Cancelled',
        no_show: 'No Show',
    };

    // Determine if reviewable: Completed OR (Confirmed AND Past)
    const isReviewable = isPast && booking.status !== 'cancelled' && booking.status !== 'no_show';

    return (
        <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-xl p-6 hover:border-[#d4af37]/20 transition-all">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                {/* Left: Info */}
                <div className="flex gap-4">
                    {/* Date Box */}
                    <div className="flex-shrink-0 w-16 h-16 bg-[#16213e] rounded-lg flex flex-col items-center justify-center">
                        <span className="text-[#d4af37] text-xs font-light uppercase">
                            {startDate.toLocaleDateString('en-US', { month: 'short' })}
                        </span>
                        <span className="text-white text-xl font-light">
                            {startDate.getDate()}
                        </span>
                    </div>

                    {/* Details */}
                    <div>
                        <h3 className="text-white font-light mb-1">
                            {booking.service_name || 'Service'}
                        </h3>
                        <p className="text-gray-500 text-sm mb-2">
                            {booking.business_name || 'Business'} • {booking.location_name || 'Location'} {booking.employee_name ? `• with ${booking.employee_name}` : ''}
                        </p>
                        <p className="text-gray-400 text-sm flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                            {' - '}
                            {endDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                    </div>
                </div>

                {/* Right: Status & Actions */}
                <div className="flex items-center gap-4">
                    {/* Price */}
                    <span className="text-[#d4af37] font-medium">
                        {booking.total_price} kr
                    </span>

                    {/* Status Badge */}
                    <span
                        className={`px-3 py-1 rounded-full text-xs font-light border ${statusColors[booking.status] || statusColors.pending
                            }`}
                    >
                        {statusLabels[booking.status] || booking.status}
                    </span>

                    {/* Actions */}
                    {!isPast && booking.status !== 'cancelled' && (
                        <div className="flex gap-2">
                            {onReschedule && (
                                <button
                                    onClick={() => onReschedule(booking)}
                                    className="text-gray-400 hover:text-[#d4af37] text-sm font-light transition-colors"
                                >
                                    Reschedule
                                </button>
                            )}
                            <button
                                onClick={() => onCancel(booking.id)}
                                className="text-gray-400 hover:text-red-400 text-sm font-light transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    )}

                    {/* Review Action */}
                    {isPast && isReviewable && onReview && (
                        <button
                            onClick={() => onReview(booking)}
                            className="bg-[#d4af37]/10 text-[#d4af37] px-4 py-2 rounded-lg text-sm hover:bg-[#d4af37] hover:text-[#0f0f1a] transition-all"
                        >
                            Write Review
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
