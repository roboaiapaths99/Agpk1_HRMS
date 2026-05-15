from datetime import datetime, date
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    NOTICE_PERIOD = "notice_period"
    TERMINATED = "terminated"
    RESIGNED = "resigned"


class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    MARKETING = "marketing"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"
    CUSTOMER_SUPPORT = "customer_support"
    ADMIN = "admin"


class Employee(Document):
    """Employee model for complete digital employee records"""
    
    # Basic Information
    employee_code: Indexed(str, unique=True) = Field(..., description="Unique employee code")
    first_name: str = Field(..., min_length=2, max_length=50, description="First name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last name")
    email: Indexed(str, unique=True) = Field(..., description="Work email address")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Professional Information
    department: Department = Field(..., description="Department")
    designation: str = Field(..., min_length=2, max_length=100, description="Job title/designation")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    reporting_manager: Optional[str] = Field(None, description="Employee code of reporting manager")
    
    # Compensation
    base_salary: float = Field(..., gt=0, description="Monthly base salary")
    variable_pay: Optional[float] = Field(0, ge=0, description="Variable compensation")
    ctc: Optional[float] = Field(None, description="Total annual CTC")
    
    # Employment Details
    joining_date: date = Field(..., description="Date of joining")
    confirmation_date: Optional[date] = Field(None, description="Date of confirmation")
    probation_end_date: Optional[date] = Field(None, description="Probation period end date")
    
    # Personal Information
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender")
    blood_group: Optional[str] = Field(None, description="Blood group")
    
    # Address Information
    permanent_address: Optional[dict] = Field(None, description="Permanent address")
    current_address: Optional[dict] = Field(None, description="Current address")
    
    # Bank Information
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    bank_name: Optional[str] = Field(None, description="Bank name")
    ifsc_code: Optional[str] = Field(None, description="IFSC code")
    pan_number: Optional[str] = Field(None, description="PAN number")
    aadhaar_number: Optional[str] = Field(None, description="Aadhaar number")
    
    # Status and Metadata
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE, description="Employee status")
    exit_date: Optional[date] = Field(None, description="Date of exit")
    exit_reason: Optional[str] = Field(None, description="Reason for exit")
    
    # Work Information
    work_location: Optional[str] = Field(None, description="Work location")
    shift: Optional[str] = Field(None, description="Work shift")
    work_email: Optional[str] = Field(None, description="Personal work email")
    
    # Benefits and Insurance
    esi_number: Optional[str] = Field(None, description="ESI number")
    pf_number: Optional[str] = Field(None, description="PF number")
    insurance_policy_number: Optional[str] = Field(None, description="Insurance policy number")
    
    # Skills and Qualifications
    skills: List[str] = Field(default_factory=list, description="Employee skills")
    qualifications: List[dict] = Field(default_factory=list, description="Educational qualifications")
    experience_years: Optional[float] = Field(0, ge=0, description="Total experience in years")
    
    # Documents
    documents: List[dict] = Field(default_factory=list, description="Uploaded documents")
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, description="Emergency contact relation")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created this record")
    last_modified_by: Optional[str] = Field(None, description="User who last modified this record")
    
    # Performance
    performance_rating: Optional[str] = Field(None, description="Latest performance rating")
    last_review_date: Optional[date] = Field(None, description="Last performance review date")
    
    class Settings:
        name = "employees"
        indexes = [
            "employee_code",
            "email",
            "department",
            "status",
            "employment_type",
            "joining_date",
            "reporting_manager"
        ]
    
    @validator('ctc', always=True)
    def calculate_ctc(cls, v, values):
        """Calculate CTC if not provided"""
        if v is None:
            base_salary = values.get('base_salary', 0)
            variable_pay = values.get('variable_pay', 0)
            return (base_salary + variable_pay) * 12  # Annual CTC
        return v
    
    @validator('last_name')
    def validate_name(cls, v):
        """Validate name contains only letters"""
        if not v.replace(' ', '').replace('-', '').replace('.', '').isalpha():
            raise ValueError('Name must contain only letters, spaces, hyphens, and dots')
        return v.title()
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def employment_duration(self) -> Optional[int]:
        """Calculate employment duration in days"""
        if self.joining_date:
            end_date = self.exit_date or date.today()
            return (end_date - self.joining_date).days
        return None
    
    @property
    def monthly_ctc(self) -> float:
        """Get monthly CTC"""
        return self.ctc / 12 if self.ctc else 0
    
    async def update_status(self, new_status: EmployeeStatus, reason: Optional[str] = None):
        """Update employee status with audit trail"""
        old_status = self.status
        self.status = new_status
        
        if new_status in [EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]:
            self.exit_date = date.today()
            self.exit_reason = reason
        
        self.updated_at = datetime.utcnow()
        await self.save()
        
        # Log status change (implement audit logging)
        await self._log_status_change(old_status, new_status, reason)
    
    async def _log_status_change(self, old_status: str, new_status: str, reason: Optional[str]):
        """Log status change for audit purposes"""
        # This would be implemented with an audit logging system
        pass
    
    def is_active_employee(self) -> bool:
        """Check if employee is currently active"""
        return self.status == EmployeeStatus.ACTIVE
    
    def get_reporting_hierarchy(self) -> Optional[str]:
        """Get reporting manager code"""
        return self.reporting_manager
