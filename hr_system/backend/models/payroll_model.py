from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum
from decimal import Decimal


class PayrollStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    LOCKED = "locked"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    DIGITAL_WALLET = "digital_wallet"


class Payroll(Document):
    """Payroll document for MongoDB"""
    
    # Employee Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Department")
    designation: str = Field(..., description="Designation")
    
    # Payroll Period
    payroll_month: Indexed(str) = Field(..., description="Payroll month (YYYY-MM)")
    from_date: date = Field(..., description="Payroll period start date")
    to_date: date = Field(..., description="Payroll period end date")
    
    # Attendance Details
    working_days: int = Field(..., description="Total working days in period")
    present_days: int = Field(..., description="Days present")
    absent_days: int = Field(default=0, description="Days absent")
    leave_days: int = Field(default=0, description="Days on leave")
    holidays: int = Field(default=0, description="Holidays")
    
    # Salary Components
    base_salary: float = Field(..., description="Base monthly salary")
    attendance_salary: float = Field(..., description="Salary based on attendance")
    overtime_hours: float = Field(default=0, description="Overtime hours")
    overtime_rate: float = Field(default=1.5, description="Overtime rate multiplier")
    overtime_amount: float = Field(default=0, description="Overtime amount")
    bonus: float = Field(default=0, description="Bonus amount")
    other_earnings: float = Field(default=0, description="Other earnings")
    
    # Gross Salary
    gross_salary: float = Field(..., description="Gross salary")
    
    # Deductions
    pf_employee: float = Field(default=0, description="Employee PF contribution")
    pf_employer: float = Field(default=0, description="Employer PF contribution")
    esi_employee: float = Field(default=0, description="Employee ESI contribution")
    esi_employer: float = Field(default=0, description="Employer ESI contribution")
    professional_tax: float = Field(default=0, description="Professional tax")
    income_tax: float = Field(default=0, description="Income tax (TDS)")
    loan_deductions: float = Field(default=0, description="Loan deductions")
    advance_deductions: float = Field(default=0, description="Advance deductions")
    other_deductions: float = Field(default=0, description="Other deductions")
    
    # Total Deductions
    total_deductions: float = Field(..., description="Total deductions")
    
    # Net Salary
    net_salary: float = Field(..., description="Net salary")
    
    # Payment Information
    payment_method: PaymentMethod = Field(default=PaymentMethod.BANK_TRANSFER, description="Payment method")
    bank_account: str = Field(..., description="Bank account number")
    payment_date: Optional[date] = Field(None, description="Payment date")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    
    # Status and Approval
    status: PayrollStatus = Field(default=PayrollStatus.DRAFT, description="Payroll status")
    approved_by: Optional[str] = Field(None, description="User who approved payroll")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    locked_by: Optional[str] = Field(None, description="User who locked payroll")
    locked_at: Optional[datetime] = Field(None, description="Lock timestamp")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created payroll")
    last_modified_by: Optional[str] = Field(None, description="User who last modified payroll")
    
    # Additional Information
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "payrolls"
    #     # indexes = [
    #     #     "employee_id",
    #     #     "employee_code",
    #     #     "payroll_month",
    #     #     "status",
    #     #     "payment_date",
    #     #     "created_at"
    #     # ]
    
    @validator('payroll_month')
    def validate_payroll_month(cls, v):
        try:
            year, month = map(int, v.split('-'))
            if month < 1 or month > 12:
                raise ValueError('Invalid month')
        except (ValueError, IndexError):
            raise ValueError('Invalid payroll month format. Use YYYY-MM')
        return v
    
    @validator('to_date')
    def validate_date_range(cls, v, values):
        if 'from_date' in values and v <= values['from_date']:
            raise ValueError('To date must be after from date')
        return v
    
    @validator('working_days')
    def validate_attendance_totals(cls, v, values):
        total = v
        if 'present_days' in values:
            total += values['present_days']
        if 'absent_days' in values:
            total += values['absent_days']
        if 'leave_days' in values:
            total += values['leave_days']
        if 'holidays' in values:
            total += values['holidays']
        
        if total > v:
            raise ValueError('Total attendance days cannot exceed working days')
        return v
    
    @validator('base_salary')
    def validate_base_salary(cls, v):
        if v <= 0:
            raise ValueError('Base salary must be greater than 0')
        return v
    
    def calculate_attendance_salary(self):
        """Calculate salary based on attendance"""
        if self.working_days > 0:
            self.attendance_salary = (self.base_salary / self.working_days) * self.present_days
        else:
            self.attendance_salary = 0
    
    def calculate_overtime(self):
        """Calculate overtime amount"""
        hourly_rate = self.base_salary / (30 * 8)  # Assuming 30 days, 8 hours
        self.overtime_amount = self.overtime_hours * hourly_rate * self.overtime_rate
    
    def calculate_gross_salary(self):
        """Calculate gross salary"""
        self.gross_salary = (
            self.attendance_salary +
            self.overtime_amount +
            self.bonus +
            self.other_earnings
        )
    
    def calculate_statutory_deductions(self):
        """Calculate statutory deductions (PF, ESI, PT)"""
        if self.gross_salary > 0:
            # PF (12% of basic salary)
            self.pf_employee = self.attendance_salary * 0.12
            self.pf_employer = self.attendance_salary * 0.12
            
            # ESI (0.75% employee, 3.25% employer)
            self.esi_employee = self.gross_salary * 0.0075
            self.esi_employer = self.gross_salary * 0.0325
            
            # Professional tax (fixed amount based on salary slab)
            if self.gross_salary <= 10000:
                self.professional_tax = 0
            elif self.gross_salary <= 20000:
                self.professional_tax = 200
            else:
                self.professional_tax = 400
    
    def calculate_total_deductions(self):
        """Calculate total deductions"""
        self.total_deductions = (
            self.pf_employee +
            self.esi_employee +
            self.professional_tax +
            self.income_tax +
            self.loan_deductions +
            self.advance_deductions +
            self.other_deductions
        )
    
    def calculate_net_salary(self):
        """Calculate net salary"""
        self.net_salary = self.gross_salary - self.total_deductions
    
    def recalculate_payroll(self):
        """Recalculate all payroll components"""
        self.calculate_attendance_salary()
        self.calculate_overtime()
        self.calculate_gross_salary()
        self.calculate_statutory_deductions()
        self.calculate_total_deductions()
        self.calculate_net_salary()
    
    def approve(self, approved_by: str):
        """Approve payroll"""
        self.status = PayrollStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
    
    def lock(self, locked_by: str):
        """Lock payroll (finalized)"""
        if self.status != PayrollStatus.APPROVED:
            raise ValueError("Only approved payrolls can be locked")
        
        self.status = PayrollStatus.LOCKED
        self.locked_by = locked_by
        self.locked_at = datetime.utcnow()
    
    def mark_paid(self, payment_date: date, transaction_id: str = None):
        """Mark payroll as paid"""
        if self.status != PayrollStatus.LOCKED:
            raise ValueError("Only locked payrolls can be marked as paid")
        
        self.status = PayrollStatus.PAID
        self.payment_date = payment_date
        self.transaction_id = transaction_id
    
    def can_be_modified(self) -> bool:
        """Check if payroll can be modified"""
        return self.status in [PayrollStatus.DRAFT]
    
    def can_be_approved(self) -> bool:
        """Check if payroll can be approved"""
        return self.status == PayrollStatus.DRAFT
    
    def can_be_locked(self) -> bool:
        """Check if payroll can be locked"""
        return self.status == PayrollStatus.APPROVED
    
    def can_be_paid(self) -> bool:
        """Check if payroll can be marked as paid"""
        return self.status == PayrollStatus.LOCKED
    
    def get_deduction_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of deductions"""
        return {
            "pf_employee": self.pf_employee,
            "pf_employer": self.pf_employer,
            "esi_employee": self.esi_employee,
            "esi_employer": self.esi_employer,
            "professional_tax": self.professional_tax,
            "income_tax": self.income_tax,
            "loan_deductions": self.loan_deductions,
            "advance_deductions": self.advance_deductions,
            "other_deductions": self.other_deductions,
            "total_deductions": self.total_deductions
        }
    
    def get_earning_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of earnings"""
        return {
            "base_salary": self.base_salary,
            "attendance_salary": self.attendance_salary,
            "overtime_amount": self.overtime_amount,
            "bonus": self.bonus,
            "other_earnings": self.other_earnings,
            "gross_salary": self.gross_salary
        }
    
    def get_payroll_summary(self) -> Dict[str, Any]:
        """Get complete payroll summary"""
        return {
            "employee_info": {
                "employee_code": self.employee_code,
                "employee_name": self.employee_name,
                "department": self.department,
                "designation": self.designation
            },
            "payroll_period": {
                "payroll_month": self.payroll_month,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "working_days": self.working_days
            },
            "attendance": {
                "present_days": self.present_days,
                "absent_days": self.absent_days,
                "leave_days": self.leave_days,
                "holidays": self.holidays,
                "attendance_percentage": (self.present_days / self.working_days * 100) if self.working_days > 0 else 0
            },
            "earnings": self.get_earning_breakdown(),
            "deductions": self.get_deduction_breakdown(),
            "net_salary": self.net_salary,
            "payment_info": {
                "payment_method": self.payment_method.value,
                "bank_account": self.bank_account,
                "payment_date": self.payment_date,
                "transaction_id": self.transaction_id
            },
            "status": self.status.value,
            "approval_info": {
                "approved_by": self.approved_by,
                "approved_at": self.approved_at,
                "locked_by": self.locked_by,
                "locked_at": self.locked_at
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed fields"""
        data = self.dict()
        data.update({
            "earning_breakdown": self.get_earning_breakdown(),
            "deduction_breakdown": self.get_deduction_breakdown(),
            "payroll_summary": self.get_payroll_summary(),
            "can_be_modified": self.can_be_modified(),
            "can_be_approved": self.can_be_approved(),
            "can_be_locked": self.can_be_locked(),
            "can_be_paid": self.can_be_paid()
        })
        return data
