'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { getLocation, getLocationServices, getLocationImages } from '@/lib/businesses';
import { getAvailableSlots, createBooking, TimeSlot } from '@/lib/bookings';
import { getLocationEmployees, Employee } from '@/lib/employees';
import { LocationSearchResult } from '@/lib/types/business';
import { Navbar } from '@/components/common';
import { Check } from 'lucide-react';

interface Service {
    id: string;
    name: string;
    description?: string;
    variants: ServiceVariant[];
}

interface ServiceVariant {
    id: string;
    name: string;
    price: number;
    durationMinutes?: number;
    duration_minutes?: number; // Backend snake_case
}

type BookingStep = 'service' | 'datetime' | 'confirm';

export default function BookingPage() {
    const params = useParams();
    const router = useRouter();
    const locationId = params.id as string;

    const { user, isAuthenticated } = useAuthStore();

    // Data states
    const [location, setLocation] = useState<LocationSearchResult | null>(null);
    const [locationImages, setLocationImages] = useState<{ id: string, image_url: string, is_primary: boolean }[]>([]);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [services, setServices] = useState<Service[]>([]);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);

    // Selection states
    const [selectedVariant, setSelectedVariant] = useState<ServiceVariant | null>(null);
    const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);  // null = any employee
    const [selectedDate, setSelectedDate] = useState<string>('');
    const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
    const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
    const [note, setNote] = useState('');
    const [dateOffset, setDateOffset] = useState(0); // Week offset for date navigation

    // UI states
    const [step, setStep] = useState<BookingStep>('service');
    const [expandedVariantId, setExpandedVariantId] = useState<string | null>(null);  // For accordion
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (locationId) {
            loadLocationData();
        }
    }, [locationId]);

    useEffect(() => {
        if (selectedVariant && selectedDate) {
            loadSlots();
        }
    }, [selectedVariant, selectedDate, selectedEmployee]);

    const loadLocationData = async () => {
        setIsLoading(true);
        try {
            // First get location to obtain businessId
            const locationData = await getLocation(locationId);
            setLocation(locationData);

            // Then fetch services using businessId (services belong to business, not location)
            if (locationData.businessId) {
                const serviceData = await getLocationServices(locationData.businessId).catch(() => []);
                setServices(serviceData);
            }

            // Fetch employees for this location
            const employeeData = await getLocationEmployees(locationId).catch(() => []);
            setEmployees(employeeData);
            console.log(`[DEBUG] Location ${locationId} has ${employeeData.length} employees:`, employeeData);

            // Fetch location images for carousel
            const imagesData = await getLocationImages(locationId).catch(() => []);
            setLocationImages(imagesData);
        } catch (err) {
            console.error('Error loading location:', err);
            setError('Failed to load location');
        } finally {
            setIsLoading(false);
        }
    };

    const loadSlots = async () => {
        if (!selectedVariant || !selectedDate) return;
        try {
            const slots = await getAvailableSlots(
                selectedDate,
                selectedVariant.id,
                locationId,
                selectedEmployee?.id  // Pass employee ID if specific employee selected
            );
            setAvailableSlots(slots);
            console.log(`[DEBUG] Loaded ${slots.length} slots for date ${selectedDate}`);
        } catch (err) {
            console.error('Error loading slots:', err);
            setAvailableSlots([]);
        }
    };

    const handleSelectVariant = (variant: ServiceVariant) => {
        // Toggle expanded state for accordion
        if (expandedVariantId === variant.id) {
            setExpandedVariantId(null);
        } else {
            setExpandedVariantId(variant.id);
        }
    };

    const handleSelectEmployeeForVariant = (variant: ServiceVariant, employee: Employee | null) => {
        setSelectedVariant(variant);
        setSelectedEmployee(employee);
        if (employee) {
            setSelectedEmployeeId(employee.id);
        }
        setStep('datetime');
        // Set default date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        setSelectedDate(tomorrow.toISOString().split('T')[0]);
    };

    // Helper to get price for employee/variant combo
    const getEmployeePrice = (employee: Employee, variantId: string, basePrice: number): number => {
        const skill = employee.skills?.find(s => s.service_variant_id === variantId);
        return skill?.custom_price ?? basePrice;
    };

    // Get employees who can perform a specific variant
    const getCapableEmployees = (variantId: string): Employee[] => {
        return employees.filter(emp =>
            emp.skills?.some(s => s.service_variant_id === variantId)
        );
    };

    const handleSelectSlot = (slot: TimeSlot) => {
        setSelectedSlot(slot);

        // If user already selected a specific employee, use them
        if (selectedEmployee) {
            setSelectedEmployeeId(selectedEmployee.id);
        } else {
            // "Any Available" - pick the first available employee from this slot
            const empIds = slot.employee_ids || slot.availableEmployeeIds || [];
            if (empIds.length > 0) {
                setSelectedEmployeeId(empIds[0]);
            }
        }
        setStep('confirm');
    };

    const handleConfirmBooking = async () => {
        if (!selectedVariant || !selectedSlot || !selectedEmployeeId) return;

        if (!isAuthenticated) {
            // Redirect to login
            router.push(`/login?redirect=/book/${locationId}`);
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            // Calculate end time from start time + duration
            const startTime = selectedSlot.start_time || selectedSlot.startTime || '';
            const startDate = new Date(startTime);
            const duration = selectedVariant.durationMinutes || selectedVariant.duration_minutes || 0;
            const endDate = new Date(startDate.getTime() + duration * 60 * 1000);

            // Send as UTC - backend will convert to Stockholm timezone
            await createBooking({
                customerId: user!.id,
                locationId,
                serviceVariantId: selectedVariant.id,
                employeeId: selectedEmployeeId,
                startTime: startDate.toISOString(),
                endTime: endDate.toISOString(),
                customerNote: note || undefined,
            });

            // Success! Redirect to bookings
            router.push('/bookings?success=true');
        } catch (err: any) {
            console.error('Error creating booking:', err);
            setError(err.response?.data?.detail || 'Failed to create booking');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Generate date options (14 days starting from offset)
    const dateOptions = Array.from({ length: 14 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() + i + 1 + (dateOffset * 14));
        return date.toISOString().split('T')[0];
    });

    // Get month/year label for current date range
    const getDateRangeLabel = () => {
        if (dateOptions.length === 0) return '';
        const startDate = new Date(dateOptions[0]);
        const endDate = new Date(dateOptions[dateOptions.length - 1]);
        const startMonth = startDate.toLocaleDateString('en-US', { month: 'short' });
        const endMonth = endDate.toLocaleDateString('en-US', { month: 'short' });
        if (startMonth === endMonth) {
            return `${startMonth} ${startDate.getFullYear()}`;
        }
        return `${startMonth} - ${endMonth} ${endDate.getFullYear()}`;
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

    if (error && !location) {
        return (
            <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400 mb-4">{error}</p>
                    <Link href="/browse" className="text-[#d4af37] hover:underline">
                        ← Back to Browse
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f0f1a]">
            {/* Navigation */}
            <Navbar />

            <div className="pt-28 pb-16 max-w-4xl mx-auto px-6 lg:px-8">
                {/* Progress Steps */}
                <div className="flex items-center justify-center gap-4 mb-12">
                    {['service', 'datetime', 'confirm'].map((s, idx) => (
                        <div key={s} className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center font-light transition-all ${step === s
                                    ? 'bg-[#d4af37] text-[#0f0f1a]'
                                    : idx < ['service', 'datetime', 'confirm'].indexOf(step)
                                        ? 'bg-green-500 text-white'
                                        : 'bg-[#1a1a2e] text-gray-500'
                                    }`}
                            >
                                {idx < ['service', 'datetime', 'confirm'].indexOf(step) ? <Check className="w-4 h-4" /> : idx + 1}
                            </div>
                            {idx < 2 && (
                                <div
                                    className={`w-12 h-0.5 ${idx < ['service', 'datetime', 'confirm'].indexOf(step)
                                        ? 'bg-green-500'
                                        : 'bg-[#1a1a2e]'
                                        }`}
                                />
                            )}
                        </div>
                    ))}
                </div>

                {/* Location Info */}
                {location && (
                    <div className="text-center mb-6">
                        <p className="text-[#d4af37] text-sm font-light mb-2">{location.businessName}</p>
                        <h1 className="text-2xl font-light text-white mb-4">{location.name}</h1>
                    </div>
                )}

                {/* Image Carousel */}
                {locationImages.length > 0 && (
                    <div className="relative mb-8 rounded-xl overflow-hidden">
                        <div className="aspect-[16/9] relative">
                            <img
                                src={locationImages[currentImageIndex]?.image_url || '/placeholder.jpg'}
                                alt={`${location?.name || 'Location'} image ${currentImageIndex + 1}`}
                                className="w-full h-full object-cover"
                            />
                            {/* Image Counter */}
                            <div className="absolute bottom-4 right-4 bg-black/50 px-3 py-1 rounded-full text-white text-sm">
                                {currentImageIndex + 1} / {locationImages.length}
                            </div>
                        </div>

                        {/* Navigation Arrows */}
                        {locationImages.length > 1 && (
                            <>
                                <button
                                    onClick={() => setCurrentImageIndex((prev) => (prev === 0 ? locationImages.length - 1 : prev - 1))}
                                    className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors"
                                >
                                    ←
                                </button>
                                <button
                                    onClick={() => setCurrentImageIndex((prev) => (prev === locationImages.length - 1 ? 0 : prev + 1))}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors"
                                >
                                    →
                                </button>
                            </>
                        )}

                        {/* Dots */}
                        {locationImages.length > 1 && (
                            <div className="flex justify-center gap-2 mt-3">
                                {locationImages.map((_, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setCurrentImageIndex(idx)}
                                        className={`w-2 h-2 rounded-full transition-colors ${idx === currentImageIndex ? 'bg-[#d4af37]' : 'bg-gray-500'}`}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Warning: No employees at this location */}
                {!isLoading && employees.length === 0 && (
                    <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-400 text-center">
                        <p className="font-medium">⚠️ No staff available at this location</p>
                        <p className="text-sm mt-1">This location has no active employees. Booking is not possible.</p>
                    </div>
                )}

                {/* Step 1: Select Service */}
                {step === 'service' && (
                    <div>
                        <h2 className="text-xl font-light text-white mb-6 text-center">Select a Service</h2>
                        {services.length === 0 ? (
                            <p className="text-center text-gray-500">No services available</p>
                        ) : (
                            <div className="space-y-4">
                                {services.map((service) => (
                                    <div
                                        key={service.id}
                                        className="bg-[#1a1a2e]/50 border border-white/5 rounded-xl p-6"
                                    >
                                        <h3 className="text-lg font-light text-white mb-2">{service.name}</h3>
                                        {service.description && (
                                            <p className="text-gray-500 text-sm mb-4">{service.description}</p>
                                        )}
                                        {service.variants?.map((variant) => {
                                            const capableEmps = getCapableEmployees(variant.id);
                                            const isExpanded = expandedVariantId === variant.id;

                                            return (
                                                <div key={variant.id} className="mt-2">
                                                    {/* Variant header - click to expand */}
                                                    <button
                                                        onClick={() => handleSelectVariant(variant)}
                                                        className={`w-full flex justify-between items-center p-4 rounded-lg border transition-all ${isExpanded
                                                            ? 'border-[#d4af37]/50 bg-[#16213e]/50'
                                                            : 'border-white/5 hover:border-[#d4af37]/30 hover:bg-[#16213e]/30'
                                                            } group`}
                                                    >
                                                        <div>
                                                            <span className={`${isExpanded ? 'text-[#d4af37]' : 'text-white group-hover:text-[#d4af37]'} transition-colors`}>
                                                                {variant.name}
                                                            </span>
                                                            <span className="text-gray-500 text-sm ml-2">
                                                                ({variant.durationMinutes || variant.duration_minutes} min)
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-[#d4af37] font-medium">from {variant.price} kr</span>
                                                            <span className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>▼</span>
                                                        </div>
                                                    </button>

                                                    {/* Expanded employee list */}
                                                    {isExpanded && (
                                                        <div className="mt-2 ml-4 space-y-2">
                                                            {/* Any Available option */}
                                                            <button
                                                                onClick={() => handleSelectEmployeeForVariant(variant, null)}
                                                                className="w-full p-3 rounded-lg border border-white/10 hover:border-[#d4af37]/50 hover:bg-[#16213e]/50 transition-all flex items-center gap-3 group"
                                                            >
                                                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#d4af37]/20 to-[#d4af37]/5 flex items-center justify-center">
                                                                    <span className="text-[#d4af37]">★</span>
                                                                </div>
                                                                <div className="flex-1 text-left">
                                                                    <p className="text-white text-sm group-hover:text-[#d4af37] transition-colors">Any Available</p>
                                                                </div>
                                                                <span className="text-[#d4af37] font-medium">{variant.price} kr</span>
                                                            </button>

                                                            {/* Individual employees who can perform this service */}
                                                            {capableEmps.map((emp) => {
                                                                const empPrice = getEmployeePrice(emp, variant.id, variant.price);
                                                                const fullName = emp.first_name && emp.last_name
                                                                    ? `${emp.first_name} ${emp.last_name}`
                                                                    : emp.job_title || 'Specialist';
                                                                const initials = emp.first_name?.charAt(0).toUpperCase() || emp.job_title?.charAt(0) || 'E';

                                                                return (
                                                                    <button
                                                                        key={emp.id}
                                                                        onClick={() => handleSelectEmployeeForVariant(variant, emp)}
                                                                        className="w-full p-3 rounded-lg border border-white/10 hover:border-[#d4af37]/50 hover:bg-[#16213e]/50 transition-all flex items-center gap-3 group"
                                                                    >
                                                                        <div
                                                                            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium"
                                                                            style={{ backgroundColor: emp.color_code || '#6366f1' }}
                                                                        >
                                                                            {initials}
                                                                        </div>
                                                                        <div className="flex-1 text-left">
                                                                            <p className="text-white text-sm group-hover:text-[#d4af37] transition-colors">{fullName}</p>
                                                                            {emp.job_title && <p className="text-gray-500 text-xs">{emp.job_title}</p>}
                                                                        </div>
                                                                        <span className="text-[#d4af37] font-medium">{empPrice} kr</span>
                                                                    </button>
                                                                );
                                                            })}

                                                            {capableEmps.length === 0 && (
                                                                <p className="text-gray-500 text-sm text-center py-2">No specialists available for this service</p>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Step 2: Select Date & Time */}
                {step === 'datetime' && selectedVariant && (
                    <div>
                        <button
                            onClick={() => setStep('service')}
                            className="text-gray-400 hover:text-white text-sm mb-6 inline-flex items-center gap-2"
                        >
                            ← Change service
                        </button>

                        <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-xl p-6 mb-6">
                            <div className="flex justify-between items-center">
                                <div>
                                    <p className="text-gray-500 text-sm mb-1">Selected Service</p>
                                    <p className="text-white font-light">{selectedVariant.name}</p>
                                    <p className="text-[#d4af37]">{selectedVariant.price} kr • {selectedVariant.durationMinutes || selectedVariant.duration_minutes} min</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-gray-500 text-sm mb-1">Specialist</p>
                                    <p className="text-white font-light">
                                        {selectedEmployee
                                            ? (selectedEmployee.first_name && selectedEmployee.last_name
                                                ? `${selectedEmployee.first_name} ${selectedEmployee.last_name}`
                                                : selectedEmployee.job_title)
                                            : 'Any Available'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-light text-white">Select Date</h2>
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => setDateOffset(Math.max(0, dateOffset - 1))}
                                    disabled={dateOffset === 0}
                                    className={`p-2 rounded-lg border transition-all ${dateOffset === 0
                                        ? 'border-white/5 text-gray-600 cursor-not-allowed'
                                        : 'border-white/10 text-gray-400 hover:border-[#d4af37]/30 hover:text-white'
                                        }`}
                                >
                                    ←
                                </button>
                                <span className="text-gray-400 text-sm min-w-[100px] text-center">
                                    {getDateRangeLabel()}
                                </span>
                                <button
                                    onClick={() => setDateOffset(dateOffset + 1)}
                                    className="p-2 rounded-lg border border-white/10 text-gray-400 hover:border-[#d4af37]/30 hover:text-white transition-all"
                                >
                                    →
                                </button>
                            </div>
                        </div>
                        <div className="grid grid-cols-4 md:grid-cols-7 gap-2 mb-8">
                            {dateOptions.map((date) => {
                                const d = new Date(date);
                                const isSelected = date === selectedDate;
                                return (
                                    <button
                                        key={date}
                                        onClick={() => {
                                            setSelectedDate(date);
                                            setSelectedSlot(null);
                                        }}
                                        className={`p-3 rounded-lg border transition-all ${isSelected
                                            ? 'bg-[#d4af37] border-[#d4af37] text-[#0f0f1a]'
                                            : 'border-white/10 text-gray-400 hover:border-[#d4af37]/30 hover:text-white'
                                            }`}
                                    >
                                        <div className="text-xs">{d.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                                        <div className="text-lg font-light">{d.getDate()}</div>
                                    </button>
                                );
                            })}
                        </div>

                        <h2 className="text-xl font-light text-white mb-6">Select Time</h2>
                        {availableSlots.length === 0 ? (
                            <div className="text-center py-8">
                                <p className="text-gray-500 mb-2">No available times on this date</p>
                                {employees.length > 0 && (
                                    <p className="text-gray-600 text-sm">
                                        Staff may not be working on {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long' })}.
                                        Try selecting a different date.
                                    </p>
                                )}
                            </div>
                        ) : (
                            <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                                {availableSlots.map((slot, idx) => {
                                    const slotTime = slot.start_time || slot.startTime || '';
                                    const time = new Date(slotTime);
                                    const isSelected = (selectedSlot?.start_time || selectedSlot?.startTime) === slotTime;
                                    return (
                                        <button
                                            key={idx}
                                            onClick={() => handleSelectSlot(slot)}
                                            className={`p-3 rounded-lg border transition-all ${isSelected
                                                ? 'bg-[#d4af37] border-[#d4af37] text-[#0f0f1a]'
                                                : 'border-white/10 text-gray-400 hover:border-[#d4af37]/30 hover:text-white'
                                                }`}
                                        >
                                            {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}

                {/* Step 3: Confirm */}
                {step === 'confirm' && selectedVariant && selectedSlot && (
                    <div>
                        <button
                            onClick={() => setStep('datetime')}
                            className="text-gray-400 hover:text-white text-sm mb-6 inline-flex items-center gap-2"
                        >
                            ← Change time
                        </button>

                        <h2 className="text-xl font-light text-white mb-6 text-center">Confirm Your Booking</h2>

                        <div className="bg-[#1a1a2e]/50 border border-white/5 rounded-xl p-8 mb-8">
                            {/* Summary */}
                            <div className="space-y-4 mb-8">
                                <div className="flex justify-between pb-4 border-b border-white/5">
                                    <span className="text-gray-500">Service</span>
                                    <span className="text-white">{selectedVariant.name}</span>
                                </div>
                                <div className="flex justify-between pb-4 border-b border-white/5">
                                    <span className="text-gray-500">Duration</span>
                                    <span className="text-white">{selectedVariant.durationMinutes || selectedVariant.duration_minutes} min</span>
                                </div>
                                <div className="flex justify-between pb-4 border-b border-white/5">
                                    <span className="text-gray-500">Date & Time</span>
                                    <span className="text-white">
                                        {new Date(selectedSlot.start_time || selectedSlot.startTime || '').toLocaleDateString('en-US', {
                                            weekday: 'short',
                                            month: 'short',
                                            day: 'numeric',
                                        })}
                                        {' at '}
                                        {new Date(selectedSlot.start_time || selectedSlot.startTime || '').toLocaleTimeString('en-US', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                        })}
                                    </span>
                                </div>
                                <div className="flex justify-between pt-2">
                                    <span className="text-white font-medium">Total</span>
                                    <span className="text-[#d4af37] text-xl font-medium">{selectedVariant.price} kr</span>
                                </div>
                            </div>

                            {/* Note */}
                            <div className="mb-6">
                                <label className="block text-gray-500 text-sm mb-2">Add a note (optional)</label>
                                <textarea
                                    value={note}
                                    onChange={(e) => setNote(e.target.value)}
                                    placeholder="Any special requests..."
                                    rows={3}
                                    className="w-full px-4 py-3 bg-[#16213e]/50 border border-white/10 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                />
                            </div>

                            {/* Error */}
                            {error && (
                                <div className="p-4 mb-6 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            {/* Login Prompt */}
                            {!isAuthenticated && (
                                <div className="p-4 mb-6 bg-[#d4af37]/10 border border-[#d4af37]/30 rounded-lg text-[#d4af37] text-sm text-center">
                                    Please sign in to complete your booking
                                </div>
                            )}

                            {/* Confirm Button */}
                            <button
                                onClick={handleConfirmBooking}
                                disabled={isSubmitting}
                                className="w-full py-4 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <div className="w-5 h-5 border-2 border-[#0f0f1a] border-t-transparent rounded-full animate-spin"></div>
                                        Processing...
                                    </span>
                                ) : isAuthenticated ? (
                                    'Confirm Booking'
                                ) : (
                                    'Sign In to Book'
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
