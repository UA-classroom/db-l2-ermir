'use client';

import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { User, Calendar, LogOut, Menu, X } from 'lucide-react';

export function Navbar() {
    const { user, isAuthenticated, logout } = useAuthStore();
    const router = useRouter();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
        setIsMobileMenuOpen(false);
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0f0f1a]/80 backdrop-blur-lg border-b border-white/10">
            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                <div className="flex justify-between h-20 items-center">
                    {/* Logo */}
                    <Link href="/" className="flex-shrink-0">
                        <span className="text-2xl font-light tracking-wider text-white">
                            Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link
                            href="/browse"
                            className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                        >
                            Discover
                        </Link>

                        {isAuthenticated && user ? (
                            <>
                                {/* Customer Links */}
                                {user.role === 'customer' && (
                                    <Link
                                        href="/dashboard"
                                        className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                                    >
                                        Dashboard
                                    </Link>
                                )}

                                {/* Provider Links */}
                                {user.role === 'provider' && (
                                    <Link
                                        href="/provider/dashboard"
                                        className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                                    >
                                        Dashboard
                                    </Link>
                                )}

                                <Link
                                    href="/bookings"
                                    className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                                >
                                    My Bookings
                                </Link>

                                {/* User Menu */}
                                <div className="relative group">
                                    <button className="flex items-center gap-2 text-gray-400 hover:text-white font-light transition-colors">
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#d4af37] to-[#b8960f] flex items-center justify-center">
                                            <span className="text-[#0f0f1a] text-xs font-medium">
                                                {user.first_name?.[0]}{user.last_name?.[0]}
                                            </span>
                                        </div>
                                        <span>{user.first_name}</span>
                                    </button>

                                    {/* Dropdown */}
                                    <div className="absolute right-0 mt-2 w-48 bg-[#1a1a2e] border border-white/10 rounded-lg shadow-xl py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                        <Link
                                            href="/profile"
                                            className="flex items-center gap-3 px-4 py-2 text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                                        >
                                            <User className="w-4 h-4" />
                                            Profile
                                        </Link>
                                        <Link
                                            href="/bookings"
                                            className="flex items-center gap-3 px-4 py-2 text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                                        >
                                            <Calendar className="w-4 h-4" />
                                            My Bookings
                                        </Link>
                                        <hr className="my-2 border-white/5" />
                                        <button
                                            onClick={handleLogout}
                                            className="w-full flex items-center gap-3 text-left px-4 py-2 text-red-400 hover:bg-white/5 transition-colors"
                                        >
                                            <LogOut className="w-4 h-4" />
                                            Sign Out
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                                >
                                    Sign In
                                </Link>
                                <Link
                                    href="/register/customer"
                                    className="px-4 py-2 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] rounded-lg font-medium hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                                >
                                    Get Started
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 text-white"
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
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden bg-[#0f0f1a] border-t border-white/10 py-4 px-6">
                    <Link
                        href="/browse"
                        className="block py-3 text-gray-400 hover:text-white font-light transition-colors"
                        onClick={() => setIsMobileMenuOpen(false)}
                    >
                        Discover
                    </Link>
                    {isAuthenticated && user ? (
                        <>
                            <Link
                                href="/dashboard"
                                className="block py-3 text-gray-400 hover:text-white font-light transition-colors"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Dashboard
                            </Link>
                            <Link
                                href="/bookings"
                                className="block py-3 text-gray-400 hover:text-white font-light transition-colors"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                My Bookings
                            </Link>
                            <Link
                                href="/profile"
                                className="block py-3 text-gray-400 hover:text-white font-light transition-colors"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Profile
                            </Link>
                            <button
                                onClick={handleLogout}
                                className="block py-3 text-red-400 font-light"
                            >
                                Sign Out
                            </button>
                        </>
                    ) : (
                        <>
                            <Link
                                href="/login"
                                className="block py-3 text-gray-400 hover:text-white font-light transition-colors"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Sign In
                            </Link>
                            <Link
                                href="/register/customer"
                                className="block py-3 text-[#d4af37] font-light"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            )}
        </nav>
    );
}
