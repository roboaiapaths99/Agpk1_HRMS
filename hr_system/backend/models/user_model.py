from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
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
    PENDING = "pending"


class User(Document):
    """User document for MongoDB"""
    
    # Basic Information
    email: Indexed(str) = Field(..., description="Email address")
    username: Indexed(str) = Field(..., description="Username")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Authentication
    hashed_password: str = Field(..., description="Hashed password")
    salt: Optional[str] = Field(None, description="Password salt")
    
    # Role and Status
    role: UserRole = Field(default=UserRole.EMPLOYEE, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_verified: bool = Field(default=False, description="Whether user is verified")
    
    # Employee Link
    employee_id: Optional[str] = Field(None, description="Reference to employee profile")
    
    # Profile Information
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")
    bio: Optional[str] = Field(None, description="User bio")
    
    # Security Settings
    two_factor_enabled: bool = Field(default=False, description="Two-factor authentication enabled")
    two_factor_secret: Optional[str] = Field(None, description="Two-factor secret")
    two_factor_backup_codes: List[str] = Field(default_factory=list, description="Two-factor backup codes")
    
    # Login Tracking
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(default=0, description="Total login count")
    failed_login_attempts: int = Field(default=0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    
    # Password Management
    password_changed_at: Optional[datetime] = Field(None, description="Password last changed")
    password_reset_token: Optional[str] = Field(None, description="Password reset token")
    password_reset_expires: Optional[datetime] = Field(None, description="Password reset token expiry")
    
    # Permissions
    permissions: List[str] = Field(default_factory=list, description="Custom permissions")
    
    # Preferences
    email_notifications: bool = Field(default=True, description="Email notifications enabled")
    push_notifications: bool = Field(default=True, description="Push notifications enabled")
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="Timezone")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created this account")
    last_modified_by: Optional[str] = Field(None, description="User who last modified this account")
    
    # Session Management
    refresh_tokens: List[str] = Field(default_factory=list, description="Active refresh tokens")
    session_tokens: List[Dict[str, Any]] = Field(default_factory=list, description="Active session tokens")
    
    # Additional Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "users"
    #     # indexes = [
    #     #     "email",
    #     #     "username", 
    #     #     "role",
    #     #     "status",
    #     #     "is_active",
    #     #     "employee_id",
    #     #     "last_login",
    #     #     "created_at"
    #     # ]
    
    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email is required')
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('username')
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain alphanumeric characters, hyphens, and underscores')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('-', '').replace(' ', '').replace('+', '').isdigit():
            raise ValueError('Phone number must contain only digits')
        return v
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, hours: int = 24):
        """Lock account for specified hours"""
        self.locked_until = datetime.utcnow() + timedelta(hours=hours)
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        self.updated_at = datetime.utcnow()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def increment_login_count(self):
        """Increment login count and update last login"""
        self.login_count += 1
        self.last_login = datetime.utcnow()
        self.reset_failed_attempts()
    
    def is_password_expired(self, days: int = 90) -> bool:
        """Check if password is expired"""
        if not self.password_changed_at:
            return True
        
        expiry_date = self.password_changed_at + timedelta(days=days)
        return datetime.utcnow() > expiry_date
    
    def get_password_expiry_days(self, days: int = 90) -> Optional[int]:
        """Get days until password expiry"""
        if not self.password_changed_at:
            return None
        
        expiry_date = self.password_changed_at + timedelta(days=days)
        remaining = (expiry_date - datetime.utcnow()).days
        return max(0, remaining)
    
    def add_permission(self, permission: str):
        """Add custom permission"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.utcnow()
    
    def remove_permission(self, permission: str):
        """Remove custom permission"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = datetime.utcnow()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has specific role"""
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_hr(self) -> bool:
        """Check if user is HR staff"""
        return self.role in [UserRole.HR_MANAGER, UserRole.HR_EXECUTIVE]
    
    def is_hr_manager(self) -> bool:
        """Check if user is HR manager"""
        return self.role == UserRole.HR_MANAGER
    
    def is_employee(self) -> bool:
        """Check if user is regular employee"""
        return self.role == UserRole.EMPLOYEE
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role in [UserRole.ADMIN, UserRole.HR_MANAGER]
    
    def can_access_payroll(self) -> bool:
        """Check if user can access payroll"""
        return self.role in [UserRole.ADMIN, UserRole.HR_MANAGER, UserRole.HR_EXECUTIVE]
    
    def can_manage_employees(self) -> bool:
        """Check if user can manage employees"""
        return self.role in [UserRole.ADMIN, UserRole.HR_MANAGER, UserRole.HR_EXECUTIVE]
    
    def add_refresh_token(self, token: str):
        """Add refresh token"""
        if token not in self.refresh_tokens:
            self.refresh_tokens.append(token)
            self.updated_at = datetime.utcnow()
    
    def remove_refresh_token(self, token: str):
        """Remove refresh token"""
        if token in self.refresh_tokens:
            self.refresh_tokens.remove(token)
            self.updated_at = datetime.utcnow()
    
    def add_session_token(self, token: str, expires_at: datetime, device_info: Dict[str, Any] = None):
        """Add session token"""
        session = {
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "device_info": device_info or {}
        }
        self.session_tokens.append(session)
        self.updated_at = datetime.utcnow()
        
        # Remove expired sessions
        self.cleanup_expired_sessions()
    
    def remove_session_token(self, token: str):
        """Remove session token"""
        self.session_tokens = [
            session for session in self.session_tokens 
            if session["token"] != token
        ]
        self.updated_at = datetime.utcnow()
    
    def cleanup_expired_sessions(self):
        """Remove expired session tokens"""
        now = datetime.utcnow()
        self.session_tokens = [
            session for session in self.session_tokens 
            if session["expires_at"] > now
        ]
        self.updated_at = datetime.utcnow()
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get active sessions"""
        self.cleanup_expired_sessions()
        return self.session_tokens
    
    def revoke_all_sessions(self):
        """Revoke all session tokens"""
        self.session_tokens.clear()
        self.refresh_tokens.clear()
        self.updated_at = datetime.utcnow()
    
    def generate_password_reset_token(self, hours: int = 1):
        """Generate password reset token"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=hours)
        self.updated_at = datetime.utcnow()
        return token
    
    def clear_password_reset_token(self):
        """Clear password reset token"""
        self.password_reset_token = None
        self.password_reset_expires = None
        self.updated_at = datetime.utcnow()
    
    def is_password_reset_token_valid(self, token: str) -> bool:
        """Check if password reset token is valid"""
        if not self.password_reset_token or not self.password_reset_expires:
            return False
        
        return (
            self.password_reset_token == token and 
            datetime.utcnow() < self.password_reset_expires
        )
    
    def enable_two_factor(self, secret: str, backup_codes: List[str]):
        """Enable two-factor authentication"""
        self.two_factor_enabled = True
        self.two_factor_secret = secret
        self.two_factor_backup_codes = backup_codes
        self.updated_at = datetime.utcnow()
    
    def disable_two_factor(self):
        """Disable two-factor authentication"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        self.two_factor_backup_codes = []
        self.updated_at = datetime.utcnow()
    
    def use_backup_code(self, code: str) -> bool:
        """Use backup code for 2FA"""
        if code in self.two_factor_backup_codes:
            self.two_factor_backup_codes.remove(code)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_last_login(self, ip_address: str = None, user_agent: str = None):
        """Update last login information"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.reset_failed_attempts()
        
        # Store login metadata
        if not self.metadata:
            self.metadata = {}
        
        self.metadata["last_login_ip"] = ip_address
        self.metadata["last_login_user_agent"] = user_agent
        self.updated_at = datetime.utcnow()
    
    def get_user_summary(self) -> Dict[str, Any]:
        """Get user summary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "employee_id": self.employee_id,
            "two_factor_enabled": self.two_factor_enabled,
            "last_login": self.last_login,
            "login_count": self.login_count,
            "created_at": self.created_at,
            "permissions": self.permissions,
            "active_sessions": len(self.get_active_sessions())
        }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        return {
            "is_locked": self.is_locked(),
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": self.locked_until,
            "two_factor_enabled": self.two_factor_enabled,
            "password_changed_at": self.password_changed_at,
            "password_expiry_days": self.get_password_expiry_days(),
            "active_sessions": len(self.get_active_sessions()),
            "refresh_tokens": len(self.refresh_tokens),
            "last_login": self.last_login
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed fields"""
        data = self.dict()
        data.update({
            "is_locked": self.is_locked(),
            "is_admin": self.is_admin(),
            "is_hr": self.is_hr(),
            "is_hr_manager": self.is_hr_manager(),
            "is_employee": self.is_employee(),
            "password_expiry_days": self.get_password_expiry_days(),
            "user_summary": self.get_user_summary(),
            "security_summary": self.get_security_summary()
        })
        return data
