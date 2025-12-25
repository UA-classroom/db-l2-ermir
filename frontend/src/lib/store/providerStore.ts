import { create } from 'zustand';
import { Business, LocationSearchResult } from '../types/business';

interface ProviderState {
    business: Business | null;
    locations: LocationSearchResult[]; // Using LocationSearchResult as it has more details
    selectedLocationId: string; // 'all' or specific UUID
    isLoading: boolean;

    setBusiness: (business: Business) => void;
    setLocations: (locations: LocationSearchResult[]) => void;
    setSelectedLocationId: (id: string) => void;
    setLoading: (loading: boolean) => void;
    reset: () => void;

    // Computed helpers could be done here or in hooks, sticking to state for now
}

export const useProviderStore = create<ProviderState>((set) => ({
    business: null,
    locations: [],
    selectedLocationId: 'all',
    isLoading: true,

    setBusiness: (business) => set({ business }),
    setLocations: (locations) => set({ locations }),
    setSelectedLocationId: (id) => set({ selectedLocationId: id }),
    setLoading: (loading) => set({ isLoading: loading }),

    reset: () => set({
        business: null,
        locations: [],
        selectedLocationId: 'all',
        isLoading: true
    }),
}));
