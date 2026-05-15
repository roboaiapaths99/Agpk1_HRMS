from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")
    remember_me: bool = Field(default=False, description="Remember me option")


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Confirm password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
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


class UserChangePassword(BaseModel):
    """User password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
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


class UserForgotPassword(BaseModel):
    """User forgot password schema"""
    email: EmailStr = Field(..., description="User email")


class UserResetPassword(BaseModel):
    """User reset password schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserRefreshToken(BaseModel):
    """User refresh token schema"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    employee_id: Optional[str]
    avatar_url: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    email_notifications: bool
    two_factor_enabled: bool
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None)
    avatar_url: Optional[str] = Field(None)
    email_notifications: Optional[bool] = Field(None)


class UserPreferences(BaseModel):
    """User preferences schema"""
    email_notifications: bool = Field(default=True)
    two_factor_enabled: bool = Field(default=False)
    language: str = Field(default="en")
    timezone: str = Field(default="UTC")
    theme: str = Field(default="light")


class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup schema"""
    secret: str = Field(..., description="2FA secret")
    qr_code: str = Field(..., description="QR code for 2FA")
    backup_codes: list[str] = Field(..., description="Backup codes")


class TwoFactorVerify(BaseModel):
    """Two-factor verification schema"""
    code: str = Field(..., min_length=6, max_length=6, description="2FA code")
    remember_device: bool = Field(default=False, description="Remember device")


class UserActivity(BaseModel):
    """User activity schema"""
    id: str
    user_id: str
    action: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    details: Optional[dict]
    
    class Config:
        from_attributes = True


class UserSession(BaseModel):
    """User session schema"""
    id: str
    user_id: str
    session_token: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    last_activity: datetime
    
    class Config:
        from_attributes = True


class PermissionCheck(BaseModel):
    """Permission check schema"""
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    user_id: Optional[str] = Field(None, description="User ID (optional, uses current user if not provided)")


class RoleAssignment(BaseModel):
    """Role assignment schema"""
    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="Role name")
    permissions: list[str] = Field(default_factory=list, description="Additional permissions")


class PasswordPolicy(BaseModel):
    """Password policy schema"""
    min_length: int = Field(default=8, description="Minimum password length")
    require_uppercase: bool = Field(default=True, description="Require uppercase letter")
    require_lowercase: bool = Field(default=True, description="Require lowercase letter")
    require_digit: bool = Field(default=True, description="Require digit")
    require_special: bool = Field(default=True, description="Require special character")
    max_age_days: int = Field(default=90, description="Maximum password age in days")
    prevent_reuse: int = Field(default=5, description="Number of previous passwords to prevent reuse")


class LoginAttempt(BaseModel):
    """Login attempt schema"""
    email: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str] = None


class SecuritySettings(BaseModel):
    """Security settings schema"""
    max_login_attempts: int = Field(default=5, description="Maximum login attempts before lockout")
    lockout_duration_minutes: int = Field(default=30, description="Account lockout duration in minutes")
    session_timeout_minutes: int = Field(default=480, description="Session timeout in minutes")
    require_two_factor: bool = Field(default=False, description="Require two-factor authentication")
    password_policy: PasswordPolicy = Field(default_factory=PasswordPolicy)


class AuditLog(BaseModel):
    """Audit log schema"""
    id: str
    user_id: Optional[str]
    action: str
    resource: str
    resource_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: dict
    success: bool
    
    class Config:
        from_attributes = True
