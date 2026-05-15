from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime, date

from services.onboarding_service import OnboardingService
from schemas.onboarding_schema import (
    OnboardingCreate, OnboardingUpdate, OnboardingResponse, OnboardingListResponse,
    OnboardingSearch, OnboardingTaskCreate, OnboardingTaskUpdate
)
from routes.auth import get_current_user, require_permission
from models.user_model import User

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])
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
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned person"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of onboardings with pagination and filtering"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    result = await onboarding_service.get_onboardings_list(
        page, page_size, search, department, status, assigned_to, sort_by, sort_order
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
    
    onboarding = await onboarding_service.get_onboarding_by_id(onboarding_id)
    return onboarding


@router.get("/employee/{employee_id}", response_model=OnboardingResponse)
async def get_onboarding_by_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get onboarding by employee ID"""
    # Users can view their own onboarding
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
    
    onboarding = await onboarding_service.update_onboarding(onboarding_id, update_data, current_user.username)
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
    
    onboarding = await onboarding_service.add_task_to_onboarding(onboarding_id, task_data, current_user.username)
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
    
    onboarding = await onboarding_service.complete_task(onboarding_id, task_id, current_user.username, notes)
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
    
    onboarding = await onboarding_service.update_task_status(onboarding_id, task_id, task_update, current_user.username)
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


@router.get("/overdue", response_model=List[OnboardingResponse])
async def get_overdue_onboardings(
    current_user: User = Depends(get_current_user)
):
    """Get all overdue onboardings"""
    # Check permission
    require_permission(current_user, "onboarding", "read")
    
    onboardings = await onboarding_service.get_overdue_onboardings()
    return onboardings


@router.get("/statistics")
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
        updated_onboarding = await onboarding_service.update_onboarding(
            str(onboarding.id), update_data, current_user.username
        )
        return updated_onboarding
    
    return onboarding


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
    
    onboarding = await onboarding_service.create_onboarding_from_template(
        template_name, employee_id, current_user.username
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
    feedback_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit onboarding feedback"""
    # Users can submit feedback for their own onboarding
    onboarding = await onboarding_service.get_onboarding_by_id(onboarding_id)
    
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
