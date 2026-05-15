from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List

from services.user_service import UserService
from schemas.user_schema import UserResponse, UserListResponse
from modules.auth.dependencies import get_current_user, require_permission
from modules.user.model import User, UserRole, UserStatus

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of users with pagination and filtering"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    result = await user_service.get_users_list(
        page, page_size, search, role, status, sort_by, sort_order
    )
    
    return UserListResponse(**result)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    # Users can view their own profile, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "read")
    
    user = await user_service.get_user_by_id(user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    # Users can update their own profile, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "update")
    
    # Restrict fields for self-update
    if current_user.id == user_id:
        allowed_fields = ["full_name", "phone", "avatar_url", "email_notifications"]
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        update_data = filtered_data
    
    user = await user_service.update_user_profile(user_id, update_data, current_user.username)
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Deactivate user account"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    # Cannot deactivate yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = await user_service.deactivate_user(user_id, current_user.username)
    return user


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Activate user account"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    user = await user_service.activate_user(user_id, current_user.username)
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_current_user)
):
    """Update user role"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    # Cannot change your own role
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user = await user_service.update_user_role(user_id, new_role, current_user.username)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user (soft delete)"""
    # Check permission
    require_permission(current_user, "users", "delete")
    
    # Cannot delete yourself
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = await user_service.delete_user(user_id, current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.get("/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: UserRole,
    current_user: User = Depends(get_current_user)
):
    """Get users by role"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_users_by_role(role)
    return users


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Result limit"),
    current_user: User = Depends(get_current_user)
):
    """Search users"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.search_users(q, limit)
    return users


@router.get("/statistics/overview")
async def get_user_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get user statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await user_service.get_user_statistics()
    return stats


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    new_password: str,
    current_user: User = Depends(get_current_user)
):
    """Reset user password"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    # Cannot reset your own password this way
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use change password endpoint for your own account"
        )
    
    user = await user_service.reset_user_password(user_id, new_password, current_user.username)
    
    return {"message": "Password reset successfully"}


@router.post("/{user_id}/unlock")
async def unlock_user_account(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unlock user account"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    user = await user_service.unlock_user_account(user_id, current_user.username)
    
    return {"message": "Account unlocked successfully"}


@router.get("/failed-logins", response_model=List[UserResponse])
async def get_users_with_failed_logins(
    failed_attempts: int = Query(3, ge=1, description="Minimum failed attempts"),
    current_user: User = Depends(get_current_user)
):
    """Get users with failed login attempts"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_users_with_failed_logins(failed_attempts)
    return users


@router.get("/inactive", response_model=List[UserResponse])
async def get_inactive_users(
    days: int = Query(30, ge=1, le=365, description="Days of inactivity"),
    current_user: User = Depends(get_current_user)
):
    """Get inactive users"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_inactive_users(days)
    return users


@router.post("/bulk-update")
async def bulk_update_users(
    user_ids: List[str],
    update_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Bulk update users"""
    # Check permission
    require_permission(current_user, "users", "update")
    
    result = await user_service.bulk_update_users(user_ids, update_data, current_user.username)
    return result


@router.get("/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user permissions"""
    # Users can view their own permissions, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "read")
    
    permissions = await user_service.get_user_permissions(user_id)
    
    return {
        "user_id": user_id,
        "permissions": permissions
    }


@router.post("/{user_id}/check-permission")
async def check_user_permission(
    user_id: str,
    resource: str,
    action: str,
    current_user: User = Depends(get_current_user)
):
    """Check if user has specific permission"""
    # Users can check their own permissions, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "read")
    
    has_permission = await user_service.check_user_permission(user_id, resource, action)
    
    return {
        "user_id": user_id,
        "resource": resource,
        "action": action,
        "has_permission": has_permission
    }


@router.get("/expiring-passwords", response_model=List[UserResponse])
async def get_users_expiring_passwords(
    days: int = Query(7, ge=1, le=90, description="Days until expiration"),
    current_user: User = Depends(get_current_user)
):
    """Get users with passwords expiring soon"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_users_expiring_passwords(days)
    return users


@router.get("/2fa-enabled", response_model=List[UserResponse])
async def get_users_with_2fa_enabled(
    current_user: User = Depends(get_current_user)
):
    """Get users with two-factor authentication enabled"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_users_with_2fa_enabled()
    return users


@router.get("/without-2fa", response_model=List[UserResponse])
async def get_users_without_2fa(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    current_user: User = Depends(get_current_user)
):
    """Get users without two-factor authentication"""
    # Check permission
    require_permission(current_user, "users", "read")
    
    users = await user_service.get_users_without_2fa(role)
    return users


@router.put("/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    # Users can update their own preferences, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "update")
    
    user = await user_service.update_user_preferences(user_id, preferences)
    
    return {
        "email_notifications": user.email_notifications,
        "two_factor_enabled": user.two_factor_enabled
    }


@router.get("/{user_id}/login-history")
async def get_user_login_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of records"),
    current_user: User = Depends(get_current_user)
):
    """Get user login history"""
    # Users can view their own history, others need permission
    if current_user.id != user_id:
        require_permission(current_user, "users", "read")
    
    history = await user_service.get_user_login_history(user_id, limit)
    
    return {"login_history": history}


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile(
    update_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    # Restrict allowed fields for self-update
    allowed_fields = ["full_name", "phone", "avatar_url", "email_notifications"]
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    user = await user_service.update_user_profile(
        str(current_user.id), filtered_data, current_user.username
    )
    return user


@router.put("/me/preferences")
async def update_my_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """Update current user's preferences"""
    user = await user_service.update_user_preferences(str(current_user.id), preferences)
    
    return {
        "email_notifications": user.email_notifications,
        "two_factor_enabled": user.two_factor_enabled
    }


@router.get("/me/permissions")
async def get_my_permissions(current_user: User = Depends(get_current_user)):
    """Get current user's permissions"""
    permissions = await user_service.get_user_permissions(str(current_user.id))
    
    return {
        "user_id": str(current_user.id),
        "role": current_user.role.value,
        "permissions": permissions,
        "custom_permissions": current_user.permissions
    }


@router.get("/me/login-history")
async def get_my_login_history(
    limit: int = Query(50, ge=1, le=100, description="Number of records"),
    current_user: User = Depends(get_current_user)
):
    """Get current user's login history"""
    history = await user_service.get_user_login_history(str(current_user.id), limit)
    
    return {"login_history": history}
