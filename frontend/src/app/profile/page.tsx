'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { updateProfile, getAddresses, createAddress, updateAddress, deleteAddress, changePassword, Address, CreateAddressData, UpdateAddressData } from '@/lib/users';
import { ProtectedRoute } from '@/components/common';
import { Calendar, Sparkles, MapPin, Plus, Trash2, Edit2, X, Check, Lock } from 'lucide-react';

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

    // Address State
    const [addresses, setAddresses] = useState<Address[]>([]);
    const [loadingAddresses, setLoadingAddresses] = useState(false);
    const [editingAddress, setEditingAddress] = useState<Address | null>(null);
    const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
    const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

    useEffect(() => {
        if (user) {
            setFormData({
                firstName: user.first_name || '',
                lastName: user.last_name || '',
                email: user.email || '',
                phone: user.phone_number || (user as any).mobileNumber || '',
            });
            loadAddresses();
        }
    }, [user]);

    const loadAddresses = async () => {
        setLoadingAddresses(true);
        try {
            const data = await getAddresses();
            setAddresses(data);
        } catch (err) {
            console.error('Error loading addresses:', err);
        } finally {
            setLoadingAddresses(false);
        }
    };

    const handleLogout = () => {
        logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
    };

    const handleSaveProfile = async () => {
        setIsSaving(true);
        try {
            await updateProfile({
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

    // Address Handlers
    const handleAddAddress = () => {
        setEditingAddress(null);
        setIsAddressModalOpen(true);
    };

    const handleEditAddress = (addr: Address) => {
        setEditingAddress(addr);
        setIsAddressModalOpen(true);
    };

    const handleDeleteAddress = async (id: string) => {
        if (!confirm('Are you sure you want to delete this address?')) return;
        try {
            await deleteAddress(id);
            setAddresses(addresses.filter(a => a.id !== id));
        } catch (err) {
            console.error('Error deleting address:', err);
            alert('Failed to delete address');
        }
    };

    const handleSaveAddress = async (data: CreateAddressData | UpdateAddressData) => {
        try {
            if (editingAddress) {
                const updated = await updateAddress(editingAddress.id, data);
                setAddresses(addresses.map(a => a.id === updated.id ? updated : a));
            } else {
                const created = await createAddress(data as CreateAddressData);
                setAddresses([...addresses, created]);
            }
            setIsAddressModalOpen(false);
        } catch (err) {
            console.error('Error saving address:', err);
            alert('Failed to save address');
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
                    <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-2xl p-8 mb-8">
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xl font-light text-white">Profile Details</h2>
                            {!isEditing ? (
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setIsPasswordModalOpen(true)}
                                        className="flex items-center gap-2 text-gray-400 hover:text-white font-light text-sm transition-colors"
                                    >
                                        <Lock className="w-3 h-3" /> Change Password
                                    </button>
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="text-[#d4af37] hover:text-[#e8c547] font-light text-sm transition-colors"
                                    >
                                        Edit
                                    </button>
                                </div>
                            ) : (
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setIsEditing(false)}
                                        className="text-gray-400 hover:text-white font-light text-sm transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleSaveProfile}
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

                    {/* Address Section */}
                    <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-2xl p-8 mb-8">
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xl font-light text-white">My Addresses</h2>
                            <button
                                onClick={handleAddAddress}
                                className="flex items-center gap-2 text-[#d4af37] hover:text-[#e8c547] font-light text-sm transition-colors"
                            >
                                <Plus className="w-4 h-4" /> Add Address
                            </button>
                        </div>

                        {loadingAddresses ? (
                            <div className="flex justify-center py-8">
                                <div className="w-6 h-6 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : addresses.length === 0 ? (
                            <div className="text-center py-8 border border-dashed border-white/10 rounded-xl">
                                <MapPin className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                                <p className="text-gray-500 text-sm">No addresses added yet</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {addresses.map((addr) => (
                                    <div key={addr.id} className="flex justify-between items-start p-4 bg-[#16213e]/30 rounded-xl border border-white/5 group hover:border-[#d4af37]/20 transition-all">
                                        <div>
                                            {addr.is_default && (
                                                <span className="inline-block px-2 py-0.5 mb-2 bg-[#d4af37]/20 text-[#d4af37] text-[10px] rounded uppercase tracking-wider">Default</span>
                                            )}
                                            <p className="text-white font-light">{addr.street_address}</p>
                                            <p className="text-gray-400 text-sm">{addr.postal_code} {addr.city}</p>
                                            {addr.country && <p className="text-gray-500 text-xs">{addr.country}</p>}
                                        </div>
                                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => handleEditAddress(addr)}
                                                className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                                            >
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteAddress(addr.id)}
                                                className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Quick Links */}
                    <div className="grid grid-cols-2 gap-4">
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

                {/* Address Modal */}
                {isAddressModalOpen && (
                    <AddressModal
                        address={editingAddress}
                        onClose={() => setIsAddressModalOpen(false)}
                        onSave={handleSaveAddress}
                    />
                )}

                {/* Password Modal */}
                {isPasswordModalOpen && (
                    <PasswordModal
                        onClose={() => setIsPasswordModalOpen(false)}
                    />
                )}
            </div>
        </ProtectedRoute>
    );
}

function AddressModal({
    address,
    onClose,
    onSave
}: {
    address: Address | null;
    onClose: () => void;
    onSave: (data: CreateAddressData | UpdateAddressData) => Promise<void>;
}) {
    const [formData, setFormData] = useState({
        street_address: address?.street_address || '',
        postal_code: address?.postal_code || '',
        city: address?.city || '',
        country: address?.country || 'Sweden',
        is_default: address?.is_default || false,
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        await onSave(formData);
        setIsSubmitting(false);
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-xl">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-light text-white">
                        {address ? 'Edit Address' : 'Add New Address'}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Street Address</label>
                        <input
                            type="text"
                            required
                            value={formData.street_address}
                            onChange={(e) => setFormData({ ...formData, street_address: e.target.value })}
                            className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Postal Code</label>
                            <input
                                type="text"
                                required
                                value={formData.postal_code}
                                onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                                className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">City</label>
                            <input
                                type="text"
                                required
                                value={formData.city}
                                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Country</label>
                        <input
                            type="text"
                            value={formData.country}
                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                            className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                        />
                    </div>

                    <div className="flex items-center gap-2 pt-2">
                        <button
                            type="button"
                            onClick={() => setFormData({ ...formData, is_default: !formData.is_default })}
                            className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${formData.is_default
                                ? 'bg-[#d4af37] border-[#d4af37]'
                                : 'border-gray-500 bg-transparent'
                                }`}
                        >
                            {formData.is_default && <Check className="w-3 h-3 text-[#0f0f1a]" />}
                        </button>
                        <span className="text-gray-400 text-sm">Set as default address</span>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-[#16213e] text-white rounded-lg hover:bg-[#16213e]/80 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="flex-1 px-4 py-2 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-lg disabled:opacity-50"
                        >
                            {isSubmitting ? 'Saving...' : 'Save Address'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function PasswordModal({ onClose }: { onClose: () => void }) {
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.newPassword !== formData.confirmPassword) {
            setError('New passwords do not match');
            return;
        }

        if (formData.newPassword.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        setIsSubmitting(true);
        try {
            await changePassword({
                currentPassword: formData.currentPassword,
                newPassword: formData.newPassword,
            });
            alert('Password changed successfully');
            onClose();
        } catch (err: any) {
            console.error('Error changing password:', err);
            setError(err.response?.data?.detail || 'Failed to change password');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-xl">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-light text-white">Change Password</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Current Password</label>
                        <input
                            type="password"
                            required
                            value={formData.currentPassword}
                            onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
                            className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">New Password</label>
                        <input
                            type="password"
                            required
                            value={formData.newPassword}
                            onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                            className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Confirm New Password</label>
                        <input
                            type="password"
                            required
                            value={formData.confirmPassword}
                            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                            className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                        />
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-[#16213e] text-white rounded-lg hover:bg-[#16213e]/80 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="flex-1 px-4 py-2 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-lg disabled:opacity-50"
                        >
                            {isSubmitting ? 'Updating...' : 'Update Password'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
