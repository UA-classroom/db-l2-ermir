'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { updateProfile } from '@/lib/users';
import { ProtectedRoute } from '@/components/common';
import { Calendar, Sparkles } from 'lucide-react';

export default function ProfilePage() {
    const router = useRouter();
    const { user, isAuthenticated, logout } = useAuthStore();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
    });
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (user) {
            setFormData({
                firstName: user.first_name || '',
                lastName: user.last_name || '',
                email: user.email || '',
                phone: user.phone_number || (user as any).mobileNumber || '',
            });
        }
    }, [user]);

    const handleLogout = () => {
        logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const updated = await updateProfile({
                firstName: formData.firstName,
                lastName: formData.lastName,
                phoneNumber: formData.phone,
            });
            // Update local user state in store
            if (user) {
                useAuthStore.setState({
                    user: {
                        ...user,
                        first_name: formData.firstName,
                        last_name: formData.lastName,
                        phone_number: formData.phone,
                    },
                });
            }
            setIsEditing(false);
        } catch (err) {
            console.error('Error updating profile:', err);
            alert('Failed to save profile. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

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
                                    href="/bookings"
                                    className="text-gray-400 hover:text-white font-light transition-colors"
                                >
                                    My Bookings
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

                <div className="pt-28 pb-16 max-w-2xl mx-auto px-6 lg:px-8">
                    {/* Header */}
                    <div className="text-center mb-12">
                        {/* Avatar */}
                        <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-[#d4af37] to-[#b8960f] flex items-center justify-center">
                            <span className="text-3xl font-light text-[#0f0f1a]">
                                {user?.first_name?.[0]}{user?.last_name?.[0]}
                            </span>
                        </div>
                        <h1 className="text-3xl font-light text-white mb-2">
                            {user?.first_name} {user?.last_name}
                        </h1>
                        <p className="text-[#d4af37] text-sm font-light tracking-wide uppercase">
                            {user?.role === 'provider' ? 'Service Provider' : 'Member'}
                        </p>
                    </div>

                    {/* Profile Card */}
                    <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-2xl p-8">
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xl font-light text-white">Profile Details</h2>
                            {!isEditing ? (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="text-[#d4af37] hover:text-[#e8c547] font-light text-sm transition-colors"
                                >
                                    Edit
                                </button>
                            ) : (
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setIsEditing(false)}
                                        className="text-gray-400 hover:text-white font-light text-sm transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        disabled={isSaving}
                                        className="text-[#d4af37] hover:text-[#e8c547] font-light text-sm transition-colors"
                                    >
                                        {isSaving ? 'Saving...' : 'Save'}
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="space-y-6">
                            {/* First Name */}
                            <div>
                                <label className="block text-sm text-gray-500 mb-2">First Name</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={formData.firstName}
                                        onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                                        className="w-full px-4 py-3 bg-[#16213e]/50 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                    />
                                ) : (
                                    <p className="text-white font-light">{formData.firstName}</p>
                                )}
                            </div>

                            {/* Last Name */}
                            <div>
                                <label className="block text-sm text-gray-500 mb-2">Last Name</label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={formData.lastName}
                                        onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                                        className="w-full px-4 py-3 bg-[#16213e]/50 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                    />
                                ) : (
                                    <p className="text-white font-light">{formData.lastName}</p>
                                )}
                            </div>

                            {/* Email */}
                            <div>
                                <label className="block text-sm text-gray-500 mb-2">Email</label>
                                <p className="text-white font-light">{formData.email}</p>
                                <p className="text-gray-500 text-xs mt-1">Email cannot be changed</p>
                            </div>

                            {/* Phone */}
                            <div>
                                <label className="block text-sm text-gray-500 mb-2">Phone</label>
                                {isEditing ? (
                                    <input
                                        type="tel"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        className="w-full px-4 py-3 bg-[#16213e]/50 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                    />
                                ) : (
                                    <p className="text-white font-light">{formData.phone || 'Not provided'}</p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div className="mt-8 grid grid-cols-2 gap-4">
                        <Link
                            href="/bookings"
                            className="group p-6 bg-[#1a1a2e]/50 border border-white/5 rounded-xl hover:border-[#d4af37]/30 transition-all"
                        >
                            <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center mb-3">
                                <Calendar className="w-5 h-5 text-[#d4af37]" />
                            </div>
                            <h3 className="text-white font-light group-hover:text-[#d4af37] transition-colors">
                                My Bookings
                            </h3>
                            <p className="text-gray-500 text-sm">View upcoming appointments</p>
                        </Link>
                        <Link
                            href="/browse"
                            className="group p-6 bg-[#1a1a2e]/50 border border-white/5 rounded-xl hover:border-[#d4af37]/30 transition-all"
                        >
                            <div className="w-10 h-10 rounded-full bg-[#d4af37]/20 flex items-center justify-center mb-3">
                                <Sparkles className="w-5 h-5 text-[#d4af37]" />
                            </div>
                            <h3 className="text-white font-light group-hover:text-[#d4af37] transition-colors">
                                Discover
                            </h3>
                            <p className="text-gray-500 text-sm">Find new services</p>
                        </Link>
                    </div>

                    {/* Danger Zone */}
                    <div className="mt-12 pt-8 border-t border-white/5">
                        <h3 className="text-red-400 text-sm font-light mb-4">Danger Zone</h3>
                        <button
                            onClick={handleLogout}
                            className="px-6 py-3 border border-red-400/30 text-red-400 font-light rounded-lg hover:bg-red-400/10 transition-all"
                        >
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
