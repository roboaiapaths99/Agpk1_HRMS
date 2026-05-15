from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=1, description="Password")


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="Email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower()
    
    @validator('username')
    def validate_username(cls, v):
        return v.lower()


class UserChangePassword(BaseModel):
    """User password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserForgotPassword(BaseModel):
    """Forgot password schema"""
    email: EmailStr = Field(..., description="Email address")


class UserResetPassword(BaseModel):
    """Reset password schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class UserRefreshToken(BaseModel):
    """Refresh token schema"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None)
    avatar_url: Optional[str] = Field(None)
    email_notifications: Optional[bool] = None


class UserPreferences(BaseModel):
    """User preferences schema"""
    email_notifications: bool = Field(default=True)
    two_factor_enabled: bool = Field(default=False)


class TwoFactorSetup(BaseModel):
    """Two-factor setup response"""
    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorVerify(BaseModel):
    """Two-factor verification"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit code")


class PermissionCheck(BaseModel):
    """Permission check schema"""
    resource: str
    action: str


class RoleAssignment(BaseModel):
    """Role assignment schema"""
    role: str
