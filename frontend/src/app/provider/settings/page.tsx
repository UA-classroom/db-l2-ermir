'use client';

import { useState, useEffect } from 'react';
import { useProviderStore } from '@/lib/store/providerStore';
import {
    updateBusiness,
    createLocation,
    updateLocation,
    getLocationContacts,
    createLocationContact,
    updateLocationContact,
    deleteLocationContact,
    getBusinessWithLocations
} from '@/lib/businesses';
import { Save, Plus, MapPin, Phone, Building, Loader2, Trash2, Edit2 } from 'lucide-react';
import { LocationSearchResult, Contact } from '@/lib/types/business';

export default function SettingsPage() {
    const { business, locations: globalLocations, setBusiness, setLocations } = useProviderStore();
    const [activeTab, setActiveTab] = useState<'business' | 'locations'>('business');
    const [isLoading, setIsLoading] = useState(false);

    const handleRefresh = async () => {
        if (!business) return;
        try {
            const data = await getBusinessWithLocations(business.id);
            setBusiness(data);
            setLocations(data.locations);
        } catch (err) {
            console.error("Failed to refresh data", err);
        }
    };

    // Business Form State
    const [businessForm, setBusinessForm] = useState({
        name: '',
        org_number: '',
        slug: ''
    });
    const [isChanged, setIsChanged] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (business) {
            setBusinessForm({
                name: business.name,
                org_number: business.orgNumber || '',
                slug: business.slug
            });
            setIsChanged(false);
        }
    }, [business]);

    useEffect(() => {
        if (business) {
            const hasChanged =
                businessForm.name !== business.name ||
                businessForm.org_number !== (business.orgNumber || '') ||
                businessForm.slug !== business.slug;
            setIsChanged(hasChanged);
        }
    }, [businessForm, business]);

    const handleUpdateBusiness = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!business) return;
        setIsLoading(true);
        try {
            const updatedBusiness = await updateBusiness(business.id, businessForm);
            await handleRefresh(); // Refresh global state
            setIsEditing(false); // Exit edit mode
            alert('Business settings updated!');
        } catch (err) {
            console.error(err);
            alert('Failed to update business settings.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = () => {
        if (business) {
            setBusinessForm({
                name: business.name,
                org_number: business.orgNumber || '',
                slug: business.slug
            });
        }
        setIsEditing(false);
    };

    if (!business) return <div className="p-8 text-center text-gray-400">Loading business settings...</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-20">
            <div>
                <h1 className="text-3xl font-light text-white mb-2">Settings</h1>
                <p className="text-gray-400">Manage your business profile and locations.</p>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-white/10">
                <button
                    onClick={() => setActiveTab('business')}
                    className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'business'
                        ? 'text-[#d4af37] border-[#d4af37]'
                        : 'text-gray-400 border-transparent hover:text-white'
                        }`}
                >
                    Business Profile
                </button>
                <button
                    onClick={() => setActiveTab('locations')}
                    className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'locations'
                        ? 'text-[#d4af37] border-[#d4af37]'
                        : 'text-gray-400 border-transparent hover:text-white'
                        }`}
                >
                    Locations & Contacts
                </button>
            </div>

            {activeTab === 'business' && (
                <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
                    <h2 className="text-xl text-white font-light mb-6 flex items-center gap-2">
                        <Building className="w-5 h-5 text-[#d4af37]" />
                        Business Details
                    </h2>
                    <form onSubmit={handleUpdateBusiness} className="space-y-6 max-w-xl">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Business Name</label>
                            <input
                                type="text"
                                disabled={!isEditing}
                                value={businessForm.name}
                                onChange={e => setBusinessForm({ ...businessForm, name: e.target.value })}
                                className={`w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none ${!isEditing ? 'opacity-50 cursor-default' : ''}`}
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Organization Number (Org.nr)</label>
                            <input
                                type="text"
                                disabled={!isEditing}
                                value={businessForm.org_number}
                                onChange={e => setBusinessForm({ ...businessForm, org_number: e.target.value })}
                                className={`w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none ${!isEditing ? 'opacity-50 cursor-default' : ''}`}
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">URL Slug</label>
                            <div className="flex items-center">
                                <span className={`bg-[#16213e] border border-r-0 border-white/10 rounded-l-lg px-4 py-3 text-gray-400 text-sm ${!isEditing ? 'opacity-50' : ''}`}>
                                    bookning.se/
                                </span>
                                <input
                                    type="text"
                                    disabled={!isEditing}
                                    value={businessForm.slug}
                                    onChange={e => setBusinessForm({ ...businessForm, slug: e.target.value })}
                                    className={`flex-1 bg-[#16213e] border border-white/10 rounded-r-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none ${!isEditing ? 'opacity-50 cursor-default' : ''}`}
                                />
                            </div>
                        </div>

                        <div className="pt-4 flex gap-3">
                            {!isEditing ? (
                                <button
                                    type="button"
                                    onClick={() => setIsEditing(true)}
                                    className="bg-white/10 text-white px-6 py-3 rounded-xl font-medium hover:bg-white/20 transition-colors flex items-center gap-2"
                                >
                                    <Edit2 className="w-5 h-5" />
                                    Edit Details
                                </button>
                            ) : (
                                <>
                                    <button
                                        type="submit"
                                        disabled={isLoading || !isChanged}
                                        className="bg-[#d4af37] text-[#0f0f1a] px-6 py-3 rounded-xl font-medium hover:bg-[#b8960f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                    >
                                        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                                        Save Changes
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleCancel}
                                        className="text-gray-400 px-6 py-3 rounded-xl font-medium hover:text-white transition-colors"
                                    >
                                        Cancel
                                    </button>
                                </>
                            )}
                        </div>
                    </form>
                </div>
            )}

            {activeTab === 'locations' && (
                <LocationsManager locations={globalLocations} businessId={business.id} onRefresh={handleRefresh} />
            )}

        </div>
    );
}

