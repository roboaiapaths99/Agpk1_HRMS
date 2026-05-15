from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from models.user_model import User, UserRole, UserStatus
from utils.helpers import create_pagination_params


class UserRepository:
    """Repository for user operations"""
    
    async def create_user(self, user_data, created_by: str = None) -> User:
        """Create a new user"""
        user = User(**user_data.dict())
        if created_by:
            user.created_by = created_by
        await user.insert()
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(PydanticObjectId(user_id))
        except:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await User.find_one(User.email == email)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await User.find_one(User.username == username)
    
    async def update_user(self, user_id: str, update_data, modified_by: str = None) -> Optional[User]:
        """Update user details"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if modified_by:
            update_dict["last_modified_by"] = modified_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await user.save()
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = UserStatus.INACTIVE
        user.is_active = False
        await user.save()
        return True
    
    async def get_users_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[User], int]:
        """Get list of users with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            query["$or"] = [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"username": {"$regex": search, "$options": "i"}}
            ]
        
        if role:
            query["role"] = role
        
        if status:
            query["status"] = status
        
        # Get total count
        total = await User.find(query).count()
        
        # Get users with pagination and sorting
        users = await User.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return users, total
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role"""
        return await User.find(User.role == role).sort(User.full_name, ASCENDING).to_list()
    
    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        return await User.find(User.is_active == True).count()
    
    async def get_users_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status"""
        return await User.find(User.status == status).sort(User.created_at, DESCENDING).to_list()
    
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users"""
        return await User.find(
            {"$or": [
                {"full_name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"username": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
    
    async def get_users_created_between(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[User]:
        """Get users created between dates"""
        return await User.find({
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).sort(User.created_at, DESCENDING).to_list()
    
    async def get_users_with_failed_logins(self, failed_attempts: int = 3) -> List[User]:
        """Get users with failed login attempts"""
        return await User.find(
            User.failed_login_attempts >= failed_attempts
        ).sort(User.failed_login_attempts, DESCENDING).to_list()
    
    async def get_users_who_never_logged_in(self) -> List[User]:
        """Get users who have never logged in"""
        return await User.find(
            User.last_login == None
        ).sort(User.created_at, DESCENDING).to_list()
    
    async def get_inactive_users(self, days: int = 30) -> List[User]:
        """Get users inactive for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await User.find({
            "last_login": {"$lt": cutoff_date}
        }).sort(User.last_login, ASCENDING).to_list()
    
    async def update_user_role(self, user_id: str, new_role: UserRole, modified_by: str = None) -> Optional[User]:
        """Update user role"""
        return await self.update_user(user_id, {"role": new_role}, modified_by)
    
    async def update_user_status(self, user_id: str, new_status: UserStatus, modified_by: str = None) -> Optional[User]:
        """Update user status"""
        update_data = {"status": new_status}
        if new_status == UserStatus.INACTIVE:
            update_data["is_active"] = False
        elif new_status == UserStatus.ACTIVE:
            update_data["is_active"] = True
        
        return await self.update_user(user_id, update_data, modified_by)
    
    async def bulk_update_users(
        self, 
        user_ids: List[str], 
        update_data: dict, 
        modified_by: str = None
    ) -> int:
        """Bulk update users"""
        if modified_by:
            update_data["last_modified_by"] = modified_by
        update_data["updated_at"] = datetime.utcnow()
        
        result = await User.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in user_ids]}}
        ).update({"$set": update_data})
        
        return result.modified_count
    
    async def get_user_statistics(self) -> dict:
        """Get user statistics"""
        total_users = await User.count()
        active_users = await self.get_active_users_count()
        
        # Role breakdown
        role_pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        role_stats = await User.aggregate(role_pipeline).to_list()
        
        # Status breakdown
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = await User.aggregate(status_pipeline).to_list()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = await User.find({
            "created_at": {"$gte": thirty_days_ago}
        }).count()
        
        # Users who never logged in
        never_logged_in = await self.get_users_who_never_logged_in()
        
        # Inactive users (last 30 days)
        inactive_users = await self.get_inactive_users(30)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_breakdown": role_stats,
            "status_breakdown": status_stats,
            "recent_registrations": recent_registrations,
            "never_logged_in_count": len(never_logged_in),
            "inactive_users_count": len(inactive_users)
        }
    
    async def get_user_login_history(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get user login history"""
        # This would integrate with an activity logging system
        # For now, return empty list
        return []
    
    async def reset_user_password(self, user_id: str, new_password: str, modified_by: str = None) -> Optional[User]:
        """Reset user password"""
        from core.security import SecurityManager
        
        security_manager = SecurityManager()
        hashed_password = security_manager.get_password_hash(new_password)
        
        return await self.update_user(
            user_id, 
            {
                "hashed_password": hashed_password,
                "password_changed_at": datetime.utcnow(),
                "failed_login_attempts": 0,
                "locked_until": None
            }, 
            modified_by
        )
    
    async def unlock_user_account(self, user_id: str, modified_by: str = None) -> Optional[User]:
        """Unlock user account"""
        return await self.update_user(
            user_id,
            {
                "failed_login_attempts": 0,
                "locked_until": None,
                "status": UserStatus.ACTIVE,
                "is_active": True
            },
            modified_by
        )
    
    async def get_users_expiring_passwords(self, days: int = 7) -> List[User]:
        """Get users with passwords expiring soon"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        return await User.find({
            "password_changed_at": {"$lte": cutoff_date - timedelta(days=90)},
            "is_active": True
        }).sort(User.password_changed_at, ASCENDING).to_list()
    
    async def get_users_with_2fa_enabled(self) -> List[User]:
        """Get users with two-factor authentication enabled"""
        return await User.find(User.two_factor_enabled == True).sort(User.full_name, ASCENDING).to_list()
    
    async def get_users_without_2fa(self, role: Optional[UserRole] = None) -> List[User]:
        """Get users without two-factor authentication"""
        query = {"two_factor_enabled": False, "is_active": True}
        if role:
            query["role"] = role
        
        return await User.find(query).sort(User.full_name, ASCENDING).to_list()
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return []
        
        from core.security import RolePermissions
        role_permissions = RolePermissions.ROLES.get(user.role.value, {})
        
        permissions = set()
        for resource, actions in role_permissions.items():
            for action in actions:
                permissions.add(f"{resource}:{action}")
        
        # Add custom permissions
        permissions.update(user.permissions)
        
        return list(permissions)
    
    async def check_user_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has specific permission"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        from core.security import RolePermissions
        return RolePermissions.has_permission(user.role.value, resource, action) or \
               f"{resource}:{action}" in user.permissions
