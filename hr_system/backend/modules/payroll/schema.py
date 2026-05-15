from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class PayrollBase(BaseModel):
    """Base payroll schema"""
    employee_id: str = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    payroll_month: str = Field(..., description="Payroll month (YYYY-MM)")
    from_date: date = Field(..., description="Pay period start date")
    to_date: date = Field(..., description="Pay period end date")
    
    # Attendance details
    working_days: int = Field(..., ge=0, description="Total working days in period")
    present_days: int = Field(..., ge=0, description="Days present")
    absent_days: int = Field(default=0, ge=0, description="Days absent")
    leave_days: int = Field(default=0, ge=0, description="Leave days")
    holidays: int = Field(default=0, ge=0, description="Holidays")
    
    # Overtime
    overtime_hours: float = Field(default=0, ge=0, description="Total overtime hours")
    overtime_rate: float = Field(default=1.5, description="Overtime rate multiplier")
    
    # Base salary
    base_salary: float = Field(..., gt=0, description="Monthly base salary")
    
    # Payment information
    payment_method: str = Field(default="bank_transfer", description="Payment method")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    
    # Loan and advances
    loan_deductions: float = Field(default=0, ge=0, description="Loan deductions")
    advance_deductions: float = Field(default=0, ge=0, description="Advance deductions")
    
    # Comments
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    employee_notes: Optional[str] = Field(None, description="Employee notes")


class PayrollCreate(PayrollBase):
    """Schema for creating payroll"""
    pass


class PayrollUpdate(BaseModel):
    """Schema for updating payroll"""
    to_date: Optional[date] = Field(None)
    payment_date: Optional[date] = Field(None)
    status: Optional[str] = Field(None, description="Payroll status")
    
    # Attendance updates
    present_days: Optional[int] = Field(None, ge=0)
    absent_days: Optional[int] = Field(None, ge=0)
    leave_days: Optional[int] = Field(None, ge=0)
    holidays: Optional[int] = Field(None, ge=0)
    
    # Overtime updates
    overtime_hours: Optional[float] = Field(None, ge=0)
    overtime_rate: Optional[float] = Field(None, gt=0)
    
    # Salary updates
    base_salary: Optional[float] = Field(None, gt=0)
    
    # Payment updates
    payment_method: Optional[str] = Field(None)
    bank_account: Optional[str] = Field(None)
    transaction_id: Optional[str] = Field(None)
    utr_number: Optional[str] = Field(None)
    
    # Deductions updates
    loan_deductions: Optional[float] = Field(None, ge=0)
    advance_deductions: Optional[float] = Field(None, ge=0)
    
    # Notes updates
    admin_notes: Optional[str] = Field(None)
    employee_notes: Optional[str] = Field(None)


class PayrollResponse(BaseModel):
    """Schema for payroll response"""
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    department: str
    payroll_month: str
    from_date: date
    to_date: date
    payment_date: Optional[date]
    
    # Status and workflow
    status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    processed_by: Optional[str]
    processed_at: Optional[datetime]
    
    # Attendance details
    working_days: int
    present_days: int
    absent_days: int
    leave_days: int
    holidays: int
    
    # Overtime
    overtime_hours: float
    overtime_rate: float
    overtime_amount: float
    
    # Salary calculations
    base_salary: float
    daily_salary: float
    earned_salary: float
    
    # Allowances
    allowances: List[Dict[str, Any]]
    total_allowances: float
    
    # Deductions
    deductions: List[Dict[str, Any]]
    total_deductions: float
    
    # Calculations
    gross_salary: float
    net_salary: float
    taxable_income: float
    income_tax: float
    
    # Statutory contributions
    pf_employee: float
    pf_employer: float
    esi_employee: float
    esi_employer: float
    professional_tax: float
    
    # Payment information
    payment_method: str
    bank_account: Optional[str]
    transaction_id: Optional[str]
    utr_number: Optional[str]
    
    # Loan and advances
    loan_deductions: float
    advance_deductions: float
    
    # Adjustments
    adjustments: List[Dict[str, Any]]
    total_adjustments: float
    
    # Comments
    admin_notes: Optional[str]
    employee_notes: Optional[str]
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    last_modified_by: Optional[str]
    
    class Config:
        from_attributes = True


