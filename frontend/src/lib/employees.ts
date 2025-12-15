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
 * Get working hours for an employee  
 */
export async function getEmployeeWorkingHours(employeeId: string): Promise<WorkingHours[]> {
    const response = await api.get(`/employees/${employeeId}/working-hours`);
    return response.data;
}
