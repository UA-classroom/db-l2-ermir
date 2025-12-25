'use client';

import { useProviderStore } from '@/lib/store/providerStore';
import { Calendar as CalendarIcon, AlertTriangle } from 'lucide-react';

export default function CalendarPage() {
    const { selectedLocationId, locations } = useProviderStore();

    // Helper to get location name
    const currentLocation = locations.find(l => l.id === selectedLocationId);

    if (selectedLocationId === 'all') {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-center bg-[#1a1a2e] border border-white/5 rounded-2xl">
                <div className="w-16 h-16 bg-yellow-500/10 rounded-full flex items-center justify-center mb-6">
                    <AlertTriangle className="w-8 h-8 text-yellow-500" />
                </div>
                <h1 className="text-2xl font-light text-white mb-2">Select a Location</h1>
                <p className="text-gray-400 max-w-md">
                    To view the calendar, please select a specific location from the dropdown menu at the top of the page.
                    Merging calendars from multiple locations is not supported yet.
                </p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-light text-white mb-2">Calendar</h1>
                    <p className="text-gray-400">
                        Viewing schedule for <span className="text-[#d4af37]">{currentLocation?.name}</span>
                    </p>
                </div>

                <button className="flex items-center gap-2 px-4 py-2 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium hover:bg-[#b8960f] transition-colors">
                    <CalendarIcon className="w-5 h-5" />
                    <span>New Appointment</span>
                </button>
            </div>

            {/* Calendar Placeholder */}
            <div className="flex-1 bg-[#1a1a2e] border border-white/5 rounded-2xl min-h-[600px] flex items-center justify-center">
                <div className="text-center text-gray-500">
                    <p className="mb-2">Calendar Component Integration Pending</p>
                    <p className="text-sm">Location ID: {selectedLocationId}</p>
                </div>
            </div>
        </div>
    );
}
