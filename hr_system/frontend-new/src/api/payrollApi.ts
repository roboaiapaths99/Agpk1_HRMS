import api from "./axios";

export interface PayrollRecord {
  id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  basic_salary: number;
  hra: number;
  bonus: number;
  allowances: number;
  pf: number;
  professional_tax: number;
  tds: number;
  gross_salary: number;
  deductions: number;
  net_salary: number;
  month: string;
  year: number;
  status: 'pending' | 'processed' | 'paid';
}

export const getPayrollRecords = async (month?: string, year?: number) => {
  const params = new URLSearchParams();
  if (month) params.append('month', month);
  if (year) params.append('year', year.toString());
  
  const res = await api.get(`/payroll?${params}`);
  return res.data;
};

export const processPayroll = async (data: any) => {
  return api.post("/payroll/run-monthly", data);
};

export const generatePayslip = async (payrollId: string) => {
  return api.get(`/payroll/${payrollId}/payslip`);
};

export const getPayrollSummary = async () => {
  const res = await api.get("/payroll/statistics");
  return res.data;
};

export const getDepartmentPayroll = async () => {
  const res = await api.get("/payroll/", { params: { page: 1, page_size: 100 } });
  return res.data;
};

export const getMonthlyPayrollTrend = async () => {
  const res = await api.get("/payroll/statistics");
  return res.data;
};

export const updatePayroll = async (payrollId: string, data: Partial<PayrollRecord>) => {
  return api.put(`/payroll/${payrollId}`, data);
};

export const deletePayroll = async (payrollId: string) => {
  return api.delete(`/payroll/${payrollId}`);
};

export const approvePayroll = async (payrollId: string) => {
  return api.patch(`/payroll/${payrollId}/approve`);
};

export const exportPayroll = async (month?: string, format: string = 'excel') => {
  const params: any = { format };
  if (month) params.payroll_month = month;
  return api.get("/payroll/export", { params });
};
