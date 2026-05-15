from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class OnboardingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OnboardingBase(BaseModel):
    """Base onboarding schema"""
    employee_id: str
    employee_code: str
    department: str
    designation: str
    start_date: date
    end_date: Optional[date] = None
    status: OnboardingStatus = OnboardingStatus.PENDING


class OnboardingCreate(OnboardingBase):
    """Create onboarding schema"""
    buddy_id: Optional[str] = None
    buddy_name: Optional[str] = None
    schedule_id: Optional[str] = None
    template_id: Optional[str] = None
    notes: Optional[str] = None


class OnboardingUpdate(BaseModel):
    """Update onboarding schema"""
    status: Optional[OnboardingStatus] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    buddy_id: Optional[str] = None
    buddy_name: Optional[str] = None


class OnboardingSearch(BaseModel):
    """Search onboarding schema"""
    status: Optional[OnboardingStatus] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None
    employee_code: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    created_by: Optional[str] = None


class OnboardingTaskBase(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None
    category: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class OnboardingTaskCreate(OnboardingTaskBase):
    """Create task schema"""
    onboarding_id: str
    checklist_item: Optional[str] = None
    template_task_id: Optional[str] = None


class OnboardingTaskUpdate(BaseModel):
    """Update task schema"""
    status: Optional[TaskStatus] = None
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class OnboardingResponse(OnboardingBase):
    """Response schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    progress: float
    tasks: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    checklists: List[Dict[str, Any]] = []
    feedback: List[Dict[str, Any]] = []


class OnboardingListResponse(BaseModel):
    """List response schema"""
    onboardings: List[OnboardingResponse]
    total: int
    page: int
    page_size: int


class OnboardingStatistics(BaseModel):
    """Statistics schema"""
    total_onboardings: int
    pending_onboardings: int
    in_progress_onboardings: int
    completed_onboardings: int
    cancelled_onboardings: int
    average_completion_days: float
    completion_rate: float


class DocumentUpload(BaseModel):
    """Document upload schema"""
    document_type: str
    file_name: str
    file_size: int
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: str
    document_type: str
    file_name: str
    file_size: int
    uploaded_at: datetime
    uploaded_by: str


class ChecklistItemCreate(BaseModel):
    """Checklist item create schema"""
    onboarding_id: str
    item: str
    category: str
    required: bool = True
    due_date: Optional[date] = None


class ChecklistItemUpdate(BaseModel):
    """Checklist item update schema"""
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class FeedbackCreate(BaseModel):
    """Feedback create schema"""
    onboarding_id: str
    feedback_type: str
    rating: Optional[int] = None
    comments: Optional[str] = None
    submitted_by: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response schema"""
    id: str
    feedback_type: str
    rating: Optional[int]
    comments: Optional[str]
    submitted_at: datetime
    submitted_by: str


class BulkAction(BaseModel):
    """Bulk action schema"""
    action: str
    onboarding_ids: List[str]
    parameters: Optional[Dict[str, Any]] = None


class OnboardingExport(BaseModel):
    """Export schema"""
    format: str = "csv"
    date_range: Optional[Dict[str, str]] = None
    include_completed: bool = True
    include_pending: bool = True
    department: Optional[str] = None
