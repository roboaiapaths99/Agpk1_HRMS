import api from "./axios";

export interface Employee {
  id: string;
  name: string;
  email: string;
  department: string;
  position: string;
  salary: number;
  location: string;
  joining_date: string;
  status: string;
}

export const getEmployees = async () => {
  const res = await api.get("/employees");
  return res.data;
};

export const createEmployee = async (data: Partial<Employee>) => {
  return api.post("/employees", data);
};

export const updateEmployee = async (id: string, data: Partial<Employee>) => {
  return api.put(`/employees/${id}`, data);
};

export const deleteEmployee = async (id: string) => {
  return api.delete(`/employees/${id}`);
};

export const getEmployeeById = async (id: string) => {
  const res = await api.get(`/employees/${id}`);
  return res.data;
};
