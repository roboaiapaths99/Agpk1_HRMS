from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime, date

from services.employee_service import EmployeeService
from schemas.employee_schema import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    EmployeeSearch, EmployeeStatusUpdate, EmployeeBulkAction
)
from routes.auth import get_current_user, require_permission
from models.user_model import User

router = APIRouter(prefix="/employees", tags=["Employees"])
employee_service = EmployeeService()


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new employee"""
    # Check permission
    require_permission(current_user, "employees", "create")
    
    employee = await employee_service.create_employee(employee_data, current_user.username)
    return employee


@router.get("/", response_model=EmployeeListResponse)
async def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of employees with pagination and filtering"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    result = await employee_service.get_employees_list(
        page, page_size, search, department, status, sort_by, sort_order
    )
    
    return EmployeeListResponse(**result)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get employee by ID"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employee = await employee_service.get_employee_by_id(employee_id)
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    update_data: EmployeeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update employee details"""
    # Check permission
    require_permission(current_user, "employees", "update")
    
    employee = await employee_service.update_employee(employee_id, update_data, current_user.username)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete employee record"""
    # Check permission
    require_permission(current_user, "employees", "delete")
    
    success = await employee_service.delete_employee(employee_id, current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )


@router.patch("/{employee_id}/status", response_model=EmployeeResponse)
async def update_employee_status(
    employee_id: str,
    status_update: EmployeeStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update employee status"""
    # Check permission
    require_permission(current_user, "employees", "update")
    
    employee = await employee_service.update_employee_status(
        employee_id, status_update.status, current_user.username
    )
    return employee


@router.post("/bulk-action")
async def bulk_action(
    bulk_action: EmployeeBulkAction,
    current_user: User = Depends(get_current_user)
):
    """Perform bulk action on employees"""
    # Check permission
    require_permission(current_user, "employees", "update")
    
    result = await employee_service.bulk_action(bulk_action, current_user.username)
    return result


@router.get("/search", response_model=List[EmployeeResponse])
async def search_employees(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Result limit"),
    current_user: User = Depends(get_current_user)
):
    """Search employees"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.search_employees(q, limit)
    return employees


@router.get("/statistics")
async def get_employee_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get employee statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await employee_service.get_employee_statistics()
    return stats


@router.get("/department/{department}", response_model=List[EmployeeResponse])
async def get_employees_by_department(
    department: str,
    current_user: User = Depends(get_current_user)
):
    """Get employees by department"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.get_employees_by_department(department)
    return employees


@router.get("/birthdays/upcoming")
async def get_upcoming_birthdays(
    days: int = Query(30, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming birthdays"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    birthdays = await employee_service.get_upcoming_birthdays(days)
    return birthdays


@router.get("/me", response_model=EmployeeResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's employee profile"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user"
        )
    
    employee = await employee_service.get_employee_by_id(current_user.employee_id)
    return employee


@router.put("/me/profile", response_model=EmployeeResponse)
async def update_my_profile(
    update_data: EmployeeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user's employee profile"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user"
        )
    
    # Restrict fields for self-update
    allowed_fields = ["phone", "address", "emergency_contact", "bank_details"]
    filtered_data = {k: v for k, v in update_data.dict().items() if k in allowed_fields}
    
    employee = await employee_service.update_employee(
        current_user.employee_id, filtered_data, current_user.username
    )
    return employee
