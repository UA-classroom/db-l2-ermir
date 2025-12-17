'use client';

import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, User, Clock, Calendar as CalendarIcon, MapPin, AlertCircle } from 'lucide-react';
import { getLocationEmployees, Employee } from '@/lib/employees';
import { getLocationServices } from '@/lib/businesses';
import { useAuthStore } from '@/lib/store';
import { useProviderStore } from '@/lib/store/providerStore';
import EmployeeModal from './EmployeeModal';
import ScheduleModal from './ScheduleModal';

export default function EmployeesPage() {
    const { user } = useAuthStore();
    const { business, locations, selectedLocationId, isLoading: isGlobalLoading } = useProviderStore();

    const [employees, setEmployees] = useState<Employee[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [serviceMap, setServiceMap] = useState<Map<string, string>>(new Map());
    const [availableServices, setAvailableServices] = useState<any[]>([]);
    const [expandedEmployeeId, setExpandedEmployeeId] = useState<string | null>(null);

    // Modal States
    const [isEmployeeModalOpen, setIsEmployeeModalOpen] = useState(false);
    const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
    const [selectedEmployee, setSelectedEmployee] = useState<Employee | undefined>(undefined);

    useEffect(() => {
        if (business) {
            loadData();
        }
    }, [business?.id, selectedLocationId, locations]);

    const loadData = async () => {
        if (!business) return;
        setIsLoading(true);

        // 1. Fetch Services (Non-critical, don't block employees)
        try {
            // Use local variable to avoid TS issues if types aren't perfect yet
            getLocationServices(business.id)
                .then((services: any[]) => {
                    const newMap = new Map<string, string>();
                    if (Array.isArray(services)) {
                        setAvailableServices(services);
                        services.forEach(s => {
                            if (s.variants && Array.isArray(s.variants)) {
                                s.variants.forEach((v: any) => {
                                    newMap.set(v.id, `${s.name} - ${v.name}`);
                                });
                            }
                        });
                    }
                    setServiceMap(newMap);
                })
                .catch(err => {
                    console.warn('Failed to load services for skill map:', err);
                });
        } catch (e) {
            // Ignore sync errors in trigger
        }

        // 2. Fetch Employees (Critical)
        try {
            await loadEmployees();
        } catch (err) {
            console.error('Error loading data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadEmployees = async () => {
        try {
            let allEmployees: Employee[] = [];

            if (selectedLocationId === 'all') {
                // Fetch for ALL known locations and merge
                // Limit to 10 locations to avoid spamming if user has many
                const promises = locations.slice(0, 10).map(loc => getLocationEmployees(loc.id));
                const results = await Promise.all(promises);

                // Merge and Deduplicate by ID
                const employeeMap = new Map<string, Employee>();
                results.flat().forEach(emp => {
                    employeeMap.set(emp.id, emp);
                });
                allEmployees = Array.from(employeeMap.values());
            } else {
                // Fetch for single location
                allEmployees = await getLocationEmployees(selectedLocationId);
            }

            setEmployees(allEmployees);
        } catch (err) {
            console.error('Error loading employees:', err);
            // We don't re-throw here to prevent crashing the whole page if just employees fail
        }
    };

    const toggleExpand = (id: string) => {
        setExpandedEmployeeId(prev => prev === id ? null : id);
    };

    const handleSaveEmployee = () => {
        loadEmployees();
        setIsEmployeeModalOpen(false);
    };

    const handleEdit = (employee: Employee) => {
        setSelectedEmployee(employee);
        setIsEmployeeModalOpen(true);
    };

    const handleSchedule = (employee: Employee) => {
        setSelectedEmployee(employee);
        setIsScheduleModalOpen(true);
    };

    const handleAdd = () => {
        setSelectedEmployee(undefined);
        setIsEmployeeModalOpen(true);
    };

    if (isGlobalLoading || (business && isLoading && employees.length === 0)) {
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
                    <CalendarIcon className="w-8 h-8 text-[#d4af37]" />
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
                    <h1 className="text-3xl font-light text-white mb-2">Employees</h1>
                    <p className="text-gray-400">
                        {selectedLocationId === 'all'
                            ? `All staff across ${locations.length} locations`
                            : `Staff at ${locations.find(l => l.id === selectedLocationId)?.name}`
                        }
                    </p>
                </div>
                <button
                    onClick={handleAdd}
                    className="flex items-center gap-2 px-4 py-2 bg-[#d4af37] text-[#0f0f1a] rounded-lg font-medium hover:bg-[#b8960f] transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    <span>Add Employee</span>
                </button>
            </div>

            {employees.length === 0 ? (
                <div className="text-center py-12 bg-[#1a1a2e] border border-white/5 rounded-2xl">
                    <p className="text-gray-400 mb-4">No employees found.</p>
                    <button onClick={handleAdd} className="text-[#d4af37] hover:underline">Add your first employee</button>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {employees.map((employee) => (
                        <div key={employee.id} className="bg-[#1a1a2e] border border-white/5 rounded-2xl overflow-hidden group hover:border-[#d4af37]/30 transition-all">
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex items-center gap-4">
                                        <div
                                            className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-medium text-[#0f0f1a]"
                                            style={{ backgroundColor: employee.color_code || '#d4af37' }}
                                        >
                                            {employee.first_name?.[0] || employee.job_title[0]}
                                        </div>
                                        <div>
                                            <h3 className="text-xl text-white font-light">
                                                {employee.first_name} {employee.last_name}
                                            </h3>
                                            <p className="text-[#d4af37] text-sm">{employee.job_title}</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleSchedule(employee)}
                                            className="p-2 text-gray-400 hover:text-[#d4af37] hover:bg-white/5 rounded-lg transition-colors"
                                            title="Manage Schedule"
                                        >
                                            <Clock className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => handleEdit(employee)}
                                            className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                                        >
                                            <Edit2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>

                                {selectedLocationId === 'all' && (
                                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                                        <MapPin className="w-3 h-3" />
                                        <span>
                                            {locations.find(l => l.id === employee.location_id)?.name || 'Unknown Location'}
                                        </span>
                                    </div>
                                )}

                                {employee.bio && (
                                    <p className="text-gray-400 text-sm mb-4 line-clamp-2">{employee.bio}</p>
                                )}

                                <div className="flex flex-wrap gap-2">
                                    {/* Skills Rendering with Expansion Logic */}
                                    {(() => {
                                        const visibleSkills = expandedEmployeeId === employee.id
                                            ? employee.skills
                                            : employee.skills?.slice(0, 3);
                                        const remainingCount = (employee.skills?.length || 0) - 3;

                                        return (
                                            <>
                                                {visibleSkills?.map((skill, i) => (
                                                    <span key={i} className="text-xs px-2 py-1 bg-white/5 rounded-full text-gray-300 border border-white/5">
                                                        {serviceMap.get(skill.service_variant_id) || 'Unknown Service'}
                                                    </span>
                                                ))}

                                                {!expandedEmployeeId && remainingCount > 0 && (
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation(); // Prevent opening edit modal
                                                            toggleExpand(employee.id);
                                                        }}
                                                        className="text-xs px-2 py-1 bg-white/5 rounded-full text-gray-500 hover:text-[#d4af37] hover:bg-white/10 transition-colors"
                                                    >
                                                        +{remainingCount} more
                                                    </button>
                                                )}

                                                {expandedEmployeeId === employee.id && (employee.skills?.length || 0) > 3 && (
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            toggleExpand(employee.id);
                                                        }}
                                                        className="text-xs px-2 py-1 bg-white/5 rounded-full text-gray-500 hover:text-[#d4af37] hover:bg-white/10 transition-colors"
                                                    >
                                                        Show Less
                                                    </button>
                                                )}
                                            </>
                                        );
                                    })()}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modals */}
            {isEmployeeModalOpen && (
                <EmployeeModal
                    isOpen={isEmployeeModalOpen}
                    onClose={() => setIsEmployeeModalOpen(false)}
                    onSave={handleSaveEmployee}
                    employeeToEdit={selectedEmployee}
                    serviceMap={serviceMap}
                    availableServices={availableServices}
                />
            )}

            {isScheduleModalOpen && selectedEmployee && (
                <ScheduleModal
                    isOpen={isScheduleModalOpen}
                    onClose={() => setIsScheduleModalOpen(false)}
                    employee={selectedEmployee}
                />
            )}
        </div>
    );
}
