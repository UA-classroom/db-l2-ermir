'use client';

import { useState, useEffect } from 'react';
import { useProviderStore } from '@/lib/store/providerStore';
import { Product, ProductCreate, ProductUpdate } from '@/lib/types/product';
import { getProducts, createProduct, updateProduct } from '@/lib/products';
import { Plus, Search, Edit2, Package, Save, X, AlertTriangle } from 'lucide-react';

export default function ProductsPage() {
    const { locations, selectedLocationId, business } = useProviderStore();
    const [products, setProducts] = useState<Product[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);
    const [formData, setFormData] = useState<ProductCreate>({
        location_id: '',
        name: '',
        sku: '',
        price: 0,
        stock_quantity: 0
    });

    // Fetch Products when location changes
    useEffect(() => {
        const fetchProducts = async () => {
            if (!selectedLocationId) return;

            // If selecting all locations, we MUST have the business ID to filter correctly.
            // If business is not loaded yet, wait.
            if (selectedLocationId === 'all' && !business?.id) {
                console.log("WAITING for business ID...");
                return;
            }

            console.log("DEBUG FETCH:", { selectedLocationId, businessId: business?.id });

            setIsLoading(true);
            try {
                // Pass business.id to filter by business if selectedLocationId is 'all'
                const data = await getProducts(selectedLocationId, business?.id);
                setProducts(data);
            } catch (error) {
                console.error("Failed to fetch products:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchProducts();
    }, [selectedLocationId, business]);

    // Reset form when modal opens
    useEffect(() => {
        if (isModalOpen) {
            if (editingProduct) {
                setFormData({
                    location_id: editingProduct.location_id,
                    name: editingProduct.name,
                    sku: editingProduct.sku || '',
                    price: editingProduct.price,
                    stock_quantity: editingProduct.stock_quantity
                });
            } else {
                setFormData({
                    location_id: selectedLocationId || locations[0]?.id || '',
                    name: '',
                    sku: '',
                    price: 0,
                    stock_quantity: 0
                });
            }
        }
    }, [isModalOpen, editingProduct, selectedLocationId, locations]);

    const handleOpenCreate = () => {
        setEditingProduct(null);
        setIsModalOpen(true);
    };

    const handleOpenEdit = (product: Product) => {
        setEditingProduct(product);
        setIsModalOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            if (editingProduct) {
                // Update
                const updateData: ProductUpdate = {
                    name: formData.name,
                    sku: formData.sku,
                    price: Number(formData.price),
                    stock_quantity: Number(formData.stock_quantity)
                };
                await updateProduct(editingProduct.id, updateData);
            } else {
                // Create
                const createData: ProductCreate = {
                    ...formData,
                    price: Number(formData.price),
                    stock_quantity: Number(formData.stock_quantity)
                };
                await createProduct(createData);
            }

            // Refresh list
            const data = await getProducts(selectedLocationId!);
            setProducts(data);
            setIsModalOpen(false);
        } catch (error) {
            console.error("Failed to save product:", error);
            alert("Failed to save product. Check console for details.");
        } finally {
            setIsLoading(false);
        }
    };

    const selectedLocationName = locations.find(l => l.id === selectedLocationId)?.name || 'Selected Location';

    if (!selectedLocationId) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] text-gray-400">
                <Package className="w-16 h-16 mb-4 opacity-50" />
                <h2 className="text-xl font-light">Select a location to manage products</h2>
            </div>
        );
    }

    // Aggregation Logic for "All Locations"
    const isAllLocations = selectedLocationId === 'all';
    let displayProducts = products;

    if (isAllLocations) {
        const grouped = products.reduce((acc, curr) => {
            const key = curr.sku || curr.name; // Use SKU for uniqueness, fallback to Name
            if (!acc[key]) {
                // Initialize with the first product found, but zero stock for accumulation
                acc[key] = { ...curr, stock_quantity: 0 };
            }
            // Add stock
            acc[key].stock_quantity += curr.stock_quantity;
            return acc;
        }, {} as Record<string, Product>);

        displayProducts = Object.values(grouped);
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-light text-white">
                        Products & Inventory
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">
                        Managing inventory for <span className="text-[#d4af37]">{selectedLocationName}</span>
                    </p>
                </div>
                {!isAllLocations && (
                    <button
                        onClick={handleOpenCreate}
                        className="flex items-center gap-2 px-4 py-2 bg-[#d4af37] text-black font-medium rounded-lg hover:bg-[#b5952f] transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        Add Product
                    </button>
                )}
            </div>

            {/* Products Table */}
            <div className="bg-[#1a1a2e] border border-white/5 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/5 bg-white/5">
                                <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">Product Name</th>
                                <th className="text-left py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">SKU</th>
                                <th className="text-right py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">Price (SEK)</th>
                                <th className="text-right py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">Stock</th>
                                <th className="text-right py-4 px-6 text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {displayProducts.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-gray-500">
                                        No products found. Add one to get started.
                                    </td>
                                </tr>
                            ) : (
                                displayProducts.map((product) => (
                                    <tr key={product.id} className="hover:bg-white/5 transition-colors">
                                        <td className="py-4 px-6 text-sm text-white font-medium">{product.name}</td>
                                        <td className="py-4 px-6 text-sm text-gray-400">{product.sku || '-'}</td>
                                        <td className="py-4 px-6 text-sm text-white text-right">{product.price} kr</td>
                                        <td className="py-4 px-6 text-sm text-right">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${product.stock_quantity <= 10
                                                ? 'bg-red-400/10 text-red-400'
                                                : 'bg-green-400/10 text-green-400'
                                                }`}>
                                                {product.stock_quantity}
                                            </span>
                                        </td>
                                        <td className="py-4 px-6 text-right">
                                            {!isAllLocations && (
                                                <button
                                                    onClick={() => handleOpenEdit(product)}
                                                    className="text-gray-400 hover:text-white transition-colors"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl w-full max-w-md shadow-2xl">
                        <form onSubmit={handleSubmit}>
                            <div className="flex items-center justify-between p-6 border-b border-white/5">
                                <h3 className="text-xl font-light text-white">
                                    {editingProduct ? 'Edit Product' : 'Add New Product'}
                                </h3>
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="text-gray-400 hover:text-white"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="p-6 space-y-4">
                                {/* Location (Hidden or Disabled if creating for selected) */}
                                <div>
                                    <label className="block text-xs font-medium text-gray-400 mb-1">Product Name</label>
                                    <input
                                        type="text"
                                        required
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                        className="w-full bg-[#0f0f1a] border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#d4af37]"
                                        placeholder="e.g. Premium Shampoo"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-medium text-gray-400 mb-1">SKU (Optional)</label>
                                        <input
                                            type="text"
                                            value={formData.sku}
                                            onChange={e => setFormData({ ...formData, sku: e.target.value })}
                                            className="w-full bg-[#0f0f1a] border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#d4af37]"
                                            placeholder="PROD-001"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-gray-400 mb-1">Price (SEK)</label>
                                        <input
                                            type="number"
                                            min="0"
                                            step="0.01"
                                            required
                                            value={formData.price}
                                            onChange={e => setFormData({ ...formData, price: Number(e.target.value) })}
                                            className="w-full bg-[#0f0f1a] border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#d4af37]"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-gray-400 mb-1">Stock Quantity</label>
                                    <div className="flex items-center gap-4">
                                        <input
                                            type="number"
                                            min="0"
                                            required
                                            value={formData.stock_quantity}
                                            onChange={e => setFormData({ ...formData, stock_quantity: Number(e.target.value) })}
                                            className="w-full bg-[#0f0f1a] border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#d4af37]"
                                        />
                                        {editingProduct && (
                                            <div className="text-xs text-gray-500">
                                                Update this value to adjust inventory.
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 border-t border-white/5 flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="flex items-center gap-2 px-6 py-2 bg-[#d4af37] text-black font-medium rounded-lg hover:bg-[#b5952f] transition-colors disabled:opacity-50"
                                >
                                    <Save className="w-4 h-4" />
                                    {isLoading ? 'Saving...' : 'Save Product'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

