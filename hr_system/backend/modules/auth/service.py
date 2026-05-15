from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import pyotp
import qrcode
import io
import base64

from ..user.model import User, UserRole, UserStatus
from ..user.repository import UserRepository
from .schema import (
    UserLogin, UserRegister, UserChangePassword, UserForgotPassword, UserResetPassword,
    UserRefreshToken, TokenResponse, UserProfileUpdate, UserPreferences, TwoFactorSetup,
    TwoFactorVerify, PermissionCheck, RoleAssignment
)
from core.security import SecurityManager
from core.config import settings
from utils.logger import audit_logger


class AuthService:
    """Service layer for authentication operations"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.security_manager = SecurityManager()
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = await self.user_repository.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        try:
            # Create new user
            hashed_password = self.security_manager.get_password_hash(user_data.password)
            
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                phone=user_data.phone,
                hashed_password=hashed_password,
                role=UserRole.EMPLOYEE,  # Default role
                is_active=True,
                created_by="self"
            )
            
            await user.insert()
            
            # Log the action
            audit_logger.log_authentication(
                user.email, "user_registered", "", success=True
            )
            
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )
    
    async def authenticate_user(self, login_data: UserLogin, ip_address: str, user_agent: str) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Get user by email
        user = await self.user_repository.get_user_by_email(login_data.email)
        if not user:
            # Log failed attempt
            audit_logger.log_authentication(
                login_data.email, "login_failed", ip_address, success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.is_active:
            audit_logger.log_authentication(
                user.email, "login_blocked_inactive", ip_address, success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Check if account is locked
        if user.is_locked():
            audit_logger.log_authentication(
                user.email, "login_blocked_locked", ip_address, success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked"
            )
        
        # Verify password
        if not self.security_manager.verify_password(login_data.password, user.hashed_password):
            # Increment failed attempts
            await user.increment_failed_login()
            
            audit_logger.log_authentication(
                user.email, "login_failed_password", ip_address, success=False
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if two-factor is enabled
        if user.two_factor_enabled:
            # Return a temporary token for 2FA verification
            temp_token = self.security_manager.create_access_token(
                data={"sub": str(user.id), "email": user.email, "2fa_required": True},
                expires_delta=timedelta(minutes=10)
            )
            
            return TokenResponse(
                access_token=temp_token,
                refresh_token="",  # No refresh token for 2FA step
                token_type="bearer",
                expires_in=600,  # 10 minutes
                user={
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "two_factor_enabled": True,
                    "2fa_required": True
                }
            )
        
        # Generate tokens
        access_token = self.security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}
        )
        
        refresh_token = self.security_manager.create_access_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=30)
        )
        
        # Update login count and last login
        await user.increment_login_count()
        
        # Log successful login
        audit_logger.log_authentication(
            user.email, "login_success", ip_address, success=True
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "employee_id": user.employee_id,
                "two_factor_enabled": user.two_factor_enabled
            }
        )
    
    async def verify_two_factor(self, user: User, code: str) -> TokenResponse:
        """Verify two-factor authentication code"""
        if not user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is not enabled"
            )
        
        # Verify TOTP code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor code"
            )
        
        # Generate final tokens
        access_token = self.security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}
        )
        
        refresh_token = self.security_manager.create_access_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=30)
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "employee_id": user.employee_id,
                "two_factor_enabled": user.two_factor_enabled
            }
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            payload = self.security_manager.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user_id = payload.get("sub")
            user = await self.user_repository.get_user_by_id(user_id)
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Generate new access token
            access_token = self.security_manager.create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role.value}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Keep the same refresh token
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "employee_id": user.employee_id,
                    "two_factor_enabled": user.two_factor_enabled
                }
            )
            
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def change_password(self, user: User, password_data: UserChangePassword) -> bool:
        """Change user password"""
        # Verify current password
        if not self.security_manager.verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = self.security_manager.get_password_hash(password_data.new_password)
        user.password_changed_at = datetime.utcnow()
        await user.save()
        
        # Log the action
        audit_logger.log_authentication(
            user.email, "password_changed", "", success=True
        )
        
        return True
    
    async def forgot_password(self, email: str) -> bool:
        """Handle forgot password request"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not
            return True
        
        # Generate reset token
        reset_token = self.security_manager.create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # In a real application, you would send this token via email
        # For now, we'll just log it
        print(f"Password reset token for {email}: {reset_token}")
        
        # Log the action
        audit_logger.log_authentication(
            user.email, "password_reset_requested", "", success=True
        )
        
        return True
    
    async def reset_password(self, reset_data: UserResetPassword) -> bool:
        """Reset user password"""
        try:
            # Verify reset token
            payload = self.security_manager.verify_token(reset_data.token)
            
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            user_id = payload.get("sub")
            user = await self.user_repository.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update password
            user.hashed_password = self.security_manager.get_password_hash(reset_data.new_password)
            user.password_changed_at = datetime.utcnow()
            await user.reset_failed_attempts()
            await user.save()
            
            # Log the action
            audit_logger.log_authentication(
                user.email, "password_reset_completed", "", success=True
            )
            
            return True
            
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    async def setup_two_factor(self, user: User) -> TwoFactorSetup:
        """Setup two-factor authentication"""
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=settings.APP_NAME
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        # Store secret temporarily (user needs to verify before enabling)
        user.two_factor_secret = secret
        user.two_factor_backup_codes = backup_codes
        await user.save()
        
        return TwoFactorSetup(
            secret=secret,
            qr_code=qr_code,
            backup_codes=backup_codes
        )
    
    async def enable_two_factor(self, user: User, code: str) -> bool:
        """Enable two-factor authentication"""
        if not user.two_factor_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor setup not initiated"
            )
        
        # Verify code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Enable 2FA
        user.two_factor_enabled = True
        await user.save()
        
        # Log the action
        audit_logger.log_authentication(
            user.email, "2fa_enabled", "", success=True
        )
        
        return True
    
    async def disable_two_factor(self, user: User, password: str) -> bool:
        """Disable two-factor authentication"""
        # Verify password
        if not self.security_manager.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        # Disable 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.two_factor_backup_codes = []
        await user.save()
        
        # Log the action
        audit_logger.log_authentication(
            user.email, "2fa_disabled", "", success=True
        )
        
        return True
    
    async def verify_permission(self, user: User, resource: str, action: str) -> bool:
        """Verify user permission"""
        from core.security import RolePermissions
        return RolePermissions.has_permission(user.role.value, resource, action)
    
    async def assign_role(self, user_id: str, role_assignment: RoleAssignment, assigned_by: str) -> User:
        """Assign role to user"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        try:
            # Validate role
            new_role = UserRole(role_assignment.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        
        # Update user role and permissions
        user.role = new_role
        user.permissions = role_assignment.permissions
        await user.save()
        
        # Log the action
        audit_logger.log_user_action(
            assigned_by, "role_assigned", user_id,
            f"Assigned role {role_assignment.role} to user {user.email}"
        )
        
        return user
    
    async def update_user_profile(self, user: User, profile_data: UserProfileUpdate) -> User:
        """Update user profile"""
        update_dict = profile_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        # Log the action
        audit_logger.log_user_action(
            str(user.id), "profile_updated", str(user.id),
            "Updated user profile"
        )
        
        return user
    
    async def update_user_preferences(self, user: User, preferences: UserPreferences) -> User:
        """Update user preferences"""
        user.email_notifications = preferences.email_notifications
        user.two_factor_enabled = preferences.two_factor_enabled
        await user.save()
        
        return user
    
    async def get_user_activities(self, user_id: str, limit: int = 50) -> list:
        """Get user activity log"""
        # This would integrate with an activity logging system
        # For now, return empty list
        return []
    
    async def get_user_sessions(self, user_id: str) -> list:
        """Get active user sessions"""
        # This would integrate with a session management system
        # For now, return empty list
        return []
    
    async def revoke_user_sessions(self, user_id: str, session_id: Optional[str] = None) -> bool:
        """Revoke user sessions"""
        # This would integrate with a session management system
        # For now, return True
        return True
    
    def get_password_requirements(self) -> Dict[str, Any]:
        """Get password requirements"""
        return self.security_manager.get_password_requirements()
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings"""
        return {
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "session_timeout_minutes": 480,
            "require_two_factor": False,
            "password_policy": self.get_password_requirements()
        }
