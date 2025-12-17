'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { ProtectedRoute } from '@/components/common';
import { useEffect } from 'react';
import { getBusinesses, getBusinessWithLocations } from '@/lib/businesses';
import { useProviderStore } from '@/lib/store/providerStore';
import { LocationSelector } from '@/components/provider/LocationSelector';
import {
    LayoutDashboard,
    Calendar,
    Scissors,
    Settings,
    LogOut,
    Store,
    Users,
    Package
} from 'lucide-react';

export default function ProviderLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const { logout, user } = useAuthStore();
    const { setBusiness, setLocations, setLoading } = useProviderStore();

    // Hydrate Global Provider Store
    useEffect(() => {
        const initProvider = async () => {
            if (!user?.id) return;
            try {
                setLoading(true);
                // 1. Fetch Business
                const businesses = await getBusinesses({ ownerId: user.id });
                if (businesses.length > 0) {
                    const myBusiness = businesses[0];
                    setBusiness(myBusiness);

                    // 2. Fetch Locations
                    const details = await getBusinessWithLocations(myBusiness.id);
                    setLocations(details.locations || []);
                }
            } catch (e) {
                console.error("Failed to load provider context:", e);
            } finally {
                setLoading(false);
            }
        };

        initProvider();
    }, [user?.id, setBusiness, setLocations, setLoading]);

    const navigation = [
        { name: 'Dashboard', href: '/provider/dashboard', icon: LayoutDashboard },
        { name: 'Calendar', href: '/provider/calendar', icon: Calendar },
        { name: 'Services', href: '/provider/services', icon: Scissors },
        { name: 'Products', href: '/provider/products', icon: Package },
        { name: 'Employees', href: '/provider/employees', icon: Users },
        { name: 'Settings', href: '/provider/settings', icon: Settings },
    ];

    return (
        <ProtectedRoute allowedRoles={['provider', 'admin']}>
            <div className="min-h-screen bg-[#0f0f1a] flex">
                {/* Sidebar */}
                <aside className="w-64 bg-[#1a1a2e] border-r border-white/5 flex flex-col fixed inset-y-0 text-white z-50">
                    <div className="h-20 flex items-center px-6 border-b border-white/5">
                        <Link href="/" className="flex items-center gap-2">
                            <Store className="w-6 h-6 text-[#d4af37]" />
                            <span className="text-xl font-light tracking-wider">
                                Provider<span className="font-semibold text-[#d4af37]">Portal</span>
                            </span>
                        </Link>
                    </div>

                    <nav className="flex-1 px-4 py-8 space-y-2">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                        ? 'bg-[#d4af37]/20 text-[#d4af37]'
                                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <item.icon className="w-5 h-5" />
                                    <span className="font-light">{item.name}</span>
                                </Link>
                            );
                        })}
                    </nav>

                    <div className="p-4 border-t border-white/5">
                        <button
                            onClick={logout}
                            className="flex items-center gap-3 px-4 py-3 w-full text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all"
                        >
                            <LogOut className="w-5 h-5" />
                            <span className="font-light">Sign Out</span>
                        </button>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 ml-64 flex flex-col min-h-screen">
                    {/* Header Bar */}
                    <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0f0f1a] sticky top-0 z-40">
                        <div className="text-gray-400 text-sm">
                            {/* Breadcrumbs or Title could go here */}
                        </div>

                        <div className="flex items-center gap-4">
                            <LocationSelector />
                            {/* We could add User Profile dropdown here too */}
                        </div>
                    </header>

                    <div className="p-8">
                        {children}
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
