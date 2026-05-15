from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .model import User, UserRole, UserStatus
from .service import UserService
from .repository import UserRepository
from core.security import SecurityManager

security = HTTPBearer()
user_service = UserService()
user_repository = UserRepository()
security_manager = SecurityManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security_manager.verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = await user_repository.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Check if account is locked
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is locked"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: UserRole):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_any_role(*allowed_roles: UserRole):
    """Decorator to require any of the specified roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_min_role(min_role: UserRole):
    """Decorator to require minimum role level"""
    role_hierarchy = {
        UserRole.EMPLOYEE: 0,
        UserRole.HR_EXECUTIVE: 1,
        UserRole.HR_MANAGER: 2,
        UserRole.ADMIN: 3
    }
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(min_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


async def require_permission(user: User, resource: str, action: str) -> bool:
    """Check if user has specific permission"""
    from core.security import RolePermissions
    
    # Check role-based permissions
    if RolePermissions.has_permission(user.role.value, resource, action):
        return True
    
    # Check custom permissions
    permission_key = f"{resource}:{action}"
    if permission_key in user.permissions:
        return True
    
    return False


def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not require_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {action} on {resource}"
            )
        return current_user
    
    return permission_checker


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_hr_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current HR user (HR Manager or HR Executive)"""
    if current_user.role not in [UserRole.HR_MANAGER, UserRole.HR_EXECUTIVE, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required"
        )
    return current_user


async def get_hr_manager_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current HR Manager user"""
    if current_user.role not in [UserRole.HR_MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR Manager access required"
        )
    return current_user


async def get_employee_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current employee user"""
    if current_user.role != UserRole.EMPLOYEE and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )
    return current_user


async def validate_user_access(user: User, target_user_id: str) -> bool:
    """Validate if user can access target user's information"""
    # Users can always access their own information
    if str(user.id) == target_user_id:
        return True
    
    # Admin can access any user's information
    if user.role == UserRole.ADMIN:
        return True
    
    # HR Manager can access any employee's information
    if user.role == UserRole.HR_MANAGER:
        return True
    
    # HR Executive can access limited information
    if user.role == UserRole.HR_EXECUTIVE:
        return True
    
    # Employees can only access their own information
    return False


async def check_user_ownership(user: User, resource_user_id: str) -> bool:
    """Check if user owns the resource"""
    return str(user.id) == resource_user_id


def require_ownership(resource_user_id_param: str = "user_id"):
    """Decorator to require resource ownership"""
    def ownership_checker(current_user: User = Depends(get_current_user), **kwargs) -> User:
        resource_user_id = kwargs.get(resource_user_id_param)
        if resource_user_id and not check_user_ownership(current_user, resource_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't own this resource"
            )
        return current_user
    
    return ownership_checker


async def get_user_with_employee_link(current_user: User = Depends(get_current_user)) -> User:
    """Get current user with employee link validation"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to an employee profile"
        )
    return current_user


async def validate_employee_access(user: User, employee_id: str) -> bool:
    """Validate if user can access employee information"""
    # Users can access their own employee information
    if user.employee_id == employee_id:
        return True
    
    # Admin can access any employee information
    if user.role == UserRole.ADMIN:
        return True
    
    # HR Manager can access any employee information
    if user.role == UserRole.HR_MANAGER:
        return True
    
    # HR Executive has limited access
    if user.role == UserRole.HR_EXECUTIVE:
        return True  # For now, allow access - can be restricted further
    
    return False


def require_employee_access(employee_id_param: str = "employee_id"):
    """Decorator to require employee access"""
    def employee_access_checker(current_user: User = Depends(get_current_user), **kwargs) -> User:
        employee_id = kwargs.get(employee_id_param)
        if employee_id and not validate_employee_access(current_user, employee_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to access this employee information"
            )
        return current_user
    
    return employee_access_checker


# Dependency for getting user service
def get_user_service() -> UserService:
    """Get user service instance"""
    return user_service


# Dependency for getting user repository
def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    return user_repository


# Dependency for getting security manager
def get_security_manager() -> SecurityManager:
    """Get security manager instance"""
    return security_manager


# Combined dependencies for common use cases
async def get_current_hr_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current HR user (Manager or Executive)"""
    if current_user.role not in [UserRole.HR_MANAGER, UserRole.HR_EXECUTIVE, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR access required"
        )
    return current_user


async def get_current_manager_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current manager user (HR Manager or Admin)"""
    if current_user.role not in [UserRole.HR_MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


# Permission-based dependencies
def require_employees_permission(action: str = "read"):
    """Require employees permission"""
    return require_permission("employees", action)


def require_onboarding_permission(action: str = "read"):
    """Require onboarding permission"""
    return require_permission("onboarding", action)


def require_payroll_permission(action: str = "read"):
    """Require payroll permission"""
    return require_permission("payroll", action)


def require_exit_management_permission(action: str = "read"):
    """Require exit management permission"""
    return require_permission("exit_management", action)


def require_analytics_permission(action: str = "read"):
    """Require analytics permission"""
    return require_permission("analytics", action)


def require_users_permission(action: str = "read"):
    """Require users permission"""
    return require_permission("users", action)
