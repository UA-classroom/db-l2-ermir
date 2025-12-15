'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { ProtectedRoute } from '@/components/common';
import { getUserBookings, cancelBooking, Booking } from '@/lib/bookings';
import { Calendar, History } from 'lucide-react';

export default function BookingsPage() {
    const router = useRouter();
    const { user, logout } = useAuthStore();
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');

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

    // Split bookings into upcoming and past
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
            <div className="min-h-screen bg-[#0f0f1a]">
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
            </div>
        </ProtectedRoute>
    );
}

// Booking Card Component
function BookingCard({
    booking,
    onCancel,
    isPast,
}: {
    booking: Booking;
    onCancel: (id: string) => void;
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
                            {booking.business_name || 'Business'} • {booking.location_name || 'Location'}
                        </p>
                        <p className="text-gray-400 text-sm">
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

                    {/* Cancel Button (only for upcoming, non-cancelled) */}
                    {!isPast && booking.status !== 'cancelled' && (
                        <button
                            onClick={() => onCancel(booking.id)}
                            className="text-gray-400 hover:text-red-400 text-sm font-light transition-colors"
                        >
                            Cancel
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
