from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RESIGNED = "resigned"


class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    MARKETING = "marketing"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"
    ADMIN = "admin"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# Base Schemas
class EmployeeBase(BaseModel):
    """Base employee schema"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    gender: Optional[Gender] = Field(None, description="Gender")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    
    employee_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    department: Department = Field(..., description="Department")
    designation: str = Field(..., description="Job designation")
    role: str = Field(..., description="Job role")
    reporting_manager: Optional[str] = Field(None, description="Reporting manager employee code")
    
    joining_date: date = Field(..., description="Date of joining")
    confirmation_date: Optional[date] = Field(None, description="Date of confirmation")
    last_working_day: Optional[date] = Field(None, description="Last working day")
    
    ctc: float = Field(..., description="Cost to company annually")
    basic_salary: Optional[float] = Field(None, description="Basic monthly salary")
    hra: Optional[float] = Field(None, description="House rent allowance")
    other_allowances: Optional[float] = Field(None, description="Other allowances")
    
    work_location: str = Field(default="Office", description="Work location")
    remote_work_allowed: bool = Field(default=False, description="Can work remotely")
    
    address: Optional[Dict[str, str]] = Field(None, description="Address details")
    
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, description="Emergency contact relation")
    
    bank_name: Optional[str] = Field(None, description="Bank name")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    bank_ifsc: Optional[str] = Field(None, description="Bank IFSC code")
    bank_branch: Optional[str] = Field(None, description="Bank branch")
    
    skills: List[str] = Field(default_factory=list, description="Employee skills")
    qualifications: List[Dict[str, str]] = Field(default_factory=list, description="Educational qualifications")
    
    performance_rating: Optional[str] = Field(None, description="Current performance rating")
    last_review_date: Optional[date] = Field(None, description="Last performance review date")
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower()
    
    @validator('ctc')
    def validate_ctc(cls, v):
        if v <= 0:
            raise ValueError('CTC must be greater than 0')
        return v
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v and v >= date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v
    
    @validator('joining_date')
    def validate_joining_date(cls, v):
        if v > date.today():
            raise ValueError('Joining date cannot be in the future')
        return v
    
    @validator('confirmation_date')
    def validate_confirmation_date(cls, v, values):
        if v and 'joining_date' in values and v <= values['joining_date']:
            raise ValueError('Confirmation date must be after joining date')
        return v


# Request Schemas
class EmployeeCreate(EmployeeBase):
    """Schema for creating employee"""
    employee_code: str = Field(..., min_length=3, max_length=20, description="Unique employee code")
    
    @validator('employee_code')
    def validate_employee_code(cls, v):
        return v.upper()


class EmployeeUpdate(BaseModel):
    """Schema for updating employee"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    gender: Optional[Gender] = Field(None, description="Gender")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    
    employee_type: Optional[EmploymentType] = Field(None, description="Employment type")
    department: Optional[Department] = Field(None, description="Department")
    designation: Optional[str] = Field(None, description="Job designation")
    role: Optional[str] = Field(None, description="Job role")
    reporting_manager: Optional[str] = Field(None, description="Reporting manager employee code")
    
    confirmation_date: Optional[date] = Field(None, description="Date of confirmation")
    last_working_day: Optional[date] = Field(None, description="Last working day")
    
    ctc: Optional[float] = Field(None, description="Cost to company annually")
    basic_salary: Optional[float] = Field(None, description="Basic monthly salary")
    hra: Optional[float] = Field(None, description="House rent allowance")
    other_allowances: Optional[float] = Field(None, description="Other allowances")
    
    work_location: Optional[str] = Field(None, description="Work location")
    remote_work_allowed: Optional[bool] = Field(None, description="Can work remotely")
    
    address: Optional[Dict[str, str]] = Field(None, description="Address details")
    
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, description="Emergency contact relation")
    
    bank_name: Optional[str] = Field(None, description="Bank name")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    bank_ifsc: Optional[str] = Field(None, description="Bank IFSC code")
    bank_branch: Optional[str] = Field(None, description="Bank branch")
    
    skills: Optional[List[str]] = Field(None, description="Employee skills")
    qualifications: Optional[List[Dict[str, str]]] = Field(None, description="Educational qualifications")
    
    performance_rating: Optional[str] = Field(None, description="Current performance rating")
    last_review_date: Optional[date] = Field(None, description="Last performance review date")


