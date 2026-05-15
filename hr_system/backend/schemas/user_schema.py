from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    HR_EXECUTIVE = "hr_executive"
    EMPLOYEE = "employee"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(default=UserRole.EMPLOYEE, description="User role")
    is_active: bool = Field(default=True, description="Account status")
    employee_id: Optional[str] = Field(None, description="Reference to employee document")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    email_notifications: bool = Field(default=True, description="Email notification preferences")
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication status")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()
    
    @validator('full_name')
    def validate_name(cls, v):
        if not v.replace(' ', '').replace('-', '').replace('.', '').isalpha():
            raise ValueError('Name must contain only letters, spaces, hyphens, and dots')
        return v.title()


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=8, description="Password")
    created_by: Optional[str] = Field(None, description="User who created this account")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Password must contain uppercase, lowercase, digit, and special character')
        
        return v


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Account status")
    employee_id: Optional[str] = Field(None, description="Reference to employee document")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    email_notifications: Optional[bool] = Field(None, description="Email notification preferences")
    two_factor_enabled: Optional[bool] = Field(None, description="Two-factor authentication status")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    employee_id: Optional[str]
    avatar_url: Optional[str]
    last_login: Optional[datetime]
    login_count: int
    failed_login_attempts: int
    locked_until: Optional[datetime]
    password_changed_at: datetime
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    last_modified_by: Optional[str]
    email_notifications: bool
    two_factor_enabled: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
