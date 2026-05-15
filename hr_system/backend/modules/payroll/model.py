from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum
from decimal import Decimal


class PayrollStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    ONLINE = "online"


class DeductionType(str, Enum):
    PF = "pf"
    ESI = "esi"
    PROFESSIONAL_TAX = "professional_tax"
    INCOME_TAX = "income_tax"
    LOAN = "loan"
    ADVANCE = "advance"
    OTHER = "other"


class AllowanceType(str, Enum):
    HRA = "hra"
    TRAVEL = "travel"
    MEDICAL = "medical"
    FOOD = "food"
    SPECIAL = "special"
    BONUS = "bonus"
    OVERTIME = "overtime"
    OTHER = "other"


class Payroll(Document):
    """Payroll calculation and payment record"""
    
    # Basic Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    
    # Payroll Period
    payroll_month: str = Field(..., description="Payroll month (YYYY-MM)")
    from_date: date = Field(..., description="Pay period start date")
    to_date: date = Field(..., description="Pay period end date")
    payment_date: Optional[date] = Field(None, description="Actual payment date")
    
    # Status and Workflow
    status: PayrollStatus = Field(default=PayrollStatus.DRAFT, description="Payroll status")
    approved_by: Optional[str] = Field(None, description="Approved by")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    processed_by: Optional[str] = Field(None, description="Processed by")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    
    # Attendance Details
    working_days: int = Field(..., ge=0, description="Total working days in period")
    present_days: int = Field(..., ge=0, description="Days present")
    absent_days: int = Field(default=0, ge=0, description="Days absent")
    leave_days: int = Field(default=0, ge=0, description="Leave days")
    holidays: int = Field(default=0, ge=0, description="Holidays")
    
    # Overtime
    overtime_hours: float = Field(default=0, ge=0, description="Total overtime hours")
    overtime_rate: float = Field(default=1.5, description="Overtime rate multiplier")
    overtime_amount: float = Field(default=0, ge=0, description="Overtime earnings")
    
    # Base Salary
    base_salary: float = Field(..., gt=0, description="Monthly base salary")
    daily_salary: float = Field(..., gt=0, description="Daily salary rate")
    earned_salary: float = Field(..., ge=0, description="Salary earned for period")
    
    # Allowances
    allowances: List[dict] = Field(default_factory=list, description="Allowance breakdown")
    total_allowances: float = Field(default=0, ge=0, description="Total allowances")
    
    # Deductions
    deductions: List[dict] = Field(default_factory=list, description="Deduction breakdown")
    total_deductions: float = Field(default=0, ge=0, description="Total deductions")
    
    # Calculations
    gross_salary: float = Field(..., ge=0, description="Gross salary")
    net_salary: float = Field(..., ge=0, description="Net salary")
    taxable_income: float = Field(default=0, ge=0, description="Taxable income")
    income_tax: float = Field(default=0, ge=0, description="Income tax deduction")
    
    # Statutory Contributions
    pf_employee: float = Field(default=0, ge=0, description="Employee PF contribution")
    pf_employer: float = Field(default=0, ge=0, description="Employer PF contribution")
    esi_employee: float = Field(default=0, ge=0, description="Employee ESI contribution")
    esi_employer: float = Field(default=0, ge=0, description="Employer ESI contribution")
    professional_tax: float = Field(default=0, ge=0, description="Professional tax")
    
    # Payment Information
    payment_method: PaymentMethod = Field(default=PaymentMethod.BANK_TRANSFER, description="Payment method")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    transaction_id: Optional[str] = Field(None, description="Payment transaction ID")
    utr_number: Optional[str] = Field(None, description="UTR number for bank transfers")
    
    # Loan and Advances
    loan_deductions: float = Field(default=0, ge=0, description="Loan deductions")
    advance_deductions: float = Field(default=0, ge=0, description="Advance deductions")
    
    # Adjustments
    adjustments: List[dict] = Field(default_factory=list, description="Manual adjustments")
    total_adjustments: float = Field(default=0, description="Total adjustments")
    
    # Audit Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Payroll admin who created")
    last_modified_by: Optional[str] = Field(None, description="Last modified by")
    
    # Comments and Notes
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    employee_notes: Optional[str] = Field(None, description="Employee notes")
    
    class Settings:
        name = "payroll"
        indexes = [
            "employee_id",
            "employee_code",
            "payroll_month",
            "status",
            "payment_date",
            "department",
            "created_at"
        ]
    
    @validator('to_date')
    def validate_pay_period(cls, v, values):
        """Validate pay period dates"""
        from_date = values.get('from_date')
        if from_date and v <= from_date:
            raise ValueError('To date must be after from date')
        return v
    
    @validator('daily_salary', always=True)
    def calculate_daily_salary(cls, v, values):
        """Calculate daily salary from base salary and working days"""
        base_salary = values.get('base_salary')
        working_days = values.get('working_days')
        if base_salary and working_days:
            return base_salary / working_days
        return v
    
    @validator('earned_salary', always=True)
    def calculate_earned_salary(cls, v, values):
        """Calculate earned salary based on attendance"""
        daily_salary = values.get('daily_salary')
        present_days = values.get('present_days')
        if daily_salary and present_days:
            return daily_salary * present_days
        return v
    
    async def calculate_payroll(self):
        """Calculate complete payroll"""
        # Calculate overtime amount
        self.overtime_amount = (self.base_salary / self.working_days / 8) * self.overtime_hours * self.overtime_rate
        
        # Calculate gross salary
        self.gross_salary = self.earned_salary + self.overtime_amount + self.total_allowances
        
        # Calculate statutory deductions (example rates)
        self.pf_employee = min(self.earned_salary * 0.12, 15000)  # 12% PF, max 15000
        self.pf_employer = min(self.earned_salary * 0.12, 15000)
        
        # ESI calculation (if applicable)
        if self.earned_salary <= 21000:  # ESI applicable if salary <= 21000
            self.esi_employee = self.earned_salary * 0.0075  # 0.75%
            self.esi_employer = self.earned_salary * 0.0325  # 3.25%
        
        # Professional tax (varies by state, example)
        self.professional_tax = 200 if self.earned_salary > 10000 else 0
        
        # Calculate taxable income
        self.taxable_income = self.gross_salary - (
            self.pf_employee + self.esi_employee + self.professional_tax + 
            self.get_standard_deduction()
        )
        
        # Calculate income tax (simplified slabs)
        self.income_tax = self.calculate_income_tax(self.taxable_income)
        
        # Total deductions
        self.total_deductions = (
            self.pf_employee + self.esi_employee + self.professional_tax + 
            self.income_tax + self.loan_deductions + self.advance_deductions
        )
        
        # Add other deductions
        for deduction in self.deductions:
            self.total_deductions += deduction.get('amount', 0)
        
        # Calculate net salary
        self.net_salary = self.gross_salary - self.total_deductions + self.total_adjustments
        
        await self.save()
    
    def get_standard_deduction(self) -> float:
        """Get standard deduction (current: 50000 per annum)"""
        return 50000 / 12  # Monthly standard deduction
    
    def calculate_income_tax(self, taxable_income: float) -> float:
        """Calculate income tax based on simplified tax slabs"""
        annual_taxable = taxable_income * 12
        
        tax = 0
        if annual_taxable <= 250000:
            tax = 0
        elif annual_taxable <= 500000:
            tax = (annual_taxable - 250000) * 0.05
        elif annual_taxable <= 1000000:
            tax = 12500 + (annual_taxable - 500000) * 0.20
        else:
            tax = 112500 + (annual_taxable - 1000000) * 0.30
        
        return tax / 12  # Convert to monthly
    
    def add_allowance(self, allowance_type: AllowanceType, amount: float, description: str = ""):
        """Add an allowance"""
        allowance = {
            "type": allowance_type.value,
            "amount": amount,
            "description": description,
            "created_at": datetime.utcnow()
        }
        self.allowances.append(allowance)
        self.total_allowances += amount
    
    def add_deduction(self, deduction_type: DeductionType, amount: float, description: str = ""):
        """Add a deduction"""
        deduction = {
            "type": deduction_type.value,
            "amount": amount,
            "description": description,
            "created_at": datetime.utcnow()
        }
        self.deductions.append(deduction)
    
    def add_adjustment(self, adjustment_type: str, amount: float, description: str = ""):
        """Add a manual adjustment"""
        adjustment = {
            "type": adjustment_type,
            "amount": amount,
            "description": description,
            "created_at": datetime.utcnow()
        }
        self.adjustments.append(adjustment)
        self.total_adjustments += amount
    
    async def approve(self, approved_by: str):
        """Approve payroll"""
        self.status = PayrollStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        await self.save()
    
    async def process(self, processed_by: str, transaction_id: Optional[str] = None):
        """Mark payroll as processed"""
        self.status = PayrollStatus.PROCESSED
        self.processed_by = processed_by
        self.processed_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id
        await self.save()
    
    async def mark_paid(self, payment_date: date, utr_number: Optional[str] = None):
        """Mark payroll as paid"""
        self.status = PayrollStatus.PAID
        self.payment_date = payment_date
        if utr_number:
            self.utr_number = utr_number
        await self.save()
    
    def get_payroll_summary(self) -> dict:
        """Get payroll summary for display"""
        return {
            "employee_code": self.employee_code,
            "employee_name": self.employee_name,
            "payroll_month": self.payroll_month,
            "gross_salary": self.gross_salary,
            "total_deductions": self.total_deductions,
            "net_salary": self.net_salary,
            "status": self.status.value,
            "payment_date": self.payment_date
        }
    
    def get_detailed_breakdown(self) -> dict:
        """Get detailed payroll breakdown"""
        return {
            "earnings": {
                "base_salary": self.earned_salary,
                "overtime": self.overtime_amount,
                "allowances": self.allowances,
                "total_earnings": self.gross_salary
            },
            "deductions": {
                "pf_employee": self.pf_employee,
                "esi_employee": self.esi_employee,
                "professional_tax": self.professional_tax,
                "income_tax": self.income_tax,
                "loan_deductions": self.loan_deductions,
                "advance_deductions": self.advance_deductions,
                "other_deductions": self.deductions,
                "total_deductions": self.total_deductions
            },
            "net_salary": self.net_salary,
            "statutory_contributions": {
                "pf_employer": self.pf_employer,
                "esi_employer": self.esi_employer
            }
        }