class EmployeeStatusUpdate(BaseModel):
    """Schema for updating employee status"""
    status: EmployeeStatus = Field(..., description="New status")


class EmployeeSearch(BaseModel):
    """Schema for employee search"""
    query: Optional[str] = Field(None, description="Search query")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")
    employee_type: Optional[str] = Field(None, description="Filter by employee type")


class EmployeeBulkAction(BaseModel):
    """Schema for bulk employee actions"""
    employee_ids: List[str] = Field(..., description="List of employee IDs")
    action: str = Field(..., description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")


# Response Schemas
class EmployeeResponse(BaseModel):
    """Schema for employee response"""
    id: str
    employee_code: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str]
    gender: Optional[Gender]
    date_of_birth: Optional[date]
    
    employee_type: EmploymentType
    status: EmployeeStatus
    department: Department
    designation: str
    role: str
    reporting_manager: Optional[str]
    
    joining_date: date
    confirmation_date: Optional[date]
    last_working_day: Optional[date]
    
    ctc: float
    basic_salary: Optional[float]
    hra: Optional[float]
    other_allowances: Optional[float]
    
    work_location: str
    remote_work_allowed: bool
    
    address: Optional[Dict[str, str]]
    
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    
    bank_name: Optional[str]
    bank_account: Optional[str]
    bank_ifsc: Optional[str]
    bank_branch: Optional[str]
    
    documents: List[Dict[str, Any]]
    
    skills: List[str]
    qualifications: List[Dict[str, str]]
    
    performance_rating: Optional[str]
    last_review_date: Optional[date]
    
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    last_modified_by: Optional[str]
    
    # Computed fields
    age: Optional[int]
    experience_years: float
    monthly_salary: float
    daily_wages: float
    hourly_wages: float
    is_probation_period: bool
    has_all_required_documents: bool
    work_anniversary: Optional[date]
    is_work_anniversary_today: bool
    remaining_probation_days: Optional[int]
    address_string: str
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for employee list response"""
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmployeeStatistics(BaseModel):
    """Schema for employee statistics"""
    total_employees: int
    active_employees: int
    inactive_employees: int
    department_breakdown: List[Dict[str, Any]]
    status_breakdown: List[Dict[str, Any]]
    employment_type_breakdown: List[Dict[str, Any]]
    recent_hires: int
    employees_leaving_this_month: int
    gender_distribution: List[Dict[str, Any]]
    age_distribution: List[Dict[str, Any]]
    experience_distribution: List[Dict[str, Any]]
    location_distribution: List[Dict[str, Any]]


class UpcomingBirthday(BaseModel):
    """Schema for upcoming birthday"""
    employee_id: str
    employee_code: str
    full_name: str
    department: str
    date_of_birth: date
    days_until_birthday: int


# Document Schemas
class DocumentUpload(BaseModel):
    """Schema for document upload"""
    document_type: str = Field(..., description="Document type")
    file_name: Optional[str] = Field(None, description="File name")
    file_url: str = Field(..., description="File URL")


class DocumentResponse(BaseModel):
    """Schema for document response"""
    type: str
    file_url: str
    file_name: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Skill Management Schemas
class SkillAdd(BaseModel):
    """Schema for adding skill"""
    skill: str = Field(..., min_length=1, max_length=50)


class SkillRemove(BaseModel):
    """Schema for removing skill"""
    skill: str = Field(..., min_length=1, max_length=50)


# Performance Schemas
class PerformanceUpdate(BaseModel):
    """Schema for performance update"""
    rating: str = Field(..., description="Performance rating")
    review_date: Optional[date] = Field(None, description="Review date")
    notes: Optional[str] = Field(None, description="Review notes")


# Address Schemas
class AddressUpdate(BaseModel):
    """Schema for address update"""
    line1: Optional[str] = Field(None, max_length=200)
    line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)


# Export Schemas
class EmployeeExport(BaseModel):
    """Schema for employee export"""
    format: str = Field(default="excel", description="Export format")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")
    employee_type: Optional[str] = Field(None, description="Filter by employee type")
