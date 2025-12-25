'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { useProviderStore } from '@/lib/store/providerStore'; // Global Context
import { getLocationBookings, Booking } from '@/lib/bookings';
import { Calendar, Users, TrendingUp } from 'lucide-react';

export default function ProviderDashboard() {
    const { user } = useAuthStore();
    const { business, locations, selectedLocationId } = useProviderStore();

    const [stats, setStats] = useState({
        todayBookings: 0,
        totalBookings: 0,
        revenueMonth: 0
    });

    // Reactive Data Fetching based on Global Context
    useEffect(() => {
        const fetchStats = async () => {
            if (!business || locations.length === 0) return;

            try {
                let bookingsToProcess: Booking[] = [];

                if (selectedLocationId === 'all') {
                    // Aggregate ALL locations
                    // Parallel fetch for better performance
                    const promises = locations.map(loc => getLocationBookings(loc.id));
                    const results = await Promise.all(promises);
                    bookingsToProcess = results.flat();
                } else {
                    // Single Location
                    bookingsToProcess = await getLocationBookings(selectedLocationId);
                }

                calculateStats(bookingsToProcess);
            } catch (err) {
                console.error("Error fetching dashboard stats:", err);
            }
        };

        fetchStats();
    }, [business, locations, selectedLocationId]); // Re-run when context changes

    const calculateStats = (bookings: Booking[]) => {
        const now = new Date();
        const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

        // 1. Today's Bookings
        const todayCount = bookings.filter(b => {
            const bookingDate = new Date(b.start_time);
            return bookingDate >= startOfDay && bookingDate < new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000);
        }).length;

        // 2. Revenue (Month)
        // Calculating confirmed + completed bookings for the current month
        const monthRevenue = bookings
            .filter(b => {
                const bookingDate = new Date(b.start_time);
                return bookingDate >= startOfMonth &&
                    (b.status === 'completed' || b.status === 'confirmed');
            })
            .reduce((sum, b) => sum + Number(b.total_price), 0);

        // 3. Total Bookings (All time for selected context)
        const totalCount = bookings.length;

        setStats({
            todayBookings: todayCount,
            totalBookings: totalCount,
            revenueMonth: monthRevenue
        });
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-light text-white mb-2">
                    Welcome back, {user?.first_name}
                </h1>
                <p className="text-gray-400">
                    {business ? (
                        <span className="flex items-center gap-2">
                            Managing <span className="text-[#d4af37]">{business.name}</span>
                        </span>
                    ) : (
                        "Loading your business profile..."
                    )}
                </p>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                            <Calendar className="w-5 h-5 text-[#d4af37]" />
                        </div>
                        <span className="text-gray-400">Today's Bookings</span>
                    </div>
                    <p className="text-3xl text-white font-light">{stats.todayBookings}</p>
                </div>

                <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                            <Users className="w-5 h-5 text-blue-400" />
                        </div>
                        <span className="text-gray-400">Total Bookings</span>
                    </div>
                    <p className="text-3xl text-white font-light">{stats.totalBookings}</p>
                </div>

                <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                            <TrendingUp className="w-5 h-5 text-green-400" />
                        </div>
                        <span className="text-gray-400">Revenue (Month)</span>
                    </div>
                    <p className="text-3xl text-white font-light">{stats.revenueMonth.toLocaleString()} kr</p>
                </div>
            </div>

            {/* Quick Actions Placeholder */}
            <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-8 text-center">
                <h2 className="text-xl text-white mb-4">Get Started</h2>
                <p className="text-gray-400 mb-6">Manage your services and availability to start accepting bookings.</p>
                <div className="flex justify-center gap-4">
                    <a href="/provider/services" className="px-6 py-3 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium hover:bg-[#b8960f] transition-colors">
                        Manage Services
                    </a>
                    <a href="/provider/calendar" className="px-6 py-3 bg-[#16213e] text-white border border-white/10 rounded-lg hover:bg-[#16213e]/80 transition-colors">
                        View Calendar
                    </a>
                </div>
            </div>
        </div>
    );
}
