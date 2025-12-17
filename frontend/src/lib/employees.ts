import api from './api';

export interface EmployeeSkill {
    service_variant_id: string;
    custom_price?: number;
    custom_duration?: number;
}

export interface Employee {
    id: string;
    user_id: string;
    location_id: string;
    job_title: string;
    bio?: string;
    color_code?: string;
    is_active: boolean;
    // User info from joined users table
    first_name?: string;
    last_name?: string;
    // Skills (services this employee can perform)
    skills: EmployeeSkill[];
}

export interface WorkingHours {
    id: string;
    employee_id: string;
    day_of_week: number;
    start_time: string;
    end_time: string;
}

/**
 * Get employees for a location
 */
export async function getLocationEmployees(locationId: string): Promise<Employee[]> {
    const response = await api.get('/employees/', {
        params: {
            location_id: locationId,
            is_active: true,
        },
    });
    return response.data;
}

/**
 * Get a single employee by ID
 */
export async function getEmployee(employeeId: string): Promise<Employee> {
    const response = await api.get(`/employees/${employeeId}`);
    return response.data;
}

/**
 * Create a new employee
 */
export async function createEmployee(data: {
    user_id: string;
    location_id: string;
    job_title: string;
    bio?: string;
    color_code?: string;
    is_active: boolean;
}): Promise<Employee> {
    const response = await api.post('/employees/', data);
    return response.data;
}

/**
 * Update an employee
 */
export async function updateEmployee(
    employeeId: string,
    data: Partial<Omit<Employee, 'id' | 'skills' | 'first_name' | 'last_name'>>
): Promise<Employee> {
    const response = await api.put(`/employees/${employeeId}`, data);
    return response.data;
}

/**
 * Delete an employee
 */
export async function deleteEmployee(employeeId: string): Promise<void> {
    await api.delete(`/employees/${employeeId}`);
}

/**
 * Get working hours for an employee  
 */
export async function getEmployeeWorkingHours(employeeId: string): Promise<WorkingHours[]> {
    const response = await api.get(`/employees/${employeeId}/working-hours`);
    return response.data;
}

/**
 * Add working hours
 */
export async function addWorkingHours(data: {
    employee_id: string;
    day_of_week: number;
    start_time: string;
    end_time: string;
}): Promise<WorkingHours> {
    const response = await api.post(`/employees/${data.employee_id}/working-hours`, data);
    return response.data;
}

export interface InternalEvent {
    id: string;
    employee_id: string;
    type: 'vacation' | 'sick' | 'meeting' | 'other';
    start_time: string;
    end_time: string;
    description?: string;
}

/**
 * Get internal events
 */
export async function getInternalEvents(employeeId: string, startDate?: string, endDate?: string): Promise<InternalEvent[]> {
    const response = await api.get(`/employees/${employeeId}/internal-events`, {
        params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
}

/**
 * Add internal event
 */
export async function addInternalEvent(data: Omit<InternalEvent, 'id'>): Promise<InternalEvent> {
    const response = await api.post(`/employees/${data.employee_id}/internal-events`, data);
    return response.data;
}

/**
 * Add skill to employee
 */
export async function addEmployeeSkill(
    employeeId: string,
    skill: { service_variant_id: string; custom_price?: number; custom_duration?: number }
): Promise<void> {
    await api.post(`/employees/${employeeId}/skills`, skill);
}
