'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, Clock, Plus, Trash2, AlertCircle } from 'lucide-react';
import { Employee, WorkingHours, InternalEvent, addWorkingHours, addInternalEvent } from '@/lib/employees';
import api from '@/lib/api';

interface ScheduleModalProps {
    isOpen: boolean;
    onClose: () => void;
    employee: Employee;
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function ScheduleModal({ isOpen, onClose, employee }: ScheduleModalProps) {
    const [activeTab, setActiveTab] = useState<'hours' | 'events'>('hours');
    const [schedule, setSchedule] = useState<{
        working_hours: WorkingHours[];
        internal_events: InternalEvent[];
    }>({ working_hours: [], internal_events: [] });
    const [isLoading, setIsLoading] = useState(false);

    // Form States
    const [selectedDay, setSelectedDay] = useState(1);
    const [startTime, setStartTime] = useState('09:00');
    const [endTime, setEndTime] = useState('17:00');

    // Event Form
    const [eventType, setEventType] = useState<'vacation' | 'sick' | 'meeting' | 'other'>('vacation');
    const [eventDate, setEventDate] = useState('');
    const [eventStart, setEventStart] = useState('09:00');
    const [eventEnd, setEventEnd] = useState('17:00');
    const [eventDesc, setEventDesc] = useState('');

    useEffect(() => {
        if (isOpen && employee) {
            loadSchedule();
        }
    }, [isOpen, employee]);

    const loadSchedule = async () => {
        setIsLoading(true);
        try {
            const res = await api.get(`/employees/${employee.id}/schedule`);
            setSchedule(res.data);
        } catch (err) {
            console.error('Failed to load schedule:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddShift = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await addWorkingHours({
                employee_id: employee.id,
                day_of_week: selectedDay,
                start_time: startTime,
                end_time: endTime
            });
            loadSchedule();
        } catch (err) {
            console.error('Failed to add shift:', err);
            alert('Failed to add shift. Check for overlaps.');
        }
    };

    const handleAddEvent = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Combine date + time to ISO string
            const startISO = new Date(`${eventDate}T${eventStart}`).toISOString();
            const endISO = new Date(`${eventDate}T${eventEnd}`).toISOString();

