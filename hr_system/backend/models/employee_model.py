from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed, Link, BackLink
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


class Employee(Document):
    """Employee document for MongoDB"""
    
    # Basic Information
    employee_code: Indexed(str) = Field(..., description="Unique employee code")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    full_name: str = Field(..., description="Full name")
    email: Indexed(str) = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    gender: Optional[Gender] = Field(None, description="Gender")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    
    # Employment Details
    employee_type: EmploymentType = Field(default=EmploymentType.FULL_TIME, description="Employment type")
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE, description="Employee status")
    department: Department = Field(..., description="Department")
    designation: str = Field(..., description="Job designation")
    role: str = Field(..., description="Job role")
    reporting_manager: Optional[str] = Field(None, description="Reporting manager employee code")
    
    # Employment Dates
    joining_date: date = Field(..., description="Date of joining")
    confirmation_date: Optional[date] = Field(None, description="Date of confirmation")
    last_working_day: Optional[date] = Field(None, description="Last working day")
    
    # Compensation
    ctc: float = Field(..., description="Cost to company annually")
    basic_salary: Optional[float] = Field(None, description="Basic monthly salary")
    hra: Optional[float] = Field(None, description="House rent allowance")
    other_allowances: Optional[float] = Field(None, description="Other allowances")
    
    # Work Location
    work_location: str = Field(default="Office", description="Work location")
    remote_work_allowed: bool = Field(default=False, description="Can work remotely")
    
    # Address Information
    address: Optional[Dict[str, str]] = Field(None, description="Address details")
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, description="Emergency contact relation")
    
    # Bank Details
    bank_name: Optional[str] = Field(None, description="Bank name")
    bank_account: Optional[str] = Field(None, description="Bank account number")
    bank_ifsc: Optional[str] = Field(None, description="Bank IFSC code")
    bank_branch: Optional[str] = Field(None, description="Bank branch")
    
    # Documents
    documents: List[Dict[str, Any]] = Field(default_factory=list, description="Uploaded documents")
    
    # Skills and Qualifications
    skills: List[str] = Field(default_factory=list, description="Employee skills")
    qualifications: List[Dict[str, str]] = Field(default_factory=list, description="Educational qualifications")
    
    # Performance
    performance_rating: Optional[str] = Field(None, description="Current performance rating")
    last_review_date: Optional[date] = Field(None, description="Last performance review date")
    
    # System Fields
    is_active: bool = Field(default=True, description="Whether employee is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the record")
    last_modified_by: Optional[str] = Field(None, description="User who last modified the record")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "employees"
    #     # indexes = [
    #     #     "employee_code",
    #     #     "email",
    #     #     "department",
    #     #     "status",
    #     #     "joining_date",
    #     #     "is_active"
    #     # ]
    
    @validator('full_name', pre=True, always=True)
    def set_full_name(cls, v, values):
        if 'first_name' in values and 'last_name' in values:
            return f"{values['first_name']} {values['last_name']}"
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits')
        return v
    
    @validator('ctc')
    def validate_ctc(cls, v):
        if v <= 0:
            raise ValueError('CTC must be greater than 0')
        return v
    
    def get_age(self) -> Optional[int]:
        """Calculate employee age"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def get_experience_years(self) -> float:
        """Calculate total experience in years"""
        end_date = self.last_working_day if self.last_working_day else date.today()
        delta = end_date - self.joining_date
        return round(delta.days / 365.25, 2)
    
    def is_probation_period(self) -> bool:
        """Check if employee is in probation period"""
        if not self.confirmation_date:
            return True
        
        probation_end = self.joining_date.replace(day=self.joining_date.day + 90)  # 3 months probation
        return date.today() <= probation_end
    
    def get_monthly_salary(self) -> float:
        """Calculate monthly salary from CTC"""
        return self.ctc / 12
    
    def get_daily_wages(self) -> float:
        """Calculate daily wages"""
        return self.get_monthly_salary() / 30
    
    def get_hourly_wages(self) -> float:
        """Calculate hourly wages"""
        return self.get_daily_wages() / 8
    
    def add_document(self, doc_type: str, file_url: str, file_name: str = None):
        """Add document to employee record"""
        document = {
            "type": doc_type,
            "file_url": file_url,
            "file_name": file_name or file_url.split('/')[-1],
            "uploaded_at": datetime.utcnow()
        }
        self.documents.append(document)
        return document
    
    def get_document_by_type(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """Get document by type"""
        for doc in self.documents:
            if doc["type"] == doc_type:
                return doc
        return None
    
    def has_all_required_documents(self) -> bool:
        """Check if all required documents are uploaded"""
        required_docs = ["pan_card", "aadhaar_card", "bank_details", "offer_letter"]
        for doc_type in required_docs:
            if not self.get_document_by_type(doc_type):
                return False
        return True
    
    def update_status(self, new_status: EmployeeStatus, modified_by: str = None):
        """Update employee status"""
        self.status = new_status
        self.last_modified_by = modified_by
        self.updated_at = datetime.utcnow()
        
        # Update is_active based on status
        if new_status == EmployeeStatus.ACTIVE:
            self.is_active = True
        elif new_status in [EmployeeStatus.INACTIVE, EmployeeStatus.TERMINATED, EmployeeStatus.RESIGNED]:
            self.is_active = False
    
    def add_skill(self, skill: str):
        """Add skill to employee"""
        if skill not in self.skills:
            self.skills.append(skill)
    
    def remove_skill(self, skill: str):
        """Remove skill from employee"""
        if skill in self.skills:
            self.skills.remove(skill)
    
    def update_performance(self, rating: str, review_date: date = None):
        """Update performance rating"""
        self.performance_rating = rating
        self.last_review_date = review_date or date.today()
        self.updated_at = datetime.utcnow()
    
    def get_work_anniversary(self) -> Optional[date]:
        """Get work anniversary for current year"""
        if not self.joining_date:
            return None
        today = date.today()
        return date(today.year, self.joining_date.month, self.joining_date.day)
    
    def is_work_anniversary_today(self) -> bool:
        """Check if today is work anniversary"""
        anniversary = self.get_work_anniversary()
        return anniversary == date.today()
    
    def get_remaining_probation_days(self) -> Optional[int]:
        """Get remaining probation days"""
        if not self.joining_date or self.confirmation_date:
            return None
        
        probation_end = self.joining_date + timedelta(days=90)
        remaining = (probation_end - date.today()).days
        return max(0, remaining)
    
    def get_address_string(self) -> str:
        """Get formatted address string"""
        if not self.address:
            return ""
        
        parts = []
        if self.address.get("line1"):
            parts.append(self.address["line1"])
        if self.address.get("line2"):
            parts.append(self.address["line2"])
        if self.address.get("city"):
            parts.append(self.address["city"])
        if self.address.get("state"):
            parts.append(self.address["state"])
        if self.address.get("pincode"):
            parts.append(self.address["pincode"])
        if self.address.get("country"):
            parts.append(self.address["country"])
        
        return ", ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed fields"""
        data = self.dict()
        data.update({
            "age": self.get_age(),
            "experience_years": self.get_experience_years(),
            "monthly_salary": self.get_monthly_salary(),
            "daily_wages": self.get_daily_wages(),
            "hourly_wages": self.get_hourly_wages(),
            "is_probation_period": self.is_probation_period(),
            "has_all_required_documents": self.has_all_required_documents(),
            "work_anniversary": self.get_work_anniversary(),
            "is_work_anniversary_today": self.is_work_anniversary_today(),
            "remaining_probation_days": self.get_remaining_probation_days(),
            "address_string": self.get_address_string()
        })
        return data
