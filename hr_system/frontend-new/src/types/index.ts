export interface Employee {
  id: number
  name: string
  email: string
  phone: string
  department: string
  position: string
  location: string
  salary: string
  status: 'Active' | 'On Leave' | 'Inactive'
}

export interface PayrollRecord {
  id: number
  employee: string
  month: string
  basic: string
  hra: string
  da: string
  other: string
  gross: string
  deductions: string
  net: string
  status: 'Processed' | 'Pending'
}

export interface AttendanceRecord {
  id: number
  name: string
  checkIn: string
  checkOut: string
  status: 'Present' | 'Absent' | 'Late'
  department: string
  lateBy: string
}
