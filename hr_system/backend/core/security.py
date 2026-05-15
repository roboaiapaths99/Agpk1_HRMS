from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Truncate password to 72 characters as bcrypt limitation
        return pwd_context.verify(plain_password[:72], hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        # Truncate password to 72 characters as bcrypt limitation
        return pwd_context.hash(password[:72])
    
    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_password_requirements() -> dict:
        """Get password requirements"""
        return {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True,
            "no_common_passwords": True
        }


class RolePermissions:
    """Role-based access control permissions"""
    
    ROLES = {
        "admin": {
            "employees": ["create", "read", "update", "delete"],
            "onboarding": ["create", "read", "update", "delete"],
            "payroll": ["create", "read", "update", "delete", "approve", "lock"],
            "exit_management": ["create", "read", "update", "delete"],
            "users": ["create", "read", "update", "delete"],
            "analytics": ["read", "create", "update", "delete"],
            "system": ["read", "update"]
        },
        "hr_manager": {
            "employees": ["create", "read", "update"],
            "onboarding": ["create", "read", "update"],
            "payroll": ["create", "read", "update", "approve"],
            "exit_management": ["create", "read", "update"],
            "analytics": ["read"]
        },
        "hr_executive": {
            "employees": ["read"],
            "onboarding": ["read", "update"],
            "payroll": ["read"],
            "exit_management": ["read", "update"],
            "analytics": ["read"]
        },
        "employee": {
            "employees": ["read"],
            "onboarding": ["read"],
            "payroll": ["read"],
            "exit_management": ["read"]
        }
    }
    
    @classmethod
    def has_permission(cls, role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource and action"""
        role_permissions = cls.ROLES.get(role, {})
        resource_permissions = role_permissions.get(resource, [])
        return action in resource_permissions
