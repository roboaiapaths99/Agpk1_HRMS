from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

from models.user_model import User, UserRole, UserStatus
from schemas.user_schema import UserResponse, UserListResponse
from repositories.user_repo import UserRepository
from utils.logger import audit_logger


class UserService:
    """Service layer for user operations"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    async def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID"""
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.repository.get_user_by_email(email)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.repository.get_user_by_username(username)
    
    async def update_user_profile(self, user_id: str, update_data: dict, modified_by: str = None) -> User:
        """Update user profile"""
        user = await self.get_user_by_id(user_id)
        
        # Validate update data
        await self._validate_user_update(update_data, user)
        
        try:
            updated_user = await self.repository.update_user(user_id, update_data, modified_by)
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "profile_updated", user_id,
                f"Updated profile for user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
    
    async def deactivate_user(self, user_id: str, deactivated_by: str) -> User:
        """Deactivate user account"""
        user = await self.get_user_by_id(user_id)
        
        try:
            updated_user = await self.repository.update_user_status(
                user_id, UserStatus.INACTIVE, deactivated_by
            )
            
            # Log the action
            audit_logger.log_user_action(
                deactivated_by, "user_deactivated", user_id,
                f"Deactivated user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user"
            )
    
    async def activate_user(self, user_id: str, activated_by: str) -> User:
        """Activate user account"""
        user = await self.get_user_by_id(user_id)
        
        try:
            updated_user = await self.repository.update_user_status(
                user_id, UserStatus.ACTIVE, activated_by
            )
            
            # Log the action
            audit_logger.log_user_action(
                activated_by, "user_activated", user_id,
                f"Activated user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate user"
            )
    
    async def update_user_role(self, user_id: str, new_role: UserRole, modified_by: str) -> User:
        """Update user role"""
        user = await self.get_user_by_id(user_id)
        
        try:
            updated_user = await self.repository.update_user_role(user_id, new_role, modified_by)
            
            # Log the action
            audit_logger.log_user_action(
                modified_by, "role_updated", user_id,
                f"Updated role to {new_role.value} for user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user role"
            )
    
    async def get_users_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of users"""
        try:
            users, total = await self.repository.get_users_list(
                page, page_size, search, role, status, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users"
            )
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role"""
        try:
            return await self.repository.get_users_by_role(role)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users by role"
            )
    
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users"""
        try:
            return await self.repository.search_users(query, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search users"
            )
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            return await self.repository.get_user_statistics()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user statistics"
            )
    
    async def reset_user_password(self, user_id: str, new_password: str, reset_by: str) -> User:
        """Reset user password"""
        user = await self.get_user_by_id(user_id)
        
        try:
            updated_user = await self.repository.reset_user_password(user_id, new_password, reset_by)
            
            # Log the action
            audit_logger.log_user_action(
                reset_by, "password_reset", user_id,
                f"Reset password for user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
    
    async def unlock_user_account(self, user_id: str, unlocked_by: str) -> User:
        """Unlock user account"""
        user = await self.get_user_by_id(user_id)
        
        try:
            updated_user = await self.repository.unlock_user_account(user_id, unlocked_by)
            
            # Log the action
            audit_logger.log_user_action(
                unlocked_by, "account_unlocked", user_id,
                f"Unlocked account for user {updated_user.email}"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlock account"
            )
    
    async def get_users_with_failed_logins(self, failed_attempts: int = 3) -> List[User]:
        """Get users with failed login attempts"""
        try:
            return await self.repository.get_users_with_failed_logins(failed_attempts)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users with failed logins"
            )
    
    async def get_inactive_users(self, days: int = 30) -> List[User]:
        """Get inactive users"""
        try:
            return await self.repository.get_inactive_users(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch inactive users"
            )
    
    async def bulk_update_users(
        self, 
        user_ids: List[str], 
        update_data: dict, 
        modified_by: str = None
    ) -> Dict[str, Any]:
        """Bulk update users"""
        try:
            # Validate that all users exist
            for user_id in user_ids:
                await self.get_user_by_id(user_id)
            
            updated_count = await self.repository.bulk_update_users(user_ids, update_data, modified_by)
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "bulk_updated", "",
                f"Bulk updated {updated_count} users"
            )
            
            return {
                "total_users": len(user_ids),
                "updated_count": updated_count,
                "failed_count": len(user_ids) - updated_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk update users"
            )
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        try:
            return await self.repository.get_user_permissions(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user permissions"
            )
    
    async def check_user_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has specific permission"""
        try:
            return await self.repository.check_user_permission(user_id, resource, action)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to check user permission"
            )
    
    async def get_users_expiring_passwords(self, days: int = 7) -> List[User]:
        """Get users with passwords expiring soon"""
        try:
            return await self.repository.get_users_expiring_passwords(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users with expiring passwords"
            )
    
    async def get_users_with_2fa_enabled(self) -> List[User]:
        """Get users with two-factor authentication enabled"""
        try:
            return await self.repository.get_users_with_2fa_enabled()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users with 2FA enabled"
            )
    
    async def get_users_without_2fa(self, role: Optional[UserRole] = None) -> List[User]:
        """Get users without two-factor authentication"""
        try:
            return await self.repository.get_users_without_2fa(role)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users without 2FA"
            )
    
    async def update_user_preferences(self, user_id: str, preferences: dict) -> User:
        """Update user preferences"""
        user = await self.get_user_by_id(user_id)
        
        try:
            # Update preferences
            update_data = {}
            
            if "email_notifications" in preferences:
                update_data["email_notifications"] = preferences["email_notifications"]
            
            if "two_factor_enabled" in preferences:
                update_data["two_factor_enabled"] = preferences["two_factor_enabled"]
            
            updated_user = await self.repository.update_user(user_id, update_data)
            
            # Log the action
            audit_logger.log_user_action(
                str(user_id), "preferences_updated", user_id,
                "Updated user preferences"
            )
            
            return updated_user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
    
    async def get_user_login_history(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get user login history"""
        try:
            return await self.repository.get_user_login_history(user_id, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user login history"
            )
    
    async def delete_user(self, user_id: str, deleted_by: str) -> bool:
        """Delete user (soft delete)"""
        user = await self.get_user_by_id(user_id)
        
        try:
            success = await self.repository.delete_user(user_id)
            
            if success:
                # Log the action
                audit_logger.log_user_action(
                    deleted_by, "user_deleted", user_id,
                    f"Deleted user {user.email}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    
    async def _validate_user_update(self, update_data: dict, user: User):
        """Validate user update data"""
        # Email validation
        if "email" in update_data:
            new_email = update_data["email"]
            if new_email != user.email:
                existing_user = await self.repository.get_user_by_email(new_email)
                if existing_user:
                    raise ValueError("Email already exists")
        
        # Username validation
        if "username" in update_data:
            new_username = update_data["username"]
            if new_username != user.username:
                existing_user = await self.repository.get_user_by_username(new_username)
                if existing_user:
                    raise ValueError("Username already exists")
        
        # Role validation
        if "role" in update_data:
            try:
                UserRole(update_data["role"])
            except ValueError:
                raise ValueError("Invalid role")
        
        # Status validation
        if "status" in update_data:
            try:
                UserStatus(update_data["status"])
            except ValueError:
                raise ValueError("Invalid status")
