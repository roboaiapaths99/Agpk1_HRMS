import api from "./axios";

export interface AttendanceRecord {
  id: string;
  employee_id: string;
  employee_name: string;
  date: string;
  check_in: string;
  check_out: string;
  status: 'present' | 'absent' | 'late' | 'half_day';
  overtime_hours: number;
  total_hours: number;
}

export const getAttendanceRecords = async (startDate?: string, endDate?: string) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  const res = await api.get(`/attendance?${params}`);
  return res.data;
};

export const markAttendance = async (data: Partial<AttendanceRecord>) => {
  return api.post("/attendance", data);
};

export const updateAttendance = async (id: string, data: Partial<AttendanceRecord>) => {
  return api.put(`/attendance/${id}`, data);
};

export const getAttendanceSummary = async () => {
  const res = await api.get("/attendance/summary");
  return res.data;
};

export const getAttendanceTrends = async () => {
  const res = await api.get("/attendance/trends");
  return res.data;
};

export const getEmployeeAttendance = async (employeeId: string) => {
  const res = await api.get(`/attendance/employee/${employeeId}`);
  return res.data;
};
