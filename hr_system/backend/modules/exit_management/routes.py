from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from fastapi.security import HTTPBearer

from .model import ExitManagement, ExitTask
from .schema import (
    ExitManagementCreate, ExitManagementUpdate, ExitManagementResponse, ExitManagementListResponse,
    ExitSearch, ExitTaskCreate, ExitTaskUpdate, ExitBlocker, ExitFeedback, ExitInterview,
    ExitAsset, ExitSettlement, ExitStatistics
)
from .service import ExitManagementService
from ..auth.dependencies import get_current_user, require_permission
from ..user.model import User

router = APIRouter()
security = HTTPBearer()
exit_service = ExitManagementService()


@router.post("/", response_model=ExitManagementResponse, status_code=status.HTTP_201_CREATED)
async def create_exit_management(
    exit_data: ExitManagementCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new exit management process"""
    # Check permission
    require_permission(current_user, "exit_management", "create")
    
    exit_management = await exit_service.create_exit_management(exit_data, current_user.username)
    return exit_management


@router.get("/", response_model=ExitManagementListResponse)
async def get_exits(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    exit_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    exit_reason: Optional[str] = Query(None, description="Filter by exit reason"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned person"),
    resignation_date_from: Optional[str] = Query(None, description="Resignation date from (YYYY-MM-DD)"),
    resignation_date_to: Optional[str] = Query(None, description="Resignation date to (YYYY-MM-DD)"),
    last_working_day_from: Optional[str] = Query(None, description="Last working day from (YYYY-MM-DD)"),
    last_working_day_to: Optional[str] = Query(None, description="Last working day to (YYYY-MM-DD)"),
    overdue_only: bool = Query(False, description="Show only overdue exits"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of exit processes with pagination and filtering"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
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
    if any([search, department, exit_status, exit_reason, assigned_to, resignation_date_from, 
            resignation_date_to, last_working_day_from, last_working_day_to, overdue_only]):
        search_obj = ExitSearch(
            query=search,
            department=department,
            status=exit_status,
            exit_reason=exit_reason,
            assigned_to=assigned_to,
            resignation_date_from=parse_date(resignation_date_from),
            resignation_date_to=parse_date(resignation_date_to),
            last_working_day_from=parse_date(last_working_day_from),
            last_working_day_to=parse_date(last_working_day_to),
            overdue_only=overdue_only
        )
    
    result = await exit_service.get_exits_list(
        page, page_size, search_obj, sort_by, sort_order
    )
    
    return ExitManagementListResponse(**result)


@router.get("/{exit_id}", response_model=ExitManagementResponse)
async def get_exit_management(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get exit management by ID"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    exit_management = await exit_service.get_exit_management(exit_id)
    return exit_management


@router.get("/employee/{employee_id}", response_model=ExitManagementResponse)
async def get_exit_by_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get exit management by employee ID"""
    # Check permission (users can view their own exit process)
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "exit_management", "read")
    
    exit_management = await exit_service.get_exit_by_employee(employee_id)
    return exit_management


@router.put("/{exit_id}", response_model=ExitManagementResponse)
async def update_exit_management(
    exit_id: str,
    update_data: ExitManagementUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update exit management details"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.update_exit_management(
        exit_id, update_data, current_user.username
    )
    return exit_management