class PayrollListResponse(BaseModel):
    """Schema for payroll list response"""
    payrolls: List[PayrollResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PayrollSearch(BaseModel):
    """Schema for payroll search"""
    query: Optional[str] = Field(None, description="Search query")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")
    payroll_month: Optional[str] = Field(None, description="Filter by payroll month")
    payment_date_from: Optional[date] = Field(None, description="Payment date from")
    payment_date_to: Optional[date] = Field(None, description="Payment date to")
    min_net_salary: Optional[float] = Field(None, ge=0, description="Minimum net salary filter")
    max_net_salary: Optional[float] = Field(None, ge=0, description="Maximum net salary filter")


class PayrollBulkAction(BaseModel):
    """Schema for bulk payroll actions"""
    payroll_ids: List[str] = Field(..., description="List of payroll IDs")
    action: str = Field(..., description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")


class PayrollAllowance(BaseModel):
    """Schema for payroll allowance"""
    allowance_type: str = Field(..., description="Type of allowance")
    amount: float = Field(..., gt=0, description="Allowance amount")
    description: Optional[str] = Field(None, description="Allowance description")


class PayrollDeduction(BaseModel):
    """Schema for payroll deduction"""
    deduction_type: str = Field(..., description="Type of deduction")
    amount: float = Field(..., gt=0, description="Deduction amount")
    description: Optional[str] = Field(None, description="Deduction description")


class PayrollAdjustment(BaseModel):
    """Schema for payroll adjustment"""
    adjustment_type: str = Field(..., description="Type of adjustment")
    amount: float = Field(..., description="Adjustment amount (can be negative)")
    description: Optional[str] = Field(None, description="Adjustment description")


class PayrollCalculationRequest(BaseModel):
    """Schema for payroll calculation request"""
    employee_id: str = Field(..., description="Employee ID")
    payroll_month: str = Field(..., description="Payroll month (YYYY-MM)")
    attendance_data: Dict[str, Any] = Field(..., description="Attendance data")
    overtime_hours: float = Field(default=0, ge=0, description="Overtime hours")
    allowances: Optional[List[PayrollAllowance]] = Field(default_factory=list)
    deductions: Optional[List[PayrollDeduction]] = Field(default_factory=list)
    adjustments: Optional[List[PayrollAdjustment]] = Field(default_factory=list)


class PayrollApproval(BaseModel):
    """Schema for payroll approval"""
    approved: bool = Field(..., description="Approval status")
    notes: Optional[str] = Field(None, description="Approval notes")


class PayrollProcessing(BaseModel):
    """Schema for payroll processing"""
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    utr_number: Optional[str] = Field(None, description="UTR number")
    payment_method: str = Field(default="bank_transfer", description="Payment method")


class PayrollStatistics(BaseModel):
    """Schema for payroll statistics"""
    total_payroll_amount: float
    total_employees: int
    average_salary: float
    total_overtime_amount: float
    total_deductions: float
    department_breakdown: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    allowance_breakdown: Dict[str, float]
    deduction_breakdown: Dict[str, float]


class PayrollTemplate(BaseModel):
    """Schema for payroll template"""
    name: str = Field(..., description="Template name")
    department: Optional[str] = Field(None, description="Department")
    description: Optional[str] = Field(None, description="Template description")
    default_allowances: List[PayrollAllowance] = Field(default_factory=list)
    default_deductions: List[PayrollDeduction] = Field(default_factory=list)
    is_active: bool = Field(default=True, description="Template active status")


class PayrollRun(BaseModel):
    """Schema for payroll run"""
    payroll_month: str = Field(..., description="Payroll month (YYYY-MM)")
    department: Optional[str] = Field(None, description="Run for specific department")
    employee_ids: Optional[List[str]] = Field(None, description="Run for specific employees")
    dry_run: bool = Field(default=False, description="Dry run without actual processing")
    auto_approve: bool = Field(default=False, description="Auto approve after calculation")


class PayrollRunResponse(BaseModel):
    """Schema for payroll run response"""
    run_id: str
    payroll_month: str
    status: str
    total_employees: int
    successful_calculations: int
    failed_calculations: int
    total_amount: float
    started_at: datetime
    completed_at: Optional[datetime]
    errors: List[Dict[str, Any]]


class PayrollSlip(BaseModel):
    """Schema for payroll slip"""
    payroll_id: str
    employee_code: str
    employee_name: str
    department: str
    designation: str
    payroll_month: str
    payment_date: Optional[date]
    
    # Earnings
    basic_salary: float
    hra: float
    special_allowance: float
    overtime_amount: float
    other_allowances: float
    total_earnings: float
    
    # Deductions
    pf_employee: float
    esi_employee: float
    professional_tax: float
    income_tax: float
    loan_deductions: float
    advance_deductions: float
    other_deductions: float
    total_deductions: float
    
    # Net salary
    net_salary: float
    
    # Statutory contributions
    pf_employer: float
    esi_employer: float
    total_cost_to_company: float
    
    # Work details
    working_days: int
    present_days: int
    overtime_hours: float
    
    # Bank details
    bank_name: Optional[str]
    bank_account: str
    payment_method: str


class PayrollYearlySummary(BaseModel):
    """Schema for yearly payroll summary"""
    year: int
    employee_id: str
    employee_code: str
    employee_name: str
    department: str
    
    # Yearly totals
    total_ctc: float
    total_gross_salary: float
    total_net_salary: float
    total_overtime_amount: float
    total_deductions: float
    
    # Monthly breakdown
    monthly_breakdown: List[Dict[str, Any]]
    
    # Yearly statistics
    average_monthly_salary: float
    total_overtime_hours: float
    total_leave_days: int


class PayrollComplianceReport(BaseModel):
    """Schema for payroll compliance report"""
    period: str
    total_employees: int
    compliant_employees: int
    non_compliant_employees: int
    
    # PF compliance
    pf_compliant: int
    pf_non_compliant: int
    total_pf_contribution: float
    
    # ESI compliance
    esi_compliant: int
    esi_non_compliant: int
    total_esi_contribution: float
    
    # PT compliance
    pt_compliant: int
    pt_non_compliant: int
    total_pt_deduction: float
    
    # Tax compliance
    tax_compliant: int
    tax_non_compliant: int
    total_tax_deduction: float
    
    # Issues
    compliance_issues: List[Dict[str, Any]]
