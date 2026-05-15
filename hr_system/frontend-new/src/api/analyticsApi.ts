import api from "./axios";

export interface EmployeeGrowth {
  month: string;
  total_employees: number;
  new_hires: number;
  departures: number;
}

export interface AttritionRate {
  month: string;
  rate: number;
  department: string;
}

export interface SalaryDistribution {
  range: string;
  count: number;
  percentage: number;
}

export interface DepartmentStats {
  department: string;
  employee_count: number;
  avg_salary: number;
  gender_ratio: {
    male: number;
    female: number;
    other: number;
  };
}

export const getEmployeeGrowth = async () => {
  const res = await api.get("/analytics/employee-growth");
  return res.data;
};

export const getAttritionRate = async () => {
  const res = await api.get("/analytics/attrition-rate");
  return res.data;
};

export const getSalaryDistribution = async () => {
  const res = await api.get("/analytics/salary-distribution");
  return res.data;
};

export const getDepartmentStats = async () => {
  const res = await api.get("/analytics/department-stats");
  return res.data;
};

export const getAttendanceTrends = async () => {
  const res = await api.get("/analytics/attendance-trends");
  return res.data;
};

export const getGenderRatio = async () => {
  const res = await api.get("/analytics/gender-ratio");
  return res.data;
};

export const getPerformanceMetrics = async () => {
  const res = await api.get("/analytics/performance-metrics");
  return res.data;
};