// Sub-component for Location Management
function LocationsManager({ locations, businessId, onRefresh }: { locations: LocationSearchResult[], businessId: string, onRefresh: () => void }) {
    const [isAdding, setIsAdding] = useState(false);

    // Quick Add Form
    const [newLoc, setNewLoc] = useState({ name: '', address: '', city: 'Stockholm' });

    const handleAddLocation = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createLocation(businessId, { ...newLoc, business_id: businessId });
            setNewLoc({ name: '', address: '', city: 'Stockholm' });
            setIsAdding(false);
            onRefresh();
            alert('Location added!');
        } catch (err) {
            console.error(err);
            alert('Failed to add location.');
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl text-white font-light flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-[#d4af37]" />
                    Locations ({locations.length})
                </h2>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-2 text-[#d4af37] hover:bg-[#d4af37]/10 px-4 py-2 rounded-lg transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Add Location
                </button>
            </div>

            {isAdding && (
                <div className="bg-[#1a1a2e] border border-[#d4af37]/30 rounded-2xl p-6 animate-fade-in">
                    <h3 className="text-white mb-4">New Location</h3>
                    <form onSubmit={handleAddLocation} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                            type="text"
                            placeholder="Location Name (e.g. Downtown)"
                            required
                            className="bg-[#16213e] border border-white/10 rounded-lg px-4 py-2 text-white"
                            value={newLoc.name}
                            onChange={e => setNewLoc({ ...newLoc, name: e.target.value })}
                        />
                        <input
                            type="text"
                            placeholder="Address"
                            required
                            className="bg-[#16213e] border border-white/10 rounded-lg px-4 py-2 text-white"
                            value={newLoc.address}
                            onChange={e => setNewLoc({ ...newLoc, address: e.target.value })}
                        />
                        <input
                            type="text"
                            placeholder="City"
                            required
                            className="bg-[#16213e] border border-white/10 rounded-lg px-4 py-2 text-white"
                            value={newLoc.city}
                            onChange={e => setNewLoc({ ...newLoc, city: e.target.value })}
                        />
                        <div className="flex gap-2">
                            <button type="button" onClick={() => setIsAdding(false)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                            <button type="submit" className="flex-1 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium">Create</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid gap-6">
                {locations.map(loc => (
                    <LocationCard key={loc.id} location={loc} onUpdate={onRefresh} />
                ))}
            </div>
        </div>
    );
}

function LocationCard({ location, onUpdate }: { location: LocationSearchResult, onUpdate: () => void }) {
    const [isEditing, setIsEditing] = useState(false);
    const [form, setForm] = useState({ name: location.name, address: location.address, city: location.city });
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [showContacts, setShowContacts] = useState(false);

    // Fetch contacts on toggle
    const toggleContacts = async () => {
        if (!showContacts) {
            try {
                const data = await getLocationContacts(location.id);
                setContacts(data);
            } catch (err) {
                console.error(err);
            }
        }
        setShowContacts(!showContacts);
    };

    const handleSave = async () => {
        try {
            await updateLocation(location.id, form);
            setIsEditing(false);
            onUpdate();
        } catch (err) {
            alert('Failed to update location');
        }
    };

    const handleAddContact = async () => {
        const phone = prompt("Enter phone number:");
        if (!phone) return;
        try {
            await createLocationContact(location.id, {
                location_id: location.id,
                contact_type: 'Phone',
                phone_number: phone
            });
            // Refresh contacts
            const data = await getLocationContacts(location.id);
            setContacts(data);
        } catch (err) {
            alert('Failed to add contact');
        }
    };

    const handleDeleteContact = async (id: number) => {
        if (!confirm("Remove this contact?")) return;
        try {
            await deleteLocationContact(id);
            // Refresh contacts
            const data = await getLocationContacts(location.id);
            setContacts(data);
        } catch (err) {
            alert('Failed to delete contact');
        }
    };

    return (
        <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl overflow-hidden group hover:border-white/10 transition-all">
            <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                    {isEditing ? (
                        <div className="space-y-3 flex-1 mr-4">
                            <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full bg-[#16213e] text-white p-2 rounded" />
                            <input value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} className="w-full bg-[#16213e] text-white p-2 rounded" />
                        </div>
                    ) : (
                        <div>
                            <h3 className="text-lg text-white font-medium">{location.name}</h3>
                            <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
                                <MapPin className="w-3 h-3" />
                                {location.address}, {location.city}
                            </p>
                        </div>
                    )}

                    <div className="flex gap-2">
                        {isEditing ? (
                            <>
                                <button onClick={() => setIsEditing(false)} className="text-gray-500 hover:text-white px-3 py-1">Cancel</button>
                                <button onClick={handleSave} className="bg-[#d4af37] text-black px-3 py-1 rounded">Save</button>
                            </>
                        ) : (
                            <button onClick={() => setIsEditing(true)} className="p-2 text-gray-400 hover:text-white bg-white/5 rounded-lg">
                                <span className="text-xs">Edit</span>
                            </button>
                        )}
                    </div>
                </div>

                <div className="border-t border-white/5 pt-4">
                    <button onClick={toggleContacts} className="text-sm text-[#d4af37] flex items-center gap-2 hover:underline">
                        <Phone className="w-3 h-3" />
                        {showContacts ? 'Hide Contacts' : 'Manage Contacts'}
                    </button>

                    {showContacts && (
                        <div className="mt-4 space-y-2 bg-[#16213e]/50 p-4 rounded-xl">
                            {contacts.map(c => (
                                <div key={c.id} className="flex justify-between items-center text-sm">
                                    <span className="text-gray-300">{c.contactType}: {c.phoneNumber}</span>
                                    <button onClick={() => handleDeleteContact(c.id)} className="text-red-400 hover:text-red-300"><Trash2 className="w-3 h-3" /></button>
                                </div>
                            ))}
                            {contacts.length === 0 && <p className="text-gray-500 text-xs text-center">No contacts listed.</p>}
                            <button onClick={handleAddContact} className="w-full mt-2 py-2 border border-dashed border-white/20 text-gray-400 text-xs rounded hover:text-white hover:border-white/40">
                                + Add Phone Number
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
