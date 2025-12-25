'use client';

import { useState, useEffect } from 'react';
import { X, Plus, Trash2, Clock, DollarSign, Check } from 'lucide-react';
import {
    Service,
    ServiceVariant,
    Category,
    createService,
    updateService,
    createServiceVariant,
    updateServiceVariant,
    deleteServiceVariant,
    getCategories
} from '@/lib/services';

interface ServiceModalProps {
    service: Service | null;
    businessId: string; // Passed from parent to link new service
    onClose: () => void;
    onSave: () => void;
}

export default function ServiceModal({ service, businessId, onClose, onSave }: ServiceModalProps) {
    const [categories, setCategories] = useState<Category[]>([]);
    const [activeTab, setActiveTab] = useState<'details' | 'variants'>('details');
    const [isLoading, setIsLoading] = useState(false);

    // Service Form State
    const [formData, setFormData] = useState({
        name: service?.name || '',
        description: service?.description || '',
        category_id: service?.category_id?.toString() || '',
        is_active: service?.is_active ?? true,
    });

    // Variant Form State (for adding new variants)
    const [isAddingVariant, setIsAddingVariant] = useState(false);
    const [variantData, setVariantData] = useState({
        name: '',
        price: '',
        duration_minutes: '30',
    });

    useEffect(() => {
        loadCategories();
    }, []);

    const loadCategories = async () => {
        try {
            const data = await getCategories();
            setCategories(data);
        } catch (err) {
            console.error('Error loading categories:', err);
        }
    };

    const handleSaveService = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            if (service) {
                await updateService(service.id, {
                    name: formData.name,
                    description: formData.description,
                    category_id: formData.category_id ? parseInt(formData.category_id) : null,
                    is_active: formData.is_active,
                });
            } else {
                await createService({
                    business_id: businessId,
                    name: formData.name,
                    description: formData.description,
                    category_id: formData.category_id ? parseInt(formData.category_id) : null,
                    is_active: formData.is_active,
                });
            }
            onSave();
        } catch (err) {
            console.error('Error saving service:', err);
            alert('Failed to save service');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddVariant = async () => {
        if (!service) return; // Should not happen if UI is correct

        try {
            await createServiceVariant({
                service_id: service.id,
                name: variantData.name,
                price: parseFloat(variantData.price),
                duration_minutes: parseInt(variantData.duration_minutes),
            });
            setVariantData({ name: '', price: '', duration_minutes: '30' });
            setIsAddingVariant(false);
            onSave(); // Refresh parent
        } catch (err) {
            console.error('Error adding variant:', err);
            alert('Failed to add variant');
        }
    };

    const handleDeleteVariant = async (variantId: string) => {
        if (!confirm('Delete this variant?')) return;
        try {
            await deleteServiceVariant(variantId);
            onSave(); // Refresh parent
        } catch (err) {
            console.error('Error deleting variant:', err);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl w-full max-w-2xl shadow-xl flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-white/5">
                    <h2 className="text-xl font-light text-white">
                        {service ? `Edit ${service.name}` : 'New Service'}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tabs */}
                {service && (
                    <div className="flex border-b border-white/5 px-6">
                        <button
                            onClick={() => setActiveTab('details')}
                            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'details'
                                    ? 'text-[#d4af37] border-[#d4af37]'
                                    : 'text-gray-400 border-transparent hover:text-white'
                                }`}
                        >
                            Details
                        </button>
                        <button
                            onClick={() => setActiveTab('variants')}
                            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'variants'
                                    ? 'text-[#d4af37] border-[#d4af37]'
                                    : 'text-gray-400 border-transparent hover:text-white'
                                }`}
                        >
                            Variants ({service.variants.length})
                        </button>
                    </div>
                )}

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1">
                    {activeTab === 'details' ? (
                        <form id="service-form" onSubmit={handleSaveService} className="space-y-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Service Name</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                    placeholder="e.g. Haircut"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Category</label>
                                <select
                                    value={formData.category_id}
                                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                                    className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50"
                                >
                                    <option value="">Select a category...</option>
                                    {categories.map((cat) => (
                                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full px-4 py-2 bg-[#16213e] border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#d4af37]/50 h-24 resize-none"
                                />
                            </div>

                            <div className="flex items-center gap-2 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setFormData({ ...formData, is_active: !formData.is_active })}
                                    className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${formData.is_active
                                            ? 'bg-[#d4af37] border-[#d4af37]'
                                            : 'border-gray-500 bg-transparent'
                                        }`}
                                >
                                    {formData.is_active && <Check className="w-3 h-3 text-[#0f0f1a]" />}
                                </button>
                                <span className="text-gray-400 text-sm">Active (visible to customers)</span>
                            </div>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            {/* Add Variant Form */}
                            {isAddingVariant ? (
                                <div className="bg-[#16213e]/50 p-4 rounded-xl border border-white/10 space-y-3">
                                    <div className="flex justify-between items-center mb-2">
                                        <h3 className="text-sm font-medium text-white">New Variant</h3>
                                        <button onClick={() => setIsAddingVariant(false)} className="text-gray-400 hover:text-white">
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Variant Name (e.g. Long Hair)"
                                        className="w-full px-3 py-2 bg-[#0f0f1a] rounded-lg text-white border border-white/10 text-sm"
                                        value={variantData.name}
                                        onChange={(e) => setVariantData({ ...variantData, name: e.target.value })}
                                    />
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="relative">
                                            <DollarSign className="absolute left-2 top-2.5 w-3 h-3 text-gray-500" />
                                            <input
                                                type="number"
                                                placeholder="Price"
                                                className="w-full pl-7 pr-3 py-2 bg-[#0f0f1a] rounded-lg text-white border border-white/10 text-sm"
                                                value={variantData.price}
                                                onChange={(e) => setVariantData({ ...variantData, price: e.target.value })}
                                            />
                                        </div>
                                        <div className="relative">
                                            <Clock className="absolute left-2 top-2.5 w-3 h-3 text-gray-500" />
                                            <input
                                                type="number"
                                                placeholder="Minutes"
                                                className="w-full pl-7 pr-3 py-2 bg-[#0f0f1a] rounded-lg text-white border border-white/10 text-sm"
                                                value={variantData.duration_minutes}
                                                onChange={(e) => setVariantData({ ...variantData, duration_minutes: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                    <button
                                        onClick={handleAddVariant}
                                        className="w-full py-2 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium text-sm hover:bg-[#b8960f]"
                                    >
                                        Add Variant
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={() => setIsAddingVariant(true)}
                                    className="w-full py-3 border border-dashed border-white/20 rounded-xl text-gray-400 hover:text-white hover:border-white/40 transition-all flex items-center justify-center gap-2"
                                >
                                    <Plus className="w-4 h-4" /> Add Variant
                                </button>
                            )}

                            {/* List Variants */}
                            <div className="space-y-2">
                                {service?.variants.map((variant) => (
                                    <div key={variant.id} className="flex justify-between items-center p-3 bg-[#16213e]/30 rounded-lg border border-white/5">
                                        <div>
                                            <p className="text-white text-sm">{variant.name}</p>
                                            <p className="text-xs text-gray-500">
                                                {variant.duration_minutes} min • ${variant.price}
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteVariant(variant.id)}
                                            className="p-2 text-gray-500 hover:text-red-400 transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/5 flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2 bg-[#16213e] text-white rounded-lg hover:bg-[#16213e]/80 transition-colors"
                    >
                        Close
                    </button>
                    {activeTab === 'details' && (
                        <button
                            form="service-form"
                            type="submit"
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium rounded-lg hover:shadow-lg disabled:opacity-50"
                        >
                            {isLoading ? 'Saving...' : (service ? 'Update Service' : 'Create Service')}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
