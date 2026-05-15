from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field, EmailStr
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


class User(Document):
    """User model for authentication and authorization"""
    
    # Basic Information
    email: Indexed(EmailStr, unique=True) = Field(..., description="User email address")
    username: Indexed(str, unique=True) = Field(..., description="Unique username")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    
    # Authentication
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Account status")
    
    # Role and Permissions
    role: UserRole = Field(default=UserRole.EMPLOYEE, description="User role")
    permissions: List[str] = Field(default_factory=list, description="Additional permissions")
    
    # Employee Reference (if user is an employee)
    employee_id: Optional[str] = Field(None, description="Reference to employee document")
    
    # Profile Information
    phone: Optional[str] = Field(None, description="Phone number")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    
    # Status and Metadata
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(default=0, description="Number of logins")
    
    # Security
    failed_login_attempts: int = Field(default=0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    password_changed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Audit Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created this account")
    
    # Settings
    email_notifications: bool = Field(default=True, description="Email notification preferences")
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication status")
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username", 
            "role",
            "status",
            "employee_id",
            "created_at"
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True
    
    async def increment_login_count(self):
        """Increment login count and update last login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.failed_login_attempts = 0  # Reset failed attempts on successful login
        await self.save()
    
    async def increment_failed_login(self):
        """Increment failed login attempts and lock account if necessary"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
            self.status = UserStatus.SUSPENDED
        
        await self.save()
    
    async def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
        if self.status == UserStatus.SUSPENDED:
            self.status = UserStatus.ACTIVE
        await self.save()
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    @property
    def display_name(self) -> str:
        """Get display name for the user"""
        return self.full_name or self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        # Check role-based permissions
        from ...core.security import RolePermissions
        role_perms = RolePermissions.ROLES.get(self.role.value, {})
        
        for resource, actions in role_perms.items():
            if permission in actions:
                return True
        
        # Check additional permissions
        return permission in self.permissions
