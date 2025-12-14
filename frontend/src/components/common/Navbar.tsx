'use client';

import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export function Navbar() {
    const { user, isAuthenticated, logout } = useAuthStore();
    const router = useRouter();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    return (
        <nav className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    {/* Logo */}
                    <Link href="/" className="flex-shrink-0">
                        <span className="text-2xl font-bold text-blue-600">EasyBooking</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link
                            href="/browse"
                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                        >
                            Browse
                        </Link>

                        {isAuthenticated && user ? (
                            <>
                                {/* Customer Links */}
                                {user.role === 'customer' && (
                                    <>
                                        <Link
                                            href="/bookings"
                                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                        >
                                            My Bookings
                                        </Link>
                                        <Link
                                            href="/favorites"
                                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                        >
                                            Favorites
                                        </Link>
                                    </>
                                )}

                                {/* Provider Links */}
                                {user.role === 'provider' && (
                                    <>
                                        <Link
                                            href="/provider/dashboard"
                                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                        >
                                            Dashboard
                                        </Link>
                                        <Link
                                            href="/provider/calendar"
                                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                        >
                                            Calendar
                                        </Link>
                                        <Link
                                            href="/provider/businesses"
                                            className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                        >
                                            Businesses
                                        </Link>
                                    </>
                                )}

                                {/* Admin Links */}
                                {user.role === 'admin' && (
                                    <Link
                                        href="/admin"
                                        className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                    >
                                        Admin
                                    </Link>
                                )}

                                {/* User Menu */}
                                <div className="relative group">
                                    <button className="flex items-center gap-2 text-gray-700 hover:text-gray-900">
                                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                            <span className="text-blue-600 font-medium text-sm">
                                                {user.first_name[0]}{user.last_name[0]}
                                            </span>
                                        </div>
                                        <span className="font-medium">{user.first_name}</span>
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                        </svg>
                                    </button>

                                    {/* Dropdown */}
                                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                        <Link
                                            href="/profile"
                                            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            Profile
                                        </Link>
                                        <Link
                                            href="/settings"
                                            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            Settings
                                        </Link>
                                        <hr className="my-1" />
                                        <button
                                            onClick={handleLogout}
                                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                                        >
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                >
                                    Login
                                </Link>
                                <Link
                                    href="/register/customer"
                                    className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {isMobileMenuOpen ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </div>

                {/* Mobile Menu */}
                {isMobileMenuOpen && (
                    <div className="md:hidden py-4 border-t border-gray-200">
                        <div className="flex flex-col gap-2">
                            <Link href="/browse" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                Browse
                            </Link>
                            {isAuthenticated && user ? (
                                <>
                                    {user.role === 'customer' && (
                                        <>
                                            <Link href="/bookings" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                                My Bookings
                                            </Link>
                                            <Link href="/favorites" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                                Favorites
                                            </Link>
                                        </>
                                    )}
                                    {user.role === 'provider' && (
                                        <>
                                            <Link href="/provider/dashboard" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                                Dashboard
                                            </Link>
                                            <Link href="/provider/calendar" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                                Calendar
                                            </Link>
                                        </>
                                    )}
                                    <Link href="/profile" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                        Profile
                                    </Link>
                                    <button
                                        onClick={handleLogout}
                                        className="px-4 py-2 text-left text-red-600 hover:bg-gray-100 rounded-lg"
                                    >
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <>
                                    <Link href="/login" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                                        Login
                                    </Link>
                                    <Link href="/register/customer" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-center">
                                        Sign Up
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
