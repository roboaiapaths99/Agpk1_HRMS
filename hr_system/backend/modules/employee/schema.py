from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class EmployeeBase(BaseModel):
    """Base employee schema"""
    first_name: str = Field(..., min_length=2, max_length=50, description="First name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Work email address")
    phone: Optional[str] = Field(None, description="Phone number")
    department: str = Field(..., description="Department")
    designation: str = Field(..., min_length=2, max_length=100, description="Job title")
    employment_type: str = Field(..., description="Type of employment")
    reporting_manager: Optional[str] = Field(None, description="Employee code of reporting manager")
    base_salary: float = Field(..., gt=0, description="Monthly base salary")
    variable_pay: Optional[float] = Field(0, ge=0, description="Variable compensation")
    joining_date: date = Field(..., description="Date of joining")
    
    # Personal Information
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender")
    blood_group: Optional[str] = Field(None, description="Blood group")
    
    # Address Information
    permanent_address: Optional[Dict[str, Any]] = Field(None, description="Permanent address")
    current_address: Optional[Dict[str, Any]] = Field(None, description="Current address")
    
    # Bank Information
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    bank_name: Optional[str] = Field(None, description="Bank name")
    ifsc_code: Optional[str] = Field(None, description="IFSC code")
    pan_number: Optional[str] = Field(None, description="PAN number")
    aadhaar_number: Optional[str] = Field(None, description="Aadhaar number")
    
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
    qualifications: List[Dict[str, Any]] = Field(default_factory=list, description="Educational qualifications")
    experience_years: Optional[float] = Field(0, ge=0, description="Total experience in years")
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, description="Emergency contact relation")
    
    @validator('last_name')
    def validate_name(cls, v):
        """Validate name contains only letters"""
        if not v.replace(' ', '').replace('-', '').replace('.', '').isalpha():
            raise ValueError('Name must contain only letters, spaces, hyphens, and dots')
        return v.title()
    
    @validator('pan_number')
    def validate_pan(cls, v):
        """Validate PAN format"""
        if v and len(v) != 10:
            raise ValueError('PAN number must be 10 characters')
        return v.upper() if v else v
    
    @validator('aadhaar_number')
    def validate_aadhaar(cls, v):
        """Validate Aadhaar format"""
        if v and len(v.replace(' ', '')) != 12:
            raise ValueError('Aadhaar number must be 12 digits')
        return v.replace(' ', '') if v else v


class EmployeeCreate(EmployeeBase):
    """Schema for creating employee"""
    employee_code: Optional[str] = Field(None, description="Employee code (auto-generated if not provided)")
    confirmation_date: Optional[date] = Field(None, description="Date of confirmation")
    probation_end_date: Optional[date] = Field(None, description="Probation period end date")


