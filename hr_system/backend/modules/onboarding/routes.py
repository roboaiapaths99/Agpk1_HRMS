from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from fastapi.security import HTTPBearer

from .model import Onboarding, OnboardingTask
from .schema import (
    OnboardingCreate, OnboardingUpdate, OnboardingResponse, OnboardingListResponse,
    OnboardingSearch, OnboardingTaskCreate, OnboardingTaskUpdate, OnboardingBlocker,
    OnboardingFeedback, OnboardingStatistics
)
from .service import OnboardingService
from ..auth.dependencies import get_current_user, require_permission
from ..user.model import User

router = APIRouter()
security = HTTPBearer()
onboarding_service = OnboardingService()


@router.post("/", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding(
    onboarding_data: OnboardingCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new onboarding process"""
    # Check permission
    require_permission(current_user, "onboarding", "create")
    
    onboarding = await onboarding_service.create_onboarding(onboarding_data, current_user.username)
    return onboarding


@router.get("/", response_model=OnboardingListResponse)
async def get_onboardings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    onboarding_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned person"),
    start_date_from: Optional[str] = Query(None, description="Start date from (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Start date to (YYYY-MM-DD)"),
    completion_date_from: Optional[str] = Query(None, description="Completion date from (YYYY-MM-DD)"),
    completion_date_to: Optional[str] = Query(None, description="Completion date to (YYYY-MM-DD)"),
    overdue_only: bool = Query(False, description="Show only overdue onboardings"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of onboardings with pagination and filtering"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    # Parse dates
    from datetime import datetime
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        return None
    
    # Build search object
    search_obj = None
    if any([search, department, onboarding_status, assigned_to, start_date_from, start_date_to, 
            completion_date_from, completion_date_to, overdue_only]):
        search_obj = OnboardingSearch(
            query=search,
            department=department,
            status=onboarding_status,
            assigned_to=assigned_to,
            start_date_from=parse_date(start_date_from),
            start_date_to=parse_date(start_date_to),
            completion_date_from=parse_date(completion_date_from),
            completion_date_to=parse_date(completion_date_to),
            overdue_only=overdue_only
        )
    
    result = await onboarding_service.get_onboardings_list(
        page, page_size, search_obj, sort_by, sort_order
    )
    
    return OnboardingListResponse(**result)


@router.get("/{onboarding_id}", response_model=OnboardingResponse)
async def get_onboarding(
    onboarding_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get onboarding by ID"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboarding = await onboarding_service.get_onboarding(onboarding_id)
    return onboarding


@router.get("/employee/{employee_id}", response_model=OnboardingResponse)
async def get_onboarding_by_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get onboarding by employee ID"""
    # Check permission (users can view their own onboarding)
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "onboarding", "read")
    
    onboarding = await onboarding_service.get_onboarding_by_employee(employee_id)
    return onboarding


@router.put("/{onboarding_id}", response_model=OnboardingResponse)
async def update_onboarding(
    onboarding_id: str,
    update_data: OnboardingUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update onboarding details"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.update_onboarding(
        onboarding_id, update_data, current_user.username
    )
    return onboarding


@router.delete("/{onboarding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_onboarding(
    onboarding_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete onboarding process"""
    # Check permission
    require_permission(current_user, "onboarding", "delete")
    
    success = await onboarding_service.delete_onboarding(onboarding_id, current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding not found"
        )


@router.post("/{onboarding_id}/tasks", response_model=OnboardingResponse)
async def add_task_to_onboarding(
    onboarding_id: str,
    task_data: OnboardingTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new task to onboarding"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.add_task_to_onboarding(
        onboarding_id, task_data, current_user.username
    )
    return onboarding


@router.patch("/{onboarding_id}/tasks/{task_id}/complete", response_model=OnboardingResponse)
async def complete_task(
    onboarding_id: str,
    task_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.complete_task(
        onboarding_id, task_id, current_user.username, notes
    )
    return onboarding


@router.patch("/{onboarding_id}/tasks/{task_id}/status", response_model=OnboardingResponse)
async def update_task_status(
    onboarding_id: str,
    task_id: str,
    task_update: OnboardingTaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update task status"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.update_task_status(
        onboarding_id, task_id, task_update, current_user.username
    )
    return onboarding


@router.get("/{onboarding_id}/tasks/overdue")
async def get_overdue_tasks(
    onboarding_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get overdue tasks for an onboarding"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    tasks = await onboarding_service.get_overdue_tasks(onboarding_id)
    return {"overdue_tasks": tasks}


@router.get("/{onboarding_id}/tasks/critical")
async def get_critical_tasks(
    onboarding_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get critical tasks for an onboarding"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    tasks = await onboarding_service.get_critical_tasks(onboarding_id)
    return {"critical_tasks": tasks}


@router.get("/overdue/list", response_model=List[OnboardingResponse])
async def get_overdue_onboardings(
    current_user: User = Depends(get_current_user)
):
    """Get all overdue onboardings"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_overdue_onboardings()
    return onboardings


@router.get("/statistics/overview")
async def get_onboarding_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get onboarding statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await onboarding_service.get_onboarding_statistics()
    return stats


@router.get("/department/{department}", response_model=List[OnboardingResponse])
async def get_onboardings_by_department(
    department: str,
    current_user: User = Depends(get_current_user)
):
    """Get onboardings by department"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_onboardings_by_department(department)
    return onboardings


@router.get("/assignee/{assignee}", response_model=List[OnboardingResponse])
async def get_onboardings_by_assignee(
    assignee: str,
    current_user: User = Depends(get_current_user)
):
    """Get onboardings assigned to a person"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_onboardings_by_assignee(assignee)
    return onboardings


@router.post("/{onboarding_id}/blockers", response_model=OnboardingResponse)
async def add_blocker(
    onboarding_id: str,
    blocker_data: OnboardingBlocker,
    current_user: User = Depends(get_current_user)
):
    """Add a blocker to onboarding"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.add_blocker(
        onboarding_id, blocker_data, current_user.username
    )
    return onboarding


@router.patch("/{onboarding_id}/blockers/{blocker_index}/resolve", response_model=OnboardingResponse)
async def resolve_blocker(
    onboarding_id: str,
    blocker_index: int,
    resolution_notes: str,
    current_user: User = Depends(get_current_user)
):
    """Resolve a blocker"""
    # Check permission
    require_permission(current_user, "onboarding", "update")
    
    onboarding = await onboarding_service.resolve_blocker(
        onboarding_id, blocker_index, resolution_notes, current_user.username
    )
    return onboarding


@router.get("/tasks/assignee/{assignee}")
async def get_tasks_by_assignee(
    assignee: str,
    current_user: User = Depends(get_current_user)
):
    """Get all tasks assigned to a person"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    tasks = await onboarding_service.get_tasks_by_assignee(assignee)
    return {"tasks": tasks}


@router.get("/templates")
async def get_onboarding_templates(
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: User = Depends(get_current_user)
):
    """Get onboarding templates"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    templates = await onboarding_service.get_onboarding_templates(department)
    return {"templates": templates}


@router.post("/from-template", response_model=OnboardingResponse)
async def create_onboarding_from_template(
    template_name: str = Query(..., description="Template name"),
    employee_id: str = Query(..., description="Employee ID"),
    current_user: User = Depends(get_current_user)
):
    """Create onboarding from template"""
    # Check permission
    require_permission(current_user, "onboarding", "create")
    
    # Get employee data (would fetch from employee service)
    # This is a placeholder - in production, you'd fetch real employee data
    employee_data = {
        "employee_id": employee_id,
        "employee_code": "EMP001",  # Placeholder
        "employee_name": "John Doe",  # Placeholder
        "department": "engineering"  # Placeholder
    }
    
    onboarding = await onboarding_service.create_onboarding_from_template(
        template_name, employee_data, current_user.username
    )
    
    if not onboarding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return onboarding


@router.post("/{onboarding_id}/feedback", response_model=OnboardingResponse)
async def submit_feedback(
    onboarding_id: str,
    feedback_data: OnboardingFeedback,
    current_user: User = Depends(get_current_user)
):
    """Submit onboarding feedback"""
    # Users can submit feedback for their own onboarding
    onboarding = await onboarding_service.get_onboarding(onboarding_id)
    
    if (current_user.role.value == "employee" and 
        onboarding.employee_id != current_user.employee_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit feedback for your own onboarding"
        )
    
    updated_onboarding = await onboarding_service.submit_feedback(
        onboarding_id, feedback_data, current_user.username
    )
    return updated_onboarding


@router.get("/starting-soon", response_model=List[OnboardingResponse])
async def get_onboardings_starting_soon(
    days: int = Query(7, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get onboardings starting in the next N days"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_onboardings_starting_soon(days)
    return onboardings


@router.get("/completing-soon", response_model=List[OnboardingResponse])
async def get_onboardings_completing_soon(
    days: int = Query(7, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get onboardings completing in the next N days"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_onboardings_completing_soon(days)
    return onboardings


@router.get("/me", response_model=OnboardingResponse)
async def get_my_onboarding(
    current_user: User = Depends(get_current_user)
):
    """Get current user's onboarding"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding not found for this user"
        )
    
    onboarding = await onboarding_service.get_onboarding_by_employee(current_user.employee_id)
    return onboarding


@router.patch("/me/checklist", response_model=OnboardingResponse)
async def update_my_checklist(
    checklist_updates: dict,
    current_user: User = Depends(get_current_user)
):
    """Update current user's onboarding checklist"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding not found for this user"
        )
    
    onboarding = await onboarding_service.get_onboarding_by_employee(current_user.employee_id)
    
    # Update checklist items that employees can update themselves
    updatable_fields = [
        "policy_acknowledgment", "benefits_enrollment"
    ]
    
    update_data = {}
    for field, value in checklist_updates.items():
        if field in updatable_fields and isinstance(value, bool):
            update_data[field] = value
    
    if update_data:
        from .schema import OnboardingUpdate
        update_obj = OnboardingUpdate(**update_data)
        updated_onboarding = await onboarding_service.update_onboarding(
            str(onboarding.id), update_obj, current_user.username
        )
        return updated_onboarding
    
    return onboarding
