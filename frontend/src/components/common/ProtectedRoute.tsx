'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore, UserRole } from '@/lib/store';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: UserRole[];
    fallbackUrl?: string;
}

/**
 * ProtectedRoute - Wraps pages that require authentication
 * 
 * Usage:
 * ```tsx
 * // Any authenticated user
 * <ProtectedRoute>{children}</ProtectedRoute>
 * 
 * // Only providers
 * <ProtectedRoute allowedRoles={['provider']}>{children}</ProtectedRoute>
 * 
 * // Providers and admins
 * <ProtectedRoute allowedRoles={['provider', 'admin']}>{children}</ProtectedRoute>
 * ```
 */
export function ProtectedRoute({
    children,
    allowedRoles,
    fallbackUrl = '/login'
}: ProtectedRouteProps) {
    const router = useRouter();
    const { user, isAuthenticated, isLoading } = useAuthStore();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        // Wait for auth state to be loaded
        if (isLoading) return;

        // Not authenticated → redirect to login
        if (!isAuthenticated || !user) {
            router.push(fallbackUrl);
            return;
        }

        // Check role if specified
        if (allowedRoles && !allowedRoles.includes(user.role)) {
            // Redirect based on actual role
            if (user.role === 'provider') {
                router.push('/provider/dashboard');
            } else if (user.role === 'admin') {
                router.push('/admin');
            } else {
                router.push('/');
            }
            return;
        }

        setIsChecking(false);
    }, [user, isAuthenticated, isLoading, allowedRoles, router, fallbackUrl]);

    // Show loading state while checking auth
    if (isLoading || isChecking) {
        return (
            <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-gray-400 font-light">Loading...</p>
                </div>
            </div>
        );
    }

    // User is authenticated and has correct role
    return <>{children}</>;
}
