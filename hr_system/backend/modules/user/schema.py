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


class UserSearch(BaseModel):
    """Schema for user search"""
    query: Optional[str] = Field(None, description="Search query")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    status: Optional[UserStatus] = Field(None, description="Filter by status")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    last_login_after: Optional[datetime] = Field(None, description="Last login after date")
    last_login_before: Optional[datetime] = Field(None, description="Last login before date")


class UserBulkAction(BaseModel):
    """Schema for bulk user actions"""
    user_ids: List[str] = Field(..., description="List of user IDs")
    action: str = Field(..., description="Action to perform")
    parameters: Optional[dict] = Field(None, description="Action parameters")


class UserPasswordUpdate(BaseModel):
    """Schema for password update"""
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


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    email_notifications: bool = Field(default=True, description="Email notification preferences")
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication status")
    language: str = Field(default="en", description="Language preference")
    timezone: str = Field(default="UTC", description="Timezone preference")
    theme: str = Field(default="light", description="UI theme preference")


class UserStatistics(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    role_breakdown: List[dict]
    status_breakdown: List[dict]
    recent_registrations: int
    never_logged_in_count: int
    inactive_users_count: int


class UserActivity(BaseModel):
    """Schema for user activity"""
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
    """Schema for user session"""
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


class UserProfile(BaseModel):
    """Schema for user profile"""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    employee_id: Optional[str]
    avatar_url: Optional[str]
    email_notifications: bool
    two_factor_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    preferences: Optional[UserPreferences]
    
    class Config:
        from_attributes = True


class UserSecurity(BaseModel):
    """Schema for user security information"""
    id: str
    email: str
    failed_login_attempts: int
    locked_until: Optional[datetime]
    last_login: Optional[datetime]
    last_login_ip: Optional[str]
    password_changed_at: datetime
    two_factor_enabled: bool
    two_factor_secret_set: bool
    login_count: int
    
    class Config:
        from_attributes = True


class UserPermission(BaseModel):
    """Schema for user permission"""
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    granted: bool = Field(..., description="Permission granted")
    granted_by: Optional[str] = Field(None, description="Who granted the permission")
    granted_at: Optional[datetime] = Field(None, description="When permission was granted")
    expires_at: Optional[datetime] = Field(None, description="When permission expires")


class UserPermissionCheck(BaseModel):
    """Schema for permission check"""
    user_id: str = Field(..., description="User ID")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")


class UserPermissionResponse(BaseModel):
    """Schema for permission check response"""
    user_id: str
    resource: str
    action: str
    has_permission: bool
    role: str
    permissions: List[str]


class UserLoginHistory(BaseModel):
    """Schema for user login history"""
    id: str
    user_id: str
    login_time: datetime
    logout_time: Optional[datetime]
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: Optional[str]
    session_duration: Optional[int]  # in seconds
    
    class Config:
        from_attributes = True


class UserBulkUpdate(BaseModel):
    """Schema for bulk user update"""
    user_ids: List[str] = Field(..., description="List of user IDs")
    update_data: dict = Field(..., description="Data to update")
    validate_before_update: bool = Field(default=True, description="Validate data before updating")


class UserExport(BaseModel):
    """Schema for user export"""
    format: str = Field(default="csv", description="Export format (csv, xlsx, json)")
    fields: List[str] = Field(default=[], description="Fields to export")
    filters: Optional[UserSearch] = Field(None, description="Filters to apply")
    include_inactive: bool = Field(default=False, description="Include inactive users")


class UserImport(BaseModel):
    """Schema for user import"""
    file_type: str = Field(default="csv", description="File type (csv, xlsx, json)")
    update_existing: bool = Field(default=False, description="Update existing users")
    send_welcome_email: bool = Field(default=True, description="Send welcome email to new users")
    default_role: UserRole = Field(default=UserRole.EMPLOYEE, description="Default role for new users")


class UserNotification(BaseModel):
    """Schema for user notification"""
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserNotificationSettings(BaseModel):
    """Schema for user notification settings"""
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=False)
    sms_notifications: bool = Field(default=False)
    notification_types: dict = Field(default_factory=dict)
