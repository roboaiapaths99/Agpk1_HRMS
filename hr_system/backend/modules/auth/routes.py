from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .schema import (
    UserLogin, UserRegister, UserChangePassword, UserForgotPassword, UserResetPassword,
    UserRefreshToken, TokenResponse, UserProfileUpdate, UserPreferences, TwoFactorSetup,
    TwoFactorVerify, PermissionCheck, RoleAssignment
)
from .service import AuthService
from ..user.model import User
from ..user.dependencies import get_current_user
from utils.logger import audit_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
auth_service = AuthService()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request
):
    """Register a new user"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    user = await auth_service.register_user(user_data)
    
    # Auto-login after registration
    login_data = UserLogin(email=user_data.email, password=user_data.password)
    return await auth_service.authenticate_user(login_data, client_ip, user_agent)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request
):
    """Authenticate user"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    return await auth_service.authenticate_user(login_data, client_ip, user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: UserRefreshToken):
    """Refresh access token"""
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user)
):
    """Logout user"""
    # In a real application, you would invalidate the token/session
    # For now, we'll just log the action
    audit_logger.log_authentication(
        current_user.email, "logout", "", success=True
    )
    
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    success = await auth_service.change_password(current_user, password_data)
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )


@router.post("/forgot-password")
async def forgot_password(forgot_data: UserForgotPassword):
    """Handle forgot password request"""
    success = await auth_service.forgot_password(forgot_data.email)
    
    if success:
        return {"message": "Password reset instructions sent to your email"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.post("/reset-password")
async def reset_password(reset_data: UserResetPassword):
    """Reset user password"""
    success = await auth_service.reset_password(reset_data)
    
    if success:
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )


@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(
    current_user: User = Depends(get_current_user)
):
    """Setup two-factor authentication"""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled"
        )
    
    return await auth_service.setup_two_factor(current_user)


@router.post("/2fa/enable")
async def enable_two_factor(
    code: str,
    current_user: User = Depends(get_current_user)
):
    """Enable two-factor authentication"""
    success = await auth_service.enable_two_factor(current_user, code)
    
    if success:
        return {"message": "Two-factor authentication enabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to enable two-factor authentication"
        )


@router.post("/2fa/disable")
async def disable_two_factor(
    password: str,
    current_user: User = Depends(get_current_user)
):
    """Disable two-factor authentication"""
    success = await auth_service.disable_two_factor(current_user, password)
    
    if success:
        return {"message": "Two-factor authentication disabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable two-factor authentication"
        )


@router.post("/2fa/verify", response_model=TokenResponse)
async def verify_two_factor(
    code: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify two-factor authentication code"""
    try:
        # Verify the temporary token
        payload = auth_service.security_manager.verify_token(credentials.credentials)
        
        if not payload.get("2fa_required"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor verification not required"
            )
        
        user_id = payload.get("sub")
        user = await auth_service.user_repository.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return await auth_service.verify_two_factor(user, code)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid two-factor code"
        )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "employee_id": current_user.employee_id,
        "avatar_url": current_user.avatar_url,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "email_notifications": current_user.email_notifications,
        "two_factor_enabled": current_user.two_factor_enabled
    }


@router.put("/me/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    updated_user = await auth_service.update_user_profile(current_user, profile_data)
    
    return {
        "id": str(updated_user.id),
        "email": updated_user.email,
        "username": updated_user.username,
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "avatar_url": updated_user.avatar_url,
        "email_notifications": updated_user.email_notifications
    }


@router.put("/me/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    updated_user = await auth_service.update_user_preferences(current_user, preferences)
    
    return {
        "email_notifications": updated_user.email_notifications,
        "two_factor_enabled": updated_user.two_factor_enabled
    }


@router.post("/verify-permission")
async def verify_permission(
    permission_check: PermissionCheck,
    current_user: User = Depends(get_current_user)
):
    """Verify user permission"""
    has_permission = await auth_service.verify_permission(
        current_user, permission_check.resource, permission_check.action
    )
    
    return {
        "has_permission": has_permission,
        "resource": permission_check.resource,
        "action": permission_check.action,
        "user_role": current_user.role.value
    }


@router.post("/assign-role")
async def assign_role(
    role_assignment: RoleAssignment,
    current_user: User = Depends(get_current_user)
):
    """Assign role to user (Admin only)"""
    # Check if current user has permission to assign roles
    has_permission = await auth_service.verify_permission(current_user, "users", "update")
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign roles"
        )
    
    updated_user = await auth_service.assign_role(
        role_assignment.user_id, role_assignment, current_user.username
    )
    
    return {
        "id": str(updated_user.id),
        "email": updated_user.email,
        "username": updated_user.username,
        "role": updated_user.role.value,
        "permissions": updated_user.permissions
    }


@router.get("/activities")
async def get_user_activities(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user activity log"""
    activities = await auth_service.get_user_activities(str(current_user.id), limit)
    
    return {"activities": activities}


@router.get("/sessions")
async def get_user_sessions(current_user: User = Depends(get_current_user)):
    """Get active user sessions"""
    sessions = await auth_service.get_user_sessions(str(current_user.id))
    
    return {"sessions": sessions}


@router.delete("/sessions")
async def revoke_user_sessions(
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Revoke user sessions"""
    success = await auth_service.revoke_user_sessions(str(current_user.id), session_id)
    
    if success:
        return {"message": "Sessions revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke sessions"
        )


@router.get("/password-requirements")
async def get_password_requirements():
    """Get password requirements"""
    requirements = auth_service.get_password_requirements()
    
    return requirements


@router.get("/security-settings")
async def get_security_settings(current_user: User = Depends(get_current_user)):
    """Get security settings"""
    settings = auth_service.get_security_settings()
    
    # Add user-specific security info
    settings.update({
        "user_two_factor_enabled": current_user.two_factor_enabled,
        "user_last_password_change": current_user.password_changed_at,
        "user_login_count": current_user.login_count,
        "user_failed_attempts": current_user.failed_login_attempts
    })
    
    return settings


@router.post("/validate-token")
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate JWT token"""
    try:
        payload = auth_service.security_manager.verify_token(credentials.credentials)
        
        return {
            "valid": True,
            "expires_at": payload.get("exp"),
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
        
    except Exception:
        return {"valid": False}


@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get user permissions"""
    from core.security import RolePermissions
    
    role_permissions = RolePermissions.ROLES.get(current_user.role.value, {})
    all_permissions = set()
    
    for resource, actions in role_permissions.items():
        for action in actions:
            all_permissions.add(f"{resource}:{action}")
    
    # Add custom permissions
    for permission in current_user.permissions:
        all_permissions.add(permission)
    
    return {
        "role": current_user.role.value,
        "permissions": list(all_permissions),
        "custom_permissions": current_user.permissions
    }
