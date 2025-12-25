'use client';

import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Clock, DollarSign, Store, AlertCircle } from 'lucide-react';
import { getLocationServices, getCategories } from '@/lib/businesses';
import { Service, Category } from '@/lib/types/business';
import { useAuthStore } from '@/lib/store';
import { useProviderStore } from '@/lib/store/providerStore';
import ServiceModal from './ServiceModal';

export default function ServicesPage() {
    const { user } = useAuthStore();
    const { business, isLoading: isGlobalLoading } = useProviderStore();

    const [services, setServices] = useState<Service[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [isLoadingServices, setIsLoadingServices] = useState(false);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingService, setEditingService] = useState<Service | undefined>(undefined);

    useEffect(() => {
        if (business?.id) {
            loadServices();
        }
    }, [business?.id]);

    const loadServices = async () => {
        if (!business) return;
        setIsLoadingServices(true);
        try {
            // 1. Load services for this business
            const servicesData = await getLocationServices(business.id);
            setServices(servicesData);

            // 2. Load categories (for modal)
            const categoriesData = await getCategories();
            setCategories(categoriesData);
        } catch (err) {
            console.error('Error loading services:', err);
        } finally {
            setIsLoadingServices(false);
        }
    };

    const handleSaveService = async () => {
        if (business) {
            const updated = await getLocationServices(business.id);
            setServices(updated);
        }
        setIsModalOpen(false);
    };

    const handleEdit = (service: Service) => {
        setEditingService(service);
        setIsModalOpen(true);
    };

    const handleAdd = () => {
        setEditingService(undefined);
        setIsModalOpen(true);
    };

    if (isGlobalLoading || (business && isLoadingServices && services.length === 0)) {
        return (
            <div className="flex justify-center py-12">
                <div className="w-8 h-8 border-2 border-[#d4af37] border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!business) {
        return (
            <div className="text-center py-12 bg-[#1a1a2e] border border-white/5 rounded-2xl">
                <div className="w-16 h-16 bg-[#d4af37]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Store className="w-8 h-8 text-[#d4af37]" />
                </div>
                <h2 className="text-xl text-white font-light mb-2">No Business Found</h2>
                <p className="text-gray-400 mb-6">We couldn't load your business profile.</p>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-light text-white mb-2">My Services</h1>
                    <p className="text-gray-400">Manage menu for <span className="text-[#d4af37]">{business.name}</span></p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-blue-400 bg-blue-400/10 px-2 py-1 rounded inline-flex">
                        <AlertCircle className="w-3 h-3" />
                        Services are applied to all locations by default
                    </div>
                </div>
                <button
                    onClick={handleAdd}
                    className="flex items-center gap-2 px-4 py-2 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium hover:bg-[#b8960f] transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    <span>Add Service</span>
                </button>
            </div>

            {services.length === 0 ? (
                <div className="text-center py-12 bg-[#1a1a2e] border border-white/5 rounded-2xl">
                    <p className="text-gray-400 mb-4">No services found.</p>
                    <p className="text-sm text-gray-500">Add your first service to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {services.map((service) => (
                        <div key={service.id} className="bg-[#1a1a2e] border border-white/5 rounded-2xl overflow-hidden group hover:border-[#d4af37]/30 transition-all">
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-xl text-white font-light mb-1">{service.name}</h3>
                                        {/* TODO: Show category logic if we map ID to name */}
                                        {service.description && (
                                            <p className="text-gray-400 text-sm line-clamp-2">{service.description}</p>
                                        )}
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleEdit(service)}
                                            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                                        >
                                            <Edit2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>

                                {/* Variants */}
                                <div className="space-y-3 mt-4 pt-4 border-t border-white/5">
                                    {service.variants?.map((variant) => (
                                        <div key={variant.id} className="flex justify-between items-center p-3 bg-[#16213e]/50 rounded-xl">
                                            <span className="text-gray-300 text-sm">{variant.name}</span>
                                            <div className="flex items-center gap-4 text-sm">
                                                <div className="flex items-center gap-1 text-gray-400">
                                                    <Clock className="w-3 h-3" />
                                                    <span>{variant.duration_minutes}m</span>
                                                </div>
                                                <div className="flex items-center gap-1 text-[#d4af37]">
                                                    <DollarSign className="w-3 h-3" />
                                                    <span>{variant.price}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {isModalOpen && (
                <ServiceModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSaveService}
                    serviceToEdit={editingService}
                    businessId={business.id}
                    categories={categories}
                />
            )}
        </div>
    );
}
