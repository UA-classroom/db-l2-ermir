'use client';

import { useState } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import { Employee, createEmployee, updateEmployee, addEmployeeSkill } from '@/lib/employees';
import { useProviderStore } from '@/lib/store/providerStore';

interface EmployeeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: () => void;
    employeeToEdit?: Employee;
    serviceMap: Map<string, string>;
    availableServices?: any[];
}

export default function EmployeeModal({ isOpen, onClose, onSave, employeeToEdit, serviceMap, availableServices = [] }: EmployeeModalProps) {
    const { locations } = useProviderStore();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Form State
    const [userId, setUserId] = useState(employeeToEdit?.user_id || '');
    const [locationId, setLocationId] = useState(employeeToEdit?.location_id || locations[0]?.id || '');
    const [jobTitle, setJobTitle] = useState(employeeToEdit?.job_title || '');
    const [bio, setBio] = useState(employeeToEdit?.bio || '');
    const [colorCode, setColorCode] = useState(employeeToEdit?.color_code || '#d4af37');
    const [isActive, setIsActive] = useState(employeeToEdit?.is_active ?? true);

    // Skill State
    const [selectedServiceVariantId, setSelectedServiceVariantId] = useState('');
    const [isAddingSkill, setIsAddingSkill] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            if (employeeToEdit) {
                await updateEmployee(employeeToEdit.id, {
                    job_title: jobTitle,
                    bio,
                    color_code: colorCode,
                    is_active: isActive,
                    location_id: locationId
                });
            } else {
                if (!userId) {
                    setError('User ID is required to link an account.');
                    setIsLoading(false);
                    return;
                }
                await createEmployee({
                    user_id: userId,
                    location_id: locationId,
                    job_title: jobTitle,
                    bio,
                    color_code: colorCode,
                    is_active: isActive
                });
            }
            onSave();
        } catch (err: any) {
            console.error('Failed to save employee:', err);
            setError(err.response?.data?.detail || 'Failed to save employee. Check if User ID exists.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl w-full max-w-lg shadow-xl animate-scale-up">
                <div className="flex justify-between items-center p-6 border-b border-white/5">
                    <h2 className="text-xl font-light text-white">
                        {employeeToEdit ? 'Edit Employee' : 'Add New Employee'}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-lg flex items-center gap-2 text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    {!employeeToEdit && (
                        <div className="space-y-2">
                            <label className="text-sm text-gray-400">User ID (UUID)</label>
                            <input
                                type="text"
                                value={userId}
                                onChange={(e) => setUserId(e.target.value)}
                                className="w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none font-mono text-sm"
                                placeholder="e.g. 550e8400-e29b-..."
                                required
                            />
                            <p className="text-xs text-gray-500">
                                Enter the UUID of the existing user account you want to grant employee access to.
                            </p>
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-sm text-gray-400">Assigned Location</label>
                        <select
                            value={locationId}
                            onChange={(e) => setLocationId(e.target.value)}
                            className="w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none"
                            required
                        >
                            {locations.map(loc => (
                                <option key={loc.id} value={loc.id}>{loc.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm text-gray-400">Job Title</label>
                            <input
                                type="text"
                                value={jobTitle}
                                onChange={(e) => setJobTitle(e.target.value)}
                                className="w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none"
                                placeholder="e.g. Senior Stylist"
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm text-gray-400">Color Code</label>
                            <div className="flex items-center gap-2">
                                <input
                                    type="color"
                                    value={colorCode}
                                    onChange={(e) => setColorCode(e.target.value)}
                                    className="h-10 w-10 bg-transparent border-none cursor-pointer"
                                />
                                <input
                                    type="text"
                                    value={colorCode}
                                    onChange={(e) => setColorCode(e.target.value)}
                                    className="w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-2 text-white font-mono text-sm uppercase"
                                    pattern="^#[0-9A-Fa-f]{6}$"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm text-gray-400">Bio</label>
                        <textarea
                            value={bio}
                            onChange={(e) => setBio(e.target.value)}
                            className="w-full bg-[#16213e] border border-white/10 rounded-lg px-4 py-3 text-white focus:border-[#d4af37] focus:outline-none min-h-[100px]"
                            placeholder="Short description..."
                        />
                    </div>

                    <label className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors">
                        <input
                            type="checkbox"
                            checked={isActive}
                            onChange={(e) => setIsActive(e.target.checked)}
                            className="w-5 h-5 rounded border-gray-500 text-[#d4af37] focus:ring-[#d4af37]"
                        />
                        <span className="text-white">Active Employee</span>
                    </label>

                    {/* Skills Section - Only for existing employees (simplification) */}
                    {employeeToEdit && (
                        <div className="pt-4 border-t border-white/5">
                            <h3 className="text-white font-medium mb-3">Skills (Assigned Services)</h3>
                            <div className="space-y-3">
                                <div className="flex flex-wrap gap-2">
                                    {employeeToEdit.skills?.map((skill, i) => (
                                        <div key={i} className="bg-[#d4af37]/10 border border-[#d4af37]/30 text-[#d4af37] px-3 py-1 rounded-full text-sm flex items-center gap-2">
                                            <span>
                                                {serviceMap.get(skill.service_variant_id) || 'Unknown Service'}
                                            </span>
                                        </div>
                                    ))}
                                    {(!employeeToEdit.skills || employeeToEdit.skills.length === 0) && (
                                        <p className="text-gray-500 text-sm">No skills assigned yet.</p>
                                    )}
                                </div>
                                <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/5">
                                    <label className="text-xs text-gray-400 block mb-2">Assign New Service</label>
                                    <div className="flex gap-2">
                                        <select
                                            value={selectedServiceVariantId}
                                            onChange={(e) => setSelectedServiceVariantId(e.target.value)}
                                            className="flex-1 bg-[#16213e] border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-[#d4af37] focus:outline-none"
                                            disabled={isAddingSkill}
                                        >
                                            <option value="">Select Service...</option>
                                            {availableServices.map(service => (
                                                <optgroup key={service.id} label={service.name}>
                                                    {service.variants?.map((variant: any) => (
                                                        <option key={variant.id} value={variant.id}>
                                                            {variant.name} ({variant.duration_minutes} min)
                                                        </option>
                                                    ))}
                                                </optgroup>
                                            ))}
                                        </select>
                                        <button
                                            type="button"
                                            disabled={!selectedServiceVariantId || isAddingSkill}
                                            onClick={async () => {
                                                if (!selectedServiceVariantId || !employeeToEdit) return;
                                                setIsAddingSkill(true);
                                                try {
                                                    await addEmployeeSkill(employeeToEdit.id, {
                                                        service_variant_id: selectedServiceVariantId
                                                    });
                                                    // Reset and refresh parent
                                                    setSelectedServiceVariantId('');
                                                    onSave(); // This triggers a reload in parent
                                                } catch (err) {
                                                    console.error("Failed to add skill", err);
                                                    alert("Failed to assign skill");
                                                } finally {
                                                    setIsAddingSkill(false);
                                                }
                                            }}
                                            className="px-4 py-2 bg-[#d4af37] text-[#0f0f1a] rounded-lg text-sm font-medium hover:bg-[#b8960f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {isAddingSkill ? 'Adding...' : 'Add'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="flex gap-4 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 py-3 bg-white/5 text-white rounded-xl font-medium hover:bg-white/10 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="flex-1 py-3 bg-[#d4af37] text-[#0f0f1a] rounded-xl font-medium hover:bg-[#b8960f] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {isLoading ? 'Saving...' : (
                                <>
                                    <Save className="w-5 h-5" />
                                    <span>Save Employee</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
