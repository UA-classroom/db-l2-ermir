'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getLocations } from '@/lib/businesses';
import { LocationSearchResult } from '@/lib/types/business';

export default function BrowsePage() {
    const [locations, setLocations] = useState<LocationSearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCity, setSelectedCity] = useState('');

    useEffect(() => {
        loadLocations();
    }, []);

    const loadLocations = async (query?: string, city?: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getLocations({
                query: query || undefined,
                city: city || undefined,
                limit: 50,
            });
            setLocations(data);
        } catch (err: any) {
            console.error('Error loading locations:', err);
            setError('Failed to load locations. Make sure the backend is running.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        loadLocations(searchQuery, selectedCity);
    };

    // Get unique cities from locations for filter
    const cities = [...new Set(locations.map((l) => l.city))].filter(Boolean);

    return (
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
                        <div className="hidden md:flex items-center gap-8">
                            <Link
                                href="/browse"
                                className="text-[#d4af37] font-light tracking-wide"
                            >
                                Discover
                            </Link>
                            <Link
                                href="/login"
                                className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                            >
                                Sign In
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-12 bg-gradient-to-br from-[#0f0f1a] via-[#1a1a2e] to-[#16213e]">
                <div className="max-w-7xl mx-auto px-6 lg:px-8">
                    <div className="text-center mb-10">
                        <h1 className="text-4xl md:text-5xl font-light text-white mb-4">
                            Discover Premium Services
                        </h1>
                        <p className="text-gray-400 font-light text-lg max-w-2xl mx-auto">
                            Browse our curated selection of exceptional service providers
                        </p>
                    </div>

                    {/* Search Form */}
                    <form onSubmit={handleSearch} className="max-w-3xl mx-auto">
                        <div className="flex flex-col md:flex-row gap-4">
                            <div className="flex-1">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search services, salons, spas..."
                                    className="w-full px-6 py-4 bg-[#1a1a2e]/80 border border-white/10 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 focus:border-[#d4af37]/50"
                                />
                            </div>
                            <select
                                value={selectedCity}
                                onChange={(e) => setSelectedCity(e.target.value)}
                                className="px-6 py-4 bg-[#1a1a2e]/80 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                            >
                                <option value="">All Cities</option>
                                {cities.map((city) => (
                                    <option key={city} value={city}>
                                        {city}
                                    </option>
                                ))}
                            </select>
                            <button
                                type="submit"
                                className="px-8 py-4 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                            >
                                Search
                            </button>
                        </div>
                    </form>
                </div>
            </section>

            {/* Results Section */}
            <section className="py-12 px-6 lg:px-8 max-w-7xl mx-auto">
                {/* Status */}
                <div className="mb-8">
                    <p className="text-gray-400 font-light">
                        {isLoading
                            ? 'Loading...'
                            : `${locations.length} locations found`}
                    </p>
                </div>

                {/* Error State */}
                {error && (
                    <div className="text-center py-20">
                        <p className="text-red-400 mb-4">{error}</p>
                        <p className="text-gray-500 text-sm">
                            Run <code className="text-[#d4af37]">uvicorn app.main:app --reload</code> in the backend folder
                        </p>
                    </div>
                )}

                {/* Loading State */}
                {isLoading && !error && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, i) => (
                            <div
                                key={i}
                                className="bg-[#1a1a2e]/50 rounded-xl overflow-hidden animate-pulse"
                            >
                                <div className="h-48 bg-[#16213e]"></div>
                                <div className="p-5">
                                    <div className="h-5 bg-[#16213e] rounded mb-3 w-3/4"></div>
                                    <div className="h-4 bg-[#16213e] rounded w-1/2"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Location Cards Grid */}
                {!isLoading && !error && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {locations.map((location) => (
                            <LocationCard key={location.id} location={location} />
                        ))}
                    </div>
                )}

                {/* Empty State */}
                {!isLoading && !error && locations.length === 0 && (
                    <div className="text-center py-20">
                        <p className="text-gray-400 text-xl mb-2">No locations found</p>
                        <p className="text-gray-500">Try adjusting your search criteria</p>
                    </div>
                )}
            </section>
        </div>
    );
}

// Location Card Component
function LocationCard({ location }: { location: LocationSearchResult }) {
    // Use primary image if available, otherwise placeholder based on category
    const imageUrl = location.primaryImage || getPlaceholderImage(location.primaryCategory);

    return (
        <Link href={`/location/${location.id}`}>
            <div className="group bg-[#1a1a2e]/50 border border-white/5 rounded-xl overflow-hidden hover:border-[#d4af37]/30 transition-all duration-500 cursor-pointer">
                {/* Image */}
                <div className="relative h-48 overflow-hidden">
                    <img
                        src={imageUrl}
                        alt={location.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    {/* Category Badge */}
                    {location.primaryCategory && (
                        <span className="absolute top-3 left-3 px-3 py-1 bg-[#0f0f1a]/80 backdrop-blur-sm text-[#d4af37] text-xs font-light rounded-full">
                            {location.primaryCategory}
                        </span>
                    )}
                </div>

                {/* Content */}
                <div className="p-5">
                    {/* Business Name */}
                    <p className="text-[#d4af37] text-xs font-light tracking-wide mb-1">
                        {location.businessName}
                    </p>

                    {/* Location Name */}
                    <h3 className="text-lg font-light text-white mb-2 group-hover:text-[#d4af37] transition-colors">
                        {location.name}
                    </h3>

                    {/* Address */}
                    <p className="text-gray-500 text-sm font-light mb-3">
                        📍 {location.address}, {location.city}
                    </p>

                    {/* Rating */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                            <span className="text-[#d4af37]">★</span>
                            <span className="text-white font-light">
                                {location.averageRating?.toFixed(1) || '0.0'}
                            </span>
                            <span className="text-gray-500 text-sm">
                                ({location.reviewCount} reviews)
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}

// Get placeholder image based on category
function getPlaceholderImage(category?: string): string {
    const categoryImages: Record<string, string> = {
        'Hair': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80',
        'Spa': 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800&q=80',
        'Gym': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80',
        'Restaurant': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80',
        'Medical': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80',
        'Pet': 'https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=800&q=80',
        'Auto': 'https://images.unsplash.com/photo-1625047509248-ec889cbff17f?w=800&q=80',
        'Home': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80',
    };

    if (category) {
        for (const [key, url] of Object.entries(categoryImages)) {
            if (category.toLowerCase().includes(key.toLowerCase())) {
                return url;
            }
        }
    }

    // Default placeholder
    return 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80';
}
