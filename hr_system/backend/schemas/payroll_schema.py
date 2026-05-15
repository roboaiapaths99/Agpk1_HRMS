from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class PayrollStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"
    LOCKED = "locked"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    ONLINE_TRANSFER = "online_transfer"


class PayrollBase(BaseModel):
    """Base payroll schema"""
    employee_id: str
    employee_code: str
    employee_name: str
    department: str
    designation: str
    payroll_month: str
    from_date: date
    to_date: date


class PayrollCreate(PayrollBase):
    """Create payroll schema"""
    working_days: int = 22
    present_days: int = 22
    absent_days: int = 0
    leave_days: int = 0
    holidays: int = 0
    base_salary: float
    attendance_salary: Optional[float] = None
    overtime_hours: float = 0
    overtime_rate: float = 1.5
    overtime_amount: float = 0
    bonus: float = 0
    other_earnings: float = 0
    gross_salary: Optional[float] = None
    pf_employee: Optional[float] = None
    pf_employer: Optional[float] = None
    esi_employee: Optional[float] = None
    esi_employer: Optional[float] = None
    professional_tax: Optional[float] = None
    income_tax: Optional[float] = None
    loan_deductions: float = 0
    advance_deductions: float = 0
    other_deductions: float = 0
    total_deductions: Optional[float] = None
    net_salary: Optional[float] = None
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    bank_account: Optional[str] = None


class PayrollUpdate(BaseModel):
    """Update payroll schema"""
    status: Optional[PayrollStatus] = None
    working_days: Optional[int] = None
    present_days: Optional[int] = None
    absent_days: Optional[int] = None
    leave_days: Optional[int] = None
    holidays: Optional[int] = None
    base_salary: Optional[float] = None
    attendance_salary: Optional[float] = None
    overtime_hours: Optional[float] = None
    overtime_rate: Optional[float] = None
    overtime_amount: Optional[float] = None
    bonus: Optional[float] = None
    other_earnings: Optional[float] = None
    gross_salary: Optional[float] = None
    pf_employee: Optional[float] = None
    pf_employer: Optional[float] = None
    esi_employee: Optional[float] = None
    esi_employer: Optional[float] = None
    professional_tax: Optional[float] = None
    income_tax: Optional[float] = None
    loan_deductions: Optional[float] = None
    advance_deductions: Optional[float] = None
    other_deductions: Optional[float] = None
    total_deductions: Optional[float] = None
    net_salary: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    bank_account: Optional[str] = None
    payment_date: Optional[datetime] = None
    transaction_id: Optional[str] = None


class PayrollSearch(BaseModel):
    """Search payroll schema"""
    employee_id: Optional[str] = None
    employee_code: Optional[str] = None
    payroll_month: Optional[str] = None
    status: Optional[PayrollStatus] = None
    department: Optional[str] = None
    payment_status: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class PayrollResponse(PayrollBase):
    """Response schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    status: PayrollStatus
    working_days: int
    present_days: int
    absent_days: int
    leave_days: int
    holidays: int
    base_salary: float
    attendance_salary: float
    overtime_hours: float
    overtime_rate: float
    overtime_amount: float
    bonus: float
    other_earnings: float
    gross_salary: float
    pf_employee: float
    pf_employer: float
    esi_employee: float
    esi_employer: float
    professional_tax: float
    income_tax: float
    loan_deductions: float
    advance_deductions: float
    other_deductions: float
    total_deductions: float
    net_salary: float
    payment_method: PaymentMethod
    bank_account: Optional[str]
    payment_date: Optional[datetime]
    transaction_id: Optional[str]


class PayrollListResponse(BaseModel):
    """List response schema"""
    payrolls: List[PayrollResponse]
    total: int
    page: int
    page_size: int


class PayrollStatistics(BaseModel):
    """Statistics schema"""
    total_payrolls: int
    draft_payrolls: int
    pending_approval: int
    approved_payrolls: int
    processed_payrolls: int
    paid_payrolls: int
    cancelled_payrolls: int
    total_gross_salary: Decimal
    total_net_salary: Decimal
    total_deductions: Decimal
    average_net_salary: Decimal


class PayslipRequest(BaseModel):
    """Payslip request schema"""
    payroll_id: str
    format: str = "pdf"
    include_breakdown: bool = True
    include_ytd: bool = False


class BulkPayrollAction(BaseModel):
    """Bulk payroll action schema"""
    action: str
    payroll_ids: List[str]
    parameters: Optional[Dict[str, Any]] = None


class PayrollExport(BaseModel):
    """Export schema"""
    format: str = "csv"
    payroll_month: Optional[str] = None
    department: Optional[str] = None
    status: Optional[PayrollStatus] = None
    include_deductions: bool = True
    include_earnings: bool = True


class PayrollApproval(BaseModel):
    """Payroll approval schema"""
    payroll_ids: List[str]
    approved_by: str
    notes: Optional[str] = None
    bulk_approve: bool = False


class PaymentProcessing(BaseModel):
    """Payment processing schema"""
    payroll_ids: List[str]
    payment_method: PaymentMethod
    processing_date: datetime
    notes: Optional[str] = None


class PayrollRun(BaseModel):
    """Payroll run schema"""
    payroll_month: str
    department: Optional[str] = None
    employee_ids: Optional[List[str]] = None
    include_overtime: bool = True
    include_bonus: bool = True
    auto_approve: bool = False


class PayrollRunResponse(BaseModel):
    """Payroll run response schema"""
    run_id: str
    payroll_month: str
    total_employees: int
    successful_payrolls: int
    failed_payrolls: int
    total_gross_salary: Decimal
    total_net_salary: Decimal
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    errors: Optional[List[str]] = None


class PayrollBulkAction(BaseModel):
    """Bulk payroll action schema (alias for BulkPayrollAction)"""
    payroll_ids: List[str]
    action: str


class AttendanceIntegration(BaseModel):
    """Attendance integration schema"""
    employee_id: str
    payroll_month: str
    use_attendance_data: bool = True
    attendance_source: str = "attendance_logs"
