'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { login, getCurrentUser } from '@/lib/auth';

// Form validation schema
const loginSchema = z.object({
    email: z.string().email('Please enter a valid email'),
    password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const { setAuth } = useAuthStore();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormData) => {
        setIsLoading(true);
        setError(null);

        try {
            const tokens = await login(data);
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);

            const user = await getCurrentUser();
            setAuth(
                {
                    id: user.id,
                    email: user.email,
                    first_name: user.first_name,
                    last_name: user.last_name,
                    role: user.role,
                    phone_number: user.phone_number,
                    is_active: user.is_active,
                },
                tokens.access_token,
                tokens.refresh_token
            );

            if (user.role === 'provider') {
                router.push('/provider/dashboard');
            } else if (user.role === 'admin') {
                router.push('/admin');
            } else {
                router.push('/');
            }
        } catch (err: any) {
            console.error('Login error:', err);
            setError(err.response?.data?.detail || 'Invalid email or password');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center py-12 px-4 relative overflow-hidden">
            {/* Background decorations */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-[#d4af37]/5 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-[#d4af37]/10 rounded-full blur-3xl"></div>

            <div className="relative z-10 max-w-md w-full">
                {/* Logo/Brand */}
                <div className="text-center mb-10">
                    <Link href="/" className="inline-block">
                        <span className="text-3xl font-light tracking-wider text-white">
                            Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
                        </span>
                    </Link>
                    <h2 className="mt-6 text-2xl font-light text-white">
                        Welcome back
                    </h2>
                    <p className="mt-2 text-gray-400 font-light">
                        Sign in to continue your journey
                    </p>
                </div>

                {/* Login Form */}
                <div className="bg-[#1a1a2e]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        {/* Error Message */}
                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                                <p className="text-sm text-red-400">{error}</p>
                            </div>
                        )}

                        {/* Email Field */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Email address
                            </label>
                            <input
                                {...register('email')}
                                type="email"
                                autoComplete="email"
                                className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.email ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="you@example.com"
                            />
                            {errors.email && (
                                <p className="mt-2 text-sm text-red-400">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Password Field */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Password
                            </label>
                            <input
                                {...register('password')}
                                type="password"
                                autoComplete="current-password"
                                className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.password ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="••••••••"
                            />
                            {errors.password && (
                                <p className="mt-2 text-sm text-red-400">{errors.password.message}</p>
                            )}
                        </div>

                        {/* Forgot Password Link */}
                        <div className="flex items-center justify-end">
                            <Link
                                href="/forgot-password"
                                className="text-sm text-[#d4af37] hover:text-[#e8c547] transition-colors"
                            >
                                Forgot your password?
                            </Link>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Signing in...
                                </span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="mt-8 relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-4 bg-[#1a1a2e] text-gray-500">
                                New to ComfortBooking?
                            </span>
                        </div>
                    </div>

                    {/* Register Links */}
                    <div className="mt-6 grid grid-cols-2 gap-4">
                        <Link
                            href="/register/customer"
                            className="flex justify-center px-4 py-3 border border-white/10 text-gray-300 font-light rounded-lg hover:bg-white/5 hover:border-white/20 transition-all"
                        >
                            As Guest
                        </Link>
                        <Link
                            href="/register/provider"
                            className="flex justify-center px-4 py-3 border border-[#d4af37]/30 text-[#d4af37] font-light rounded-lg hover:bg-[#d4af37]/10 hover:border-[#d4af37]/50 transition-all"
                        >
                            As Provider
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
