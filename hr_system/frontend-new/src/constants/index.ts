export const API_BASE_URL = 'http://localhost:8000'

export const DEPARTMENTS = [
  'Engineering',
  'HR',
  'Sales',
  'Marketing',
  'Operations',
  'Finance'
] as const

export const STATUSES = {
  EMPLOYEE: ['Active', 'On Leave', 'Inactive'] as const,
  ATTENDANCE: ['Present', 'Absent', 'Late'] as const,
  PAYROLL: ['Processed', 'Pending'] as const
}
