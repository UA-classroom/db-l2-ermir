'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getLocation, getLocationImages, getLocationServices } from '@/lib/businesses';
import { LocationSearchResult, LocationImage } from '@/lib/types/business';

interface Service {
    id: string;
    name: string;
    description?: string;
    categoryId: number;
    variants: ServiceVariant[];
}

interface ServiceVariant {
    id: string;
    name: string;
    price: number;
    durationMinutes: number;
}

export default function LocationDetailPage() {
    const params = useParams();
    const locationId = params.id as string;

    const [location, setLocation] = useState<LocationSearchResult | null>(null);
    const [images, setImages] = useState<LocationImage[]>([]);
    const [services, setServices] = useState<Service[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeImage, setActiveImage] = useState(0);

    useEffect(() => {
        if (locationId) {
            loadLocationData();
        }
    }, [locationId]);

    const loadLocationData = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Load location details
            const locationData = await getLocation(locationId);
            setLocation(locationData);

            // Load images
            try {
                const imageData = await getLocationImages(locationId);
                setImages(imageData);
            } catch {
                // Images might not exist, use placeholder
            }

            // Load services via business
            if (locationData.businessId) {
                try {
                    const serviceData = await getLocationServices(locationData.businessId);
                    setServices(serviceData);
                } catch {
                    // Services might not be available
                }
            }
        } catch (err: any) {
            console.error('Error loading location:', err);
            setError('Location not found');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-gray-400 font-light">Loading...</p>
                </div>
            </div>
        );
    }

    if (error || !location) {
        return (
            <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl text-white mb-4">Location not found</h1>
                    <Link href="/browse" className="text-[#d4af37] hover:underline">
                        ← Back to Browse
                    </Link>
                </div>
            </div>
        );
    }

    // Get image URL - use primary from API or placeholder
    const currentImageUrl = images[activeImage]?.url || location.primaryImage ||
        'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80';

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
                        <Link
                            href="/browse"
                            className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
                        >
                            ← Back
                        </Link>
                    </div>
                </div>
            </nav>

            <div className="pt-24 pb-16 max-w-7xl mx-auto px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Left: Images */}
                    <div>
                        {/* Main Image */}
                        <div className="relative h-80 md:h-96 rounded-2xl overflow-hidden mb-4">
                            <img
                                src={currentImageUrl}
                                alt={location.name}
                                className="w-full h-full object-cover"
                            />
                            {location.primaryCategory && (
                                <span className="absolute top-4 left-4 px-4 py-2 bg-[#0f0f1a]/80 backdrop-blur-sm text-[#d4af37] text-sm font-light rounded-full">
                                    {location.primaryCategory}
                                </span>
                            )}
                        </div>

                        {/* Thumbnail Gallery */}
                        {images.length > 1 && (
                            <div className="flex gap-3 overflow-x-auto pb-2">
                                {images.map((img, idx) => (
                                    <button
                                        key={img.id}
                                        onClick={() => setActiveImage(idx)}
                                        className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${activeImage === idx ? 'border-[#d4af37]' : 'border-transparent opacity-60 hover:opacity-100'
                                            }`}
                                    >
                                        <img src={img.url} alt={img.altText || ''} className="w-full h-full object-cover" />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Right: Info */}
                    <div>
                        {/* Business Name */}
                        <p className="text-[#d4af37] text-sm font-light tracking-wide mb-2">
                            {location.businessName}
                        </p>

                        {/* Location Name */}
                        <h1 className="text-3xl md:text-4xl font-light text-white mb-4">
                            {location.name}
                        </h1>

                        {/* Rating */}
                        <div className="flex items-center gap-2 mb-6">
                            <span className="text-[#d4af37] text-xl">★</span>
                            <span className="text-white text-lg font-light">
                                {location.averageRating?.toFixed(1) || '0.0'}
                            </span>
                            <span className="text-gray-500">
                                ({location.reviewCount} reviews)
                            </span>
                        </div>

                        {/* Address */}
                        <div className="flex items-start gap-3 mb-8 p-4 bg-[#1a1a2e]/50 rounded-lg border border-white/5">
                            <span className="text-xl">📍</span>
                            <div>
                                <p className="text-white font-light">{location.address}</p>
                                <p className="text-gray-500 text-sm">{location.city} {location.postalCode}</p>
                            </div>
                        </div>

                        {/* CTA */}
                        <Link
                            href={`/book/${location.id}`}
                            className="block w-full py-4 text-center bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                        >
                            Book Now
                        </Link>
                    </div>
                </div>

                {/* Services Section */}
                {services.length > 0 && (
                    <section className="mt-16">
                        <h2 className="text-2xl font-light text-white mb-8">Services</h2>
                        <div className="grid gap-4">
                            {services.map((service) => (
                                <div
                                    key={service.id}
                                    className="p-6 bg-[#1a1a2e]/50 border border-white/5 rounded-xl"
                                >
                                    <h3 className="text-lg font-light text-white mb-2">{service.name}</h3>
                                    {service.description && (
                                        <p className="text-gray-500 text-sm mb-4">{service.description}</p>
                                    )}
                                    {service.variants && service.variants.length > 0 && (
                                        <div className="space-y-2">
                                            {service.variants.map((variant) => (
                                                <div
                                                    key={variant.id}
                                                    className="flex justify-between items-center py-2 border-t border-white/5"
                                                >
                                                    <div>
                                                        <span className="text-gray-300">{variant.name}</span>
                                                        <span className="text-gray-500 text-sm ml-2">
                                                            ({variant.durationMinutes} min)
                                                        </span>
                                                    </div>
                                                    <span className="text-[#d4af37] font-medium">
                                                        {variant.price} kr
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}
