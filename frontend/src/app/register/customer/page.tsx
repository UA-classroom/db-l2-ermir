'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { registerCustomer, login, getCurrentUser } from '@/lib/auth';
import { useAuthStore } from '@/lib/store';

const registerSchema = z.object({
    first_name: z.string().min(2, 'First name must be at least 2 characters'),
    last_name: z.string().min(2, 'Last name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email'),
    phone_number: z.string().optional(),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function CustomerRegisterPage() {
    const router = useRouter();
    const { setAuth } = useAuthStore();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormData) => {
        setIsLoading(true);
        setError(null);

        try {
            await registerCustomer({
                first_name: data.first_name,
                last_name: data.last_name,
                email: data.email,
                password: data.password,
                phone_number: data.phone_number,
            });

            const tokens = await login({ email: data.email, password: data.password });
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

            router.push('/');
        } catch (err: any) {
            console.error('Registration error:', err);
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center py-12 px-4 relative overflow-hidden">
            {/* Background decorations */}
            <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#d4af37]/5 rounded-full blur-3xl"></div>
            <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-[#d4af37]/10 rounded-full blur-3xl"></div>

            <div className="relative z-10 max-w-md w-full">
                {/* Logo/Brand */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-block">
                        <span className="text-3xl font-light tracking-wider text-white">
                            Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
                        </span>
                    </Link>
                    <h2 className="mt-6 text-2xl font-light text-white">
                        Create your account
                    </h2>
                    <p className="mt-2 text-gray-400 font-light">
                        Join to book premium experiences
                    </p>
                </div>

                {/* Register Form */}
                <div className="bg-[#1a1a2e]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        {/* Error Message */}
                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                                <p className="text-sm text-red-400">{error}</p>
                            </div>
                        )}

                        {/* Name Fields */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-light text-gray-300 mb-2">
                                    First name
                                </label>
                                <input
                                    {...register('first_name')}
                                    type="text"
                                    className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.first_name ? 'border-red-500/50' : 'border-white/10'
                                        }`}
                                    placeholder="John"
                                />
                                {errors.first_name && (
                                    <p className="mt-1.5 text-xs text-red-400">{errors.first_name.message}</p>
                                )}
                            </div>
                            <div>
                                <label className="block text-sm font-light text-gray-300 mb-2">
                                    Last name
                                </label>
                                <input
                                    {...register('last_name')}
                                    type="text"
                                    className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.last_name ? 'border-red-500/50' : 'border-white/10'
                                        }`}
                                    placeholder="Doe"
                                />
                                {errors.last_name && (
                                    <p className="mt-1.5 text-xs text-red-400">{errors.last_name.message}</p>
                                )}
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Email address
                            </label>
                            <input
                                {...register('email')}
                                type="email"
                                className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.email ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="you@example.com"
                            />
                            {errors.email && (
                                <p className="mt-2 text-sm text-red-400">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Phone (Optional) */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Phone <span className="text-gray-500">(optional)</span>
                            </label>
                            <input
                                {...register('phone_number')}
                                type="tel"
                                className="w-full px-4 py-3 bg-[#16213e]/50 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all"
                                placeholder="+46 70 123 4567"
                            />
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Password
                            </label>
                            <input
                                {...register('password')}
                                type="password"
                                className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.password ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="••••••••"
                            />
                            {errors.password && (
                                <p className="mt-2 text-sm text-red-400">{errors.password.message}</p>
                            )}
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label className="block text-sm font-light text-gray-300 mb-2">
                                Confirm password
                            </label>
                            <input
                                {...register('confirm_password')}
                                type="password"
                                className={`w-full px-4 py-3 bg-[#16213e]/50 border rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50 transition-all ${errors.confirm_password ? 'border-red-500/50' : 'border-white/10'
                                    }`}
                                placeholder="••••••••"
                            />
                            {errors.confirm_password && (
                                <p className="mt-2 text-sm text-red-400">{errors.confirm_password.message}</p>
                            )}
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                        >
                            {isLoading ? 'Creating account...' : 'Create Account'}
                        </button>
                    </form>

                    {/* Login Link */}
                    <p className="mt-6 text-center text-sm text-gray-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-[#d4af37] hover:text-[#e8c547]">
                            Sign in
                        </Link>
                    </p>
                </div>

                {/* Provider Link */}
                <p className="mt-6 text-center text-sm text-gray-500">
                    Want to offer services?{' '}
                    <Link href="/register/provider" className="text-[#d4af37] hover:text-[#e8c547]">
                        Register as Provider
                    </Link>
                </p>
            </div>
        </div>
    );
}