@router.delete("/{exit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exit_management(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete exit management process"""
    # Check permission
    require_permission(current_user, "exit_management", "delete")
    
    success = await exit_service.delete_exit_management(exit_id, current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit process not found"
        )


@router.post("/{exit_id}/tasks", response_model=ExitManagementResponse)
async def add_task_to_exit(
    exit_id: str,
    task_data: ExitTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new task to exit process"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.add_task_to_exit(
        exit_id, task_data, current_user.username
    )
    return exit_management


@router.patch("/{exit_id}/tasks/{task_id}/complete", response_model=ExitManagementResponse)
async def complete_task(
    exit_id: str,
    task_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.complete_task(
        exit_id, task_id, current_user.username, notes
    )
    return exit_management


@router.patch("/{exit_id}/tasks/{task_id}/status", response_model=ExitManagementResponse)
async def update_task_status(
    exit_id: str,
    task_id: str,
    task_update: ExitTaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update task status"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.update_task_status(
        exit_id, task_id, task_update, current_user.username
    )
    return exit_management


@router.get("/{exit_id}/tasks/overdue")
async def get_overdue_tasks(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get overdue tasks for an exit process"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    tasks = await exit_service.get_overdue_tasks(exit_id)
    return {"overdue_tasks": tasks}


@router.get("/statistics/overview")
async def get_exit_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get exit management statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await exit_service.get_exit_statistics()
    return stats


@router.get("/department/{department}", response_model=List[ExitManagementResponse])
async def get_exits_by_department(
    department: str,
    current_user: User = Depends(get_current_user)
):
    """Get exit processes by department"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    exits = await exit_service.get_exits_by_department(department)
    return exits


@router.get("/assignee/{assignee}", response_model=List[ExitManagementResponse])
async def get_exits_by_assignee(
    assignee: str,
    current_user: User = Depends(get_current_user)
):
    """Get exit processes assigned to a person"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    exits = await exit_service.get_exits_by_assignee(assignee)
    return exits


@router.post("/{exit_id}/blockers", response_model=ExitManagementResponse)
async def add_blocker(
    exit_id: str,
    blocker_data: ExitBlocker,
    current_user: User = Depends(get_current_user)
):
    """Add a blocker to exit process"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.add_blocker(
        exit_id, blocker_data, current_user.username
    )
    return exit_management


@router.patch("/{exit_id}/blockers/{blocker_index}/resolve", response_model=ExitManagementResponse)
async def resolve_blocker(
    exit_id: str,
    blocker_index: int,
    resolution_notes: str,
    current_user: User = Depends(get_current_user)
):
    """Resolve a blocker"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.resolve_blocker(
        exit_id, blocker_index, resolution_notes, current_user.username
    )
    return exit_management


@router.patch("/{exit_id}/complete", response_model=ExitManagementResponse)
async def complete_exit(
    exit_id: str,
    completion_date: str = Query(..., description="Completion date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """Complete the exit process"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    from datetime import datetime
    try:
        parsed_date = datetime.strptime(completion_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    exit_management = await exit_service.complete_exit(
        exit_id, parsed_date, current_user.username
    )
    return exit_management


@router.post("/{exit_id}/interview", response_model=ExitManagementResponse)
async def conduct_exit_interview(
    exit_id: str,
    interview_data: ExitInterview,
    current_user: User = Depends(get_current_user)
):
    """Conduct exit interview"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.conduct_exit_interview(
        exit_id, interview_data, current_user.username
    )
    return exit_management


@router.post("/{exit_id}/assets", response_model=ExitManagementResponse)
async def add_asset_return(
    exit_id: str,
    asset_data: ExitAsset,
    current_user: User = Depends(get_current_user)
):
    """Add asset return record"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    exit_management = await exit_service.add_asset_return(
        exit_id, asset_data, current_user.username
    )
    return exit_management


@router.patch("/{exit_id}/settlement/calculate", response_model=ExitManagementResponse)
async def calculate_final_settlement(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Calculate final settlement"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    exit_management = await exit_service.calculate_final_settlement(
        exit_id, current_user.username
    )
    return exit_management


@router.post("/{exit_id}/settlement/process", response_model=ExitManagementResponse)
async def process_final_settlement(
    exit_id: str,
    settlement_data: ExitSettlement,
    current_user: User = Depends(get_current_user)
):
    """Process final settlement"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    exit_management = await exit_service.process_final_settlement(
        exit_id, settlement_data, current_user.username
    )
    return exit_management


@router.post("/{exit_id}/feedback", response_model=ExitManagementResponse)
async def submit_exit_feedback(
    exit_id: str,
    feedback_data: ExitFeedback,
    current_user: User = Depends(get_current_user)
):
    """Submit exit feedback"""
    # Users can submit feedback for their own exit process
    exit_management = await exit_service.get_exit_management(exit_id)
    
    if (current_user.role.value == "employee" and 
        exit_management.employee_id != current_user.employee_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit feedback for your own exit process"
        )
    
    updated_exit_management = await exit_service.submit_exit_feedback(
        exit_id, feedback_data, current_user.username
    )
    return updated_exit_management


@router.get("/{exit_id}/clearance")
async def get_clearance_status(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get clearance status for all departments"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    clearance_status = await exit_service.get_clearance_status(exit_id)
    return clearance_status


@router.get("/{exit_id}/summary")
async def get_exit_summary(
    exit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get exit process summary"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    summary = await exit_service.get_exit_summary(exit_id)
    return summary


@router.get("/tasks/assignee/{assignee}")
async def get_tasks_by_assignee(
    assignee: str,
    current_user: User = Depends(get_current_user)
):
    """Get all tasks assigned to a person"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    tasks = await exit_service.get_tasks_by_assignee(assignee)
    return {"tasks": tasks}


@router.get("/completing-soon", response_model=List[ExitManagementResponse])
async def get_exits_completing_soon(
    days: int = Query(7, ge=1, le=365, description="Days ahead to look"),
    current_user: User = Depends(get_current_user)
):
    """Get exit processes completing in the next N days"""
    # Check permission
    require_permission(current_user, "exit_management", "read")
    
    exits = await exit_service.get_exits_completing_soon(days)
    return exits


@router.post("/{exit_id}/documents/issue", response_model=ExitManagementResponse)
async def issue_documents(
    exit_id: str,
    document_types: List[str],
    current_user: User = Depends(get_current_user)
):
    """Issue exit documents"""
    # Check permission
    require_permission(current_user, "exit_management", "update")
    
    # Validate document types
    valid_documents = ["experience_letter", "relieving_letter"]
    for doc_type in document_types:
        if doc_type not in valid_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {doc_type}. Valid types: {valid_documents}"
            )
    
    exit_management = await exit_service.issue_documents(
        exit_id, document_types, current_user.username
    )
    return exit_management


@router.get("/me", response_model=ExitManagementResponse)
async def get_my_exit_process(
    current_user: User = Depends(get_current_user)
):
    """Get current user's exit process"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit process not found for this user"
        )
    
    exit_management = await exit_service.get_exit_by_employee(current_user.employee_id)
    return exit_management


@router.post("/me/feedback", response_model=ExitManagementResponse)
async def submit_my_feedback(
    feedback_data: ExitFeedback,
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for current user's exit process"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit process not found for this user"
        )
    
    exit_management = await exit_service.get_exit_by_employee(current_user.employee_id)
    
    updated_exit_management = await exit_service.submit_exit_feedback(
        str(exit_management.id), feedback_data, current_user.username
    )
    return updated_exit_management


@router.get("/me/clearance")
async def get_my_clearance_status(
    current_user: User = Depends(get_current_user)
):
    """Get clearance status for current user's exit process"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit process not found for this user"
        )
    
    exit_management = await exit_service.get_exit_by_employee(current_user.employee_id)
    clearance_status = await exit_service.get_clearance_status(str(exit_management.id))
    return clearance_status


@router.get("/me/summary")
async def get_my_exit_summary(
    current_user: User = Depends(get_current_user)
):
    """Get exit process summary for current user"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit process not found for this user"
        )
    
    exit_management = await exit_service.get_exit_by_employee(current_user.employee_id)
    summary = await exit_service.get_exit_summary(str(exit_management.id))
    return summary
