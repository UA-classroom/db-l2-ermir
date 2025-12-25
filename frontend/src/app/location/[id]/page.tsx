'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getLocation, getLocationImages, getLocationServices, getLocationContacts } from '@/lib/businesses';
import { LocationSearchResult, LocationImage, Service, ServiceVariant } from '@/lib/types/business';
import { getBusinessReviews, Review } from '@/lib/reviews';
import { getFavorites, addFavorite, removeFavorite, FavoriteResponse } from '@/lib/favorites';
import { useAuthStore } from '@/lib/store';
import { Navbar } from '@/components/common';
import { MapPin, Star, Heart, Phone, User } from 'lucide-react';



export default function LocationDetailPage() {
    const params = useParams();
    const locationId = params.id as string;
    const { isAuthenticated } = useAuthStore();

    const [location, setLocation] = useState<LocationSearchResult | null>(null);
    const [images, setImages] = useState<LocationImage[]>([]);
    const [services, setServices] = useState<Service[]>([]);
    const [reviews, setReviews] = useState<Review[]>([]);
    const [contacts, setContacts] = useState<{ id: number; contactType: string; phoneNumber: string }[]>([]);
    const [isFavorite, setIsFavorite] = useState(false);
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

                // Load reviews (for this specific location)
                try {
                    const reviewData = await getBusinessReviews(locationId);
                    setReviews(reviewData);
                } catch {
                    // Reviews might not exist
                }
            }

            // Load contacts
            try {
                const contactData = await getLocationContacts(locationId);
                setContacts(contactData);
            } catch {
                // Contacts might not exist
            }

            // Check if favorited
            if (isAuthenticated) {
                try {
                    const favorites = await getFavorites();
                    setIsFavorite(favorites.some(f => f.locationId === locationId));
                } catch {
                    // Favorites might fail
                }
            }
        } catch (err: any) {
            console.error('Error loading location:', err);
            setError('Location not found');
        } finally {
            setIsLoading(false);
        }
    };

    const handleToggleFavorite = async () => {
        if (!isAuthenticated) return;
        try {
            if (isFavorite) {
                await removeFavorite(locationId);
                setIsFavorite(false);
            } else {
                await addFavorite(locationId);
                setIsFavorite(true);
            }
        } catch (err) {
            console.error('Error toggling favorite:', err);
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
            <Navbar />

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
                            <Star className="w-5 h-5 text-[#d4af37] fill-[#d4af37]" />
                            <span className="text-white text-lg font-light">
                                {location.averageRating?.toFixed(1) || '0.0'}
                            </span>
                            <span className="text-gray-500">
                                ({location.reviewCount} reviews)
                            </span>
                        </div>

                        {/* Address */}
                        <div className="flex items-start gap-3 mb-8 p-4 bg-[#1a1a2e]/50 rounded-lg border border-white/5">
                            <MapPin className="w-5 h-5 text-[#d4af37] mt-0.5" />
                            <div>
                                <p className="text-white font-light">{location.address}</p>
                                <p className="text-gray-500 text-sm">{location.city} {location.postalCode}</p>
                            </div>
                        </div>

                        {/* CTA */}
                        <div className="flex gap-3">
                            <Link
                                href={`/book/${location.id}`}
                                className="flex-1 py-4 text-center bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
                            >
                                Book Now
                            </Link>
                            {isAuthenticated && (
                                <button
                                    onClick={handleToggleFavorite}
                                    className={`px-4 py-4 rounded-lg border transition-all ${isFavorite
                                        ? 'bg-[#d4af37]/20 border-[#d4af37] text-[#d4af37]'
                                        : 'bg-[#1a1a2e] border-white/10 text-gray-400 hover:text-[#d4af37] hover:border-[#d4af37]'
                                        }`}
                                >
                                    <Heart className={`w-5 h-5 ${isFavorite ? 'fill-[#d4af37]' : ''}`} />
                                </button>
                            )}
                        </div>

                        {/* Contact Info */}
                        {contacts.length > 0 && (
                            <div className="mt-6 p-4 bg-[#1a1a2e]/50 rounded-lg border border-white/5">
                                <h3 className="text-white font-light mb-3 flex items-center gap-2">
                                    <Phone className="w-4 h-4 text-[#d4af37]" /> Contact
                                </h3>
                                {contacts.map((contact) => (
                                    <div key={contact.id} className="flex justify-between items-center py-1">
                                        <span className="text-gray-400 text-sm">{contact.contactType}</span>
                                        <a href={`tel:${contact.phoneNumber}`} className="text-[#d4af37] hover:underline">
                                            {contact.phoneNumber}
                                        </a>
                                    </div>
                                ))}
                            </div>
                        )}
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
                                                            ({variant.durationMinutes || variant.duration_minutes} min)
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

                {/* Reviews Section */}
                {reviews.length > 0 && (
                    <section className="mt-16">
                        <h2 className="text-2xl font-light text-white mb-8">Customer Reviews</h2>
                        <div className="grid gap-4">
                            {reviews.map((review) => (
                                <div
                                    key={review.id}
                                    className="p-6 bg-[#1a1a2e]/50 border border-white/5 rounded-xl"
                                >
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-full bg-[#d4af37]/20 flex items-center justify-center">
                                                <User className="w-4 h-4 text-[#d4af37]" />
                                            </div>
                                            <span className="text-white font-light">
                                                {review.user_name || 'Customer'}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {[...Array(5)].map((_, i) => (
                                                <Star
                                                    key={i}
                                                    className={`w-4 h-4 ${i < review.rating
                                                        ? 'text-[#d4af37] fill-[#d4af37]'
                                                        : 'text-gray-600'
                                                        }`}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                    {review.comment && (
                                        <p className="text-gray-400 font-light">{review.comment}</p>
                                    )}
                                    <p className="text-gray-600 text-sm mt-2">
                                        {new Date(review.created_at || review.createdAt || '').toLocaleDateString('sv-SE')}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}
