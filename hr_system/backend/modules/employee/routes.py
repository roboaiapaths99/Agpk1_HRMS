from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from fastapi.security import HTTPBearer

from .model import Employee
from .schema import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    EmployeeSearch, EmployeeStatusUpdate, EmployeeBulkAction
)
from .service import EmployeeService
from ..auth.dependencies import get_current_user, require_permission
from ..user.model import User

router = APIRouter()
security = HTTPBearer()
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
    employment_type: Optional[str] = Query(None, description="Filter by employment type"),
    employee_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    min_salary: Optional[float] = Query(None, ge=0, description="Minimum salary filter"),
    max_salary: Optional[float] = Query(None, ge=0, description="Maximum salary filter"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of employees with pagination and filtering"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    # Build search object
    search_obj = None
    if search or department or employment_type or employee_status or min_salary or max_salary:
        search_obj = EmployeeSearch(
            query=search,
            department=department,
            employment_type=employment_type,
            status=employee_status,
            min_salary=min_salary,
            max_salary=max_salary
        )
    
    result = await employee_service.get_employees_list(
        page, page_size, search_obj, sort_by, sort_order
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
    
    employee = await employee_service.get_employee(employee_id)
    return employee


@router.get("/code/{employee_code}", response_model=EmployeeResponse)
async def get_employee_by_code(
    employee_code: str,
    current_user: User = Depends(get_current_user)
):
    """Get employee by employee code"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employee = await employee_service.get_employee_by_code(employee_code)
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
    """Delete employee (soft delete)"""
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
        employee_id, status_update, current_user.username
    )
    return employee


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


@router.get("/manager/{manager_code}", response_model=List[EmployeeResponse])
async def get_employees_by_manager(
    manager_code: str,
    current_user: User = Depends(get_current_user)
):
    """Get employees reporting to a manager"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.get_employees_by_manager(manager_code)
    return employees


@router.get("/statistics/overview")
async def get_employee_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get employee statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await employee_service.get_employee_statistics()
    return stats


@router.get("/count/active")
async def get_active_employees_count(
    current_user: User = Depends(get_current_user)
):
    """Get count of active employees"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    count = await employee_service.get_active_employees_count()
    return {"active_employees_count": count}


@router.get("/joining-soon", response_model=List[EmployeeResponse])
async def get_employees_joining_soon(
    days: int = Query(7, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get employees joining in the next N days"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.get_employees_joining_soon(days)
    return employees


@router.get("/probation", response_model=List[EmployeeResponse])
async def get_employees_on_probation(
    current_user: User = Depends(get_current_user)
):
    """Get employees currently on probation"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.get_employees_on_probation()
    return employees


@router.post("/bulk-action")
async def bulk_employee_action(
    bulk_action: EmployeeBulkAction,
    current_user: User = Depends(get_current_user)
):
    """Perform bulk action on employees"""
    # Check permission
    require_permission(current_user, "employees", "update")
    
    # Validate action
    valid_actions = ["update_status", "update_department", "delete"]
    if bulk_action.action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Valid actions: {valid_actions}"
        )
    
    if bulk_action.action == "delete":
        # Bulk delete
        deleted_count = 0
        for emp_id in bulk_action.employee_ids:
            success = await employee_service.delete_employee(emp_id, current_user.username)
            if success:
                deleted_count += 1
        
        return {"message": f"Successfully deleted {deleted_count} employees"}
    
    elif bulk_action.action == "update_status":
        # Bulk status update
        if not bulk_action.parameters or "status" not in bulk_action.parameters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status parameter is required for status update action"
            )
        
        update_data = {"status": bulk_action.parameters["status"]}
        updated_count = await employee_service.bulk_update_employees(
            bulk_action.employee_ids, update_data, current_user.username
        )
        
        return {"message": f"Successfully updated status for {updated_count} employees"}
    
    elif bulk_action.action == "update_department":
        # Bulk department update
        if not bulk_action.parameters or "department" not in bulk_action.parameters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department parameter is required for department update action"
            )
        
        update_data = {"department": bulk_action.parameters["department"]}
        updated_count = await employee_service.bulk_update_employees(
            bulk_action.employee_ids, update_data, current_user.username
        )
        
        return {"message": f"Successfully updated department for {updated_count} employees"}


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


@router.get("/birthdays/upcoming", response_model=List[EmployeeResponse])
async def get_upcoming_birthdays(
    days: int = Query(30, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get employees with upcoming birthdays"""
    # Check permission
    require_permission(current_user, "employees", "read")
    
    employees = await employee_service.get_employees_with_upcoming_birthdays(days)
    return employees


@router.get("/me", response_model=EmployeeResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's employee profile"""
    # Users can only view their own profile
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user"
        )
    
    employee = await employee_service.get_employee(current_user.employee_id)
    return employee


@router.patch("/me", response_model=EmployeeResponse)
async def update_my_profile(
    update_data: EmployeeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user's employee profile"""
    # Users can only update their own profile with limited fields
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user"
        )
    
    # Restrict fields that employees can update themselves
    allowed_fields = {
        "phone", "current_address", "permanent_address", 
        "emergency_contact_name", "emergency_contact_phone", 
        "emergency_contact_relation"
    }
    
    # Filter update data to only allowed fields
    filtered_data = EmployeeUpdate(**{
        k: v for k, v in update_data.dict(exclude_unset=True).items() 
        if k in allowed_fields
    })
    
    employee = await employee_service.update_employee(
        current_user.employee_id, filtered_data, current_user.username
    )
    return employee
