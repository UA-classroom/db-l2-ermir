
'use client';

import { useProviderStore } from '@/lib/store/providerStore';
import { MapPin, Building2 } from 'lucide-react';

export function LocationSelector() {
    const { locations, selectedLocationId, setSelectedLocationId, business } = useProviderStore();

    if (!business || locations.length === 0) {
        return null; // Don't show if no data loaded yet
    }

    return (
        <div className="flex items-center gap-2 bg-[#1a1a2e] border border-white/10 rounded-lg px-3 py-1.5 min-w-[200px]">
            {selectedLocationId === 'all' ? (
                <Building2 className="w-4 h-4 text-[#d4af37]" />
            ) : (
                <MapPin className="w-4 h-4 text-[#d4af37]" />
            )}

            <select
                value={selectedLocationId}
                onChange={(e) => setSelectedLocationId(e.target.value)}
                className="bg-transparent text-sm text-white focus:outline-none w-full cursor-pointer appearance-none"
                aria-label="Select Location"
            >
                <option value="all" className="bg-[#1a1a2e] text-white">
                    All Locations
                </option>
                <option disabled className="bg-[#1a1a2e] text-gray-500">
                    ──────────
                </option>
                {locations.map((loc) => (
                    <option key={loc.id} value={loc.id} className="bg-[#1a1a2e] text-white">
                        {loc.name}
                    </option>
                ))}
            </select>
        </div>
    );
}
