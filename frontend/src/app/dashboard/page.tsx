'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { ProtectedRoute } from '@/components/common';
import { getUserBookings, Booking } from '@/lib/bookings';
import { Calendar, CheckCircle, CreditCard, Search, ClipboardList, User } from 'lucide-react';

export default function CustomerDashboard() {
    const router = useRouter();
    const { user, logout } = useAuthStore();
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setIsLoading(true);
        try {
            const data = await getUserBookings();
            setBookings(data);
        } catch (err) {
            console.error('Error loading dashboard data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
    };

    // Calculate stats
    const now = new Date();
    const upcomingBookings = bookings.filter(
        (b) => new Date(b.startTime) >= now && b.status !== 'cancelled'
    );
    const completedBookings = bookings.filter((b) => b.status === 'completed');
    const nextBooking = upcomingBookings.sort(
        (a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
    )[0];

    // Calculate total spent
    const totalSpent = completedBookings.reduce((sum, b) => sum + (b.totalPrice || 0), 0);

    return (
        <ProtectedRoute allowedRoles={['customer']}>
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
                                    href="/bookings"
                                    className="text-gray-400 hover:text-white font-light transition-colors"
                                >
                                    My Bookings
                                </Link>
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

                <div className="pt-28 pb-16 max-w-6xl mx-auto px-6 lg:px-8">
                    {/* Welcome Header */}
                    <div className="mb-10">
                        <p className="text-[#d4af37] text-sm font-light tracking-wide mb-2">
                            Welcome back,
                        </p>
                        <h1 className="text-4xl font-light text-white">
                            {user?.first_name} {user?.last_name}
                        </h1>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                        {/* Upcoming */}
                        <div className="bg-gradient-to-br from-[#1a1a2e] to-[#16213e] border border-white/5 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                    <Calendar className="w-5 h-5 text-[#d4af37]" />
                                </div>
                                <span className="text-gray-400 font-light text-sm">Upcoming</span>
                            </div>
                            <p className="text-3xl font-light text-white">{upcomingBookings.length}</p>
                            <p className="text-gray-500 text-sm mt-1">appointments</p>
                        </div>

                        {/* Completed */}
                        <div className="bg-gradient-to-br from-[#1a1a2e] to-[#16213e] border border-white/5 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                </div>
                                <span className="text-gray-400 font-light text-sm">Completed</span>
                            </div>
                            <p className="text-3xl font-light text-white">{completedBookings.length}</p>
                            <p className="text-gray-500 text-sm mt-1">appointments</p>
                        </div>

                        {/* Total Spent */}
                        <div className="bg-gradient-to-br from-[#1a1a2e] to-[#16213e] border border-white/5 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                                    <CreditCard className="w-5 h-5 text-purple-400" />
                                </div>
                                <span className="text-gray-400 font-light text-sm">Total Spent</span>
                            </div>
                            <p className="text-3xl font-light text-white">{totalSpent} kr</p>
                            <p className="text-gray-500 text-sm mt-1">all time</p>
                        </div>
                    </div>

                    {/* Main Content Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Next Appointment */}
                        <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-2xl p-6">
                            <h2 className="text-xl font-light text-white mb-6">Next Appointment</h2>

                            {isLoading ? (
                                <div className="flex items-center justify-center py-10">
                                    <div className="w-6 h-6 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
                                </div>
                            ) : nextBooking ? (
                                <div className="flex gap-4">
                                    {/* Date Box */}
                                    <div className="flex-shrink-0 w-20 h-20 bg-gradient-to-br from-[#d4af37] to-[#b8960f] rounded-xl flex flex-col items-center justify-center">
                                        <span className="text-[#0f0f1a] text-xs font-light uppercase">
                                            {new Date(nextBooking.startTime).toLocaleDateString('en-US', { month: 'short' })}
                                        </span>
                                        <span className="text-[#0f0f1a] text-2xl font-medium">
                                            {new Date(nextBooking.startTime).getDate()}
                                        </span>
                                    </div>

                                    <div className="flex-1">
                                        <h3 className="text-white font-light mb-1">
                                            {nextBooking.serviceName || 'Service'}
                                        </h3>
                                        <p className="text-gray-500 text-sm mb-2">
                                            {nextBooking.businessName} • {nextBooking.locationName}
                                        </p>
                                        <p className="text-[#d4af37] text-sm">
                                            {new Date(nextBooking.startTime).toLocaleTimeString('en-US', {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-10">
                                    <p className="text-gray-500 mb-4">No upcoming appointments</p>
                                    <Link
                                        href="/browse"
                                        className="text-[#d4af37] hover:underline text-sm"
                                    >
                                        Book your first appointment
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-2xl p-6">
                            <h2 className="text-xl font-light text-white mb-6">Quick Actions</h2>

                            <div className="space-y-3">
                                <Link
                                    href="/browse"
                                    className="flex items-center gap-4 p-4 rounded-xl bg-[#16213e]/50 hover:bg-[#16213e] border border-white/5 hover:border-[#d4af37]/30 transition-all group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                        <Search className="w-5 h-5 text-[#d4af37]" />
                                    </div>
                                    <div>
                                        <p className="text-white font-light group-hover:text-[#d4af37] transition-colors">
                                            Discover Services
                                        </p>
                                        <p className="text-gray-500 text-xs">Find and book new appointments</p>
                                    </div>
                                </Link>

                                <Link
                                    href="/bookings"
                                    className="flex items-center gap-4 p-4 rounded-xl bg-[#16213e]/50 hover:bg-[#16213e] border border-white/5 hover:border-[#d4af37]/30 transition-all group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                        <ClipboardList className="w-5 h-5 text-[#d4af37]" />
                                    </div>
                                    <div>
                                        <p className="text-white font-light group-hover:text-[#d4af37] transition-colors">
                                            View All Bookings
                                        </p>
                                        <p className="text-gray-500 text-xs">See your complete booking history</p>
                                    </div>
                                </Link>

                                <Link
                                    href="/profile"
                                    className="flex items-center gap-4 p-4 rounded-xl bg-[#16213e]/50 hover:bg-[#16213e] border border-white/5 hover:border-[#d4af37]/30 transition-all group"
                                >
                                    <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                        <User className="w-5 h-5 text-[#d4af37]" />
                                    </div>
                                    <div>
                                        <p className="text-white font-light group-hover:text-[#d4af37] transition-colors">
                                            Edit Profile
                                        </p>
                                        <p className="text-gray-500 text-xs">Update your personal information</p>
                                    </div>
                                </Link>
                            </div>
                        </div>
                    </div>

                    {/* Recent Bookings */}
                    {upcomingBookings.length > 1 && (
                        <div className="mt-8">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-light text-white">Upcoming Appointments</h2>
                                <Link href="/bookings" className="text-[#d4af37] text-sm hover:underline">
                                    View all
                                </Link>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {upcomingBookings.slice(0, 3).map((booking) => (
                                    <div
                                        key={booking.id}
                                        className="bg-[#1a1a2e]/50 border border-white/5 rounded-xl p-4 hover:border-[#d4af37]/20 transition-all"
                                    >
                                        <p className="text-white font-light mb-1">{booking.serviceName || 'Service'}</p>
                                        <p className="text-gray-500 text-sm mb-2">{booking.businessName}</p>
                                        <p className="text-[#d4af37] text-sm">
                                            {new Date(booking.startTime).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