class EmployeeUpdate(BaseModel):
    """Schema for updating employee"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    designation: Optional[str] = Field(None, min_length=2, max_length=100)
    employment_type: Optional[str] = Field(None)
    reporting_manager: Optional[str] = Field(None)
    base_salary: Optional[float] = Field(None, gt=0)
    variable_pay: Optional[float] = Field(None, ge=0)
    confirmation_date: Optional[date] = Field(None)
    probation_end_date: Optional[date] = Field(None)
    date_of_birth: Optional[date] = Field(None)
    gender: Optional[str] = Field(None)
    blood_group: Optional[str] = Field(None)
    permanent_address: Optional[Dict[str, Any]] = Field(None)
    current_address: Optional[Dict[str, Any]] = Field(None)
    bank_account_number: Optional[str] = Field(None)
    bank_name: Optional[str] = Field(None)
    ifsc_code: Optional[str] = Field(None)
    pan_number: Optional[str] = Field(None)
    aadhaar_number: Optional[str] = Field(None)
    work_location: Optional[str] = Field(None)
    shift: Optional[str] = Field(None)
    work_email: Optional[str] = Field(None)
    esi_number: Optional[str] = Field(None)
    pf_number: Optional[str] = Field(None)
    insurance_policy_number: Optional[str] = Field(None)
    skills: Optional[List[str]] = Field(None)
    qualifications: Optional[List[Dict[str, Any]]] = Field(None)
    experience_years: Optional[float] = Field(None, ge=0)
    emergency_contact_name: Optional[str] = Field(None)
    emergency_contact_phone: Optional[str] = Field(None)
    emergency_contact_relation: Optional[str] = Field(None)


class EmployeeResponse(BaseModel):
    """Schema for employee response"""
    id: str
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    department: str
    designation: str
    employment_type: str
    reporting_manager: Optional[str]
    base_salary: float
    variable_pay: float
    ctc: float
    joining_date: date
    confirmation_date: Optional[date]
    probation_end_date: Optional[date]
    date_of_birth: Optional[date]
    gender: Optional[str]
    blood_group: Optional[str]
    permanent_address: Optional[Dict[str, Any]]
    current_address: Optional[Dict[str, Any]]
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    ifsc_code: Optional[str]
    pan_number: Optional[str]
    aadhaar_number: Optional[str]
    work_location: Optional[str]
    shift: Optional[str]
    work_email: Optional[str]
    esi_number: Optional[str]
    pf_number: Optional[str]
    insurance_policy_number: Optional[str]
    skills: List[str]
    qualifications: List[Dict[str, Any]]
    experience_years: float
    documents: List[Dict[str, Any]]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relation: Optional[str]
    status: str
    exit_date: Optional[date]
    exit_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    last_modified_by: Optional[str]
    performance_rating: Optional[str]
    last_review_date: Optional[date]
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for employee list response"""
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmployeeStatusUpdate(BaseModel):
    """Schema for updating employee status"""
    status: str = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")


class EmployeeSearch(BaseModel):
    """Schema for employee search"""
    query: Optional[str] = Field(None, description="Search query")
    department: Optional[str] = Field(None, description="Filter by department")
    employment_type: Optional[str] = Field(None, description="Filter by employment type")
    status: Optional[str] = Field(None, description="Filter by status")
    min_salary: Optional[float] = Field(None, ge=0, description="Minimum salary filter")
    max_salary: Optional[float] = Field(None, ge=0, description="Maximum salary filter")
    joining_date_from: Optional[date] = Field(None, description="Joining date from")
    joining_date_to: Optional[date] = Field(None, description="Joining date to")


class EmployeeBulkAction(BaseModel):
    """Schema for bulk employee actions"""
    employee_ids: List[str] = Field(..., description="List of employee IDs")
    action: str = Field(..., description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")


class EmployeeDocument(BaseModel):
    """Schema for employee document"""
    document_type: str = Field(..., description="Document type")
    document_name: str = Field(..., description="Document name")
    file_url: str = Field(..., description="File URL")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[date] = Field(None, description="Document expiry date")
    notes: Optional[str] = Field(None, description="Document notes")


class EmployeePerformance(BaseModel):
    """Schema for employee performance"""
    rating: str = Field(..., description="Performance rating")
    review_date: date = Field(..., description="Review date")
    reviewer: str = Field(..., description="Reviewer name/ID")
    strengths: List[str] = Field(default_factory=list, description="Strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    goals: List[str] = Field(default_factory=list, description="Goals for next period")
    notes: Optional[str] = Field(None, description="Additional notes")


class EmployeeSalaryUpdate(BaseModel):
    """Schema for salary update"""
    new_base_salary: float = Field(..., gt=0, description="New base salary")
    new_variable_pay: Optional[float] = Field(None, ge=0, description="New variable pay")
    effective_date: date = Field(..., description="Effective date")
    reason: str = Field(..., description="Reason for salary change")
    approved_by: str = Field(..., description="Approver name/ID")


class EmployeeTransfer(BaseModel):
    """Schema for employee transfer"""
    new_department: str = Field(..., description="New department")
    new_designation: Optional[str] = Field(None, description="New designation")
    new_work_location: Optional[str] = Field(None, description="New work location")
    new_reporting_manager: Optional[str] = Field(None, description="New reporting manager")
    effective_date: date = Field(..., description="Effective date")
    reason: str = Field(..., description="Reason for transfer")
    approved_by: str = Field(..., description="Approver name/ID")