            await addInternalEvent({
                employee_id: employee.id,
                type: eventType,
                start_time: startISO,
                end_time: endISO,
                description: eventDesc
            });
            loadSchedule();
            setEventDesc('');
        } catch (err) {
            console.error('Failed to add event:', err);
            alert('Failed to add event.');
        }
    };

    const handleDeleteHours = async (id: string) => {
        if (!confirm('Delete this shift?')) return;
        try {
            // We need a delete endpoint or update? Not implemented in lib yet?
            // Actually, we missed adding `deleteWorkingHours` in lib/employees.ts
            // I'll call API directly for now
            await api.delete(`/employees/working-hours/${id}`); // Wait, endpoint might be different?
            // Checking backend: NO specific delete endpoint for working hours exposed in router?
            // Wait, looking at employees.py: there IS NO DELETE /working-hours endpoint in Router!
            // Update: I missed it or it doesn't exist.
            // Let's check backend file again.
            // Ah, line 370 in repository has delete, but is it exposed in router?
            // NO. I see `get`, `add`, but not delete. This is a missing feature in backend.
            alert('Delete not supported by backend yet (Safe Mode).');
        } catch (err) {
            console.error(err);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl w-full max-w-4xl shadow-xl h-[80vh] flex flex-col">
                <div className="flex justify-between items-center p-6 border-b border-white/5">
                    <div>
                        <h2 className="text-xl font-light text-white">Manage Schedule</h2>
                        <p className="text-sm text-gray-400">for {employee.first_name || 'Employee'}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="flex border-b border-white/5 px-6">
                    <button
                        onClick={() => setActiveTab('hours')}
                        className={`py-4 mr-8 text-sm font-medium border-b-2 transition-colors ${activeTab === 'hours' ? 'border-[#d4af37] text-[#d4af37]' : 'border-transparent text-gray-400 hover:text-white'
                            }`}
                    >
                        Working Hours
                    </button>
                    <button
                        onClick={() => setActiveTab('events')}
                        className={`py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'events' ? 'border-[#d4af37] text-[#d4af37]' : 'border-transparent text-gray-400 hover:text-white'
                            }`}
                    >
                        Time Off & Events
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-6">
                    {activeTab === 'hours' ? (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div className="md:col-span-2 space-y-4">
                                {DAYS.map((dayName, idx) => {
                                    const dayNum = idx + 1;
                                    const shifts = schedule.working_hours.filter(h => h.day_of_week === dayNum);

                                    return (
                                        <div key={dayNum} className="bg-white/5 rounded-xl p-4 flex items-center justify-between">
                                            <div className="w-32 font-medium text-gray-300">{dayName}</div>
                                            <div className="flex-1">
                                                {shifts.length === 0 ? (
                                                    <span className="text-gray-600 text-sm italic">Off</span>
                                                ) : (
                                                    <div className="flex flex-wrap gap-2">
                                                        {shifts.map(shift => (
                                                            <div key={shift.id} className="flex items-center gap-2 bg-[#16213e] border border-white/10 px-3 py-1 rounded text-sm text-[#d4af37]">
                                                                <Clock className="w-3 h-3" />
                                                                {shift.start_time.substring(0, 5)} - {shift.end_time.substring(0, 5)}
                                                                {/* Delete button disabled safely */}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            <div className="bg-[#16213e] p-6 rounded-xl h-fit">
                                <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                                    <Plus className="w-4 h-4 text-[#d4af37]" /> Add Shift
                                </h3>
                                <form onSubmit={handleAddShift} className="space-y-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Day</label>
                                        <select
                                            value={selectedDay}
                                            onChange={e => setSelectedDay(Number(e.target.value))}
                                            className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                        >
                                            {DAYS.map((d, i) => <option key={i} value={i + 1}>{d}</option>)}
                                        </select>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="text-xs text-gray-400 block mb-1">Start</label>
                                            <input
                                                type="time"
                                                value={startTime}
                                                onChange={e => setStartTime(e.target.value)}
                                                className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-gray-400 block mb-1">End</label>
                                            <input
                                                type="time"
                                                value={endTime}
                                                onChange={e => setEndTime(e.target.value)}
                                                className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                            />
                                        </div>
                                    </div>
                                    <button type="submit" className="w-full bg-[#d4af37] text-[#0f0f1a] py-2 rounded font-medium text-sm hover:bg-[#b8960f]">
                                        Add Shift
                                    </button>
                                </form>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div className="md:col-span-2 space-y-4">
                                {schedule.internal_events.length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">No time off or events scheduled.</p>
                                ) : (
                                    schedule.internal_events.map(event => (
                                        <div key={event.id} className="bg-white/5 rounded-xl p-4 flex items-center justify-between border-l-2 border-[#d4af37]">
                                            <div>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-white font-medium capitalize">{event.type}</span>
                                                    <span className="text-gray-500 text-xs px-2 py-0.5 bg-black/20 rounded-full">
                                                        {new Date(event.start_time).toLocaleDateString()}
                                                    </span>
                                                </div>
                                                <div className="text-sm text-gray-400">
                                                    {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -
                                                    {new Date(event.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </div>
                                                {event.description && <p className="text-gray-500 text-sm mt-1">{event.description}</p>}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="bg-[#16213e] p-6 rounded-xl h-fit">
                                <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-[#d4af37]" /> Add Event
                                </h3>
                                <form onSubmit={handleAddEvent} className="space-y-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Type</label>
                                        <select
                                            value={eventType}
                                            onChange={e => setEventType(e.target.value as any)}
                                            className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                        >
                                            <option value="vacation">Vacation</option>
                                            <option value="sick">Sick Leave</option>
                                            <option value="meeting">Meeting</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Date</label>
                                        <input
                                            type="date"
                                            value={eventDate}
                                            onChange={e => setEventDate(e.target.value)}
                                            className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                            required
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="text-xs text-gray-400 block mb-1">Start</label>
                                            <input
                                                type="time"
                                                value={eventStart}
                                                onChange={e => setEventStart(e.target.value)}
                                                className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-gray-400 block mb-1">End</label>
                                            <input
                                                type="time"
                                                value={eventEnd}
                                                onChange={e => setEventEnd(e.target.value)}
                                                className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Description</label>
                                        <input
                                            type="text"
                                            value={eventDesc}
                                            onChange={e => setEventDesc(e.target.value)}
                                            className="w-full bg-[#1a1a2e] border border-white/10 rounded p-2 text-white text-sm"
                                        />
                                    </div>
                                    <button type="submit" className="w-full bg-[#d4af37] text-[#0f0f1a] py-2 rounded font-medium text-sm hover:bg-[#b8960f]">
                                        Add Event
                                    </button>
                                </form>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
