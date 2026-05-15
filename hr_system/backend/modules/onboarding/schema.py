from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class OnboardingTaskBase(BaseModel):
    """Base onboarding task schema"""
    title: str = Field(..., min_length=2, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to: Optional[str] = Field(None, description="Person responsible for task")
    department: Optional[str] = Field(None, description="Department responsible")
    priority: str = Field(default="medium", description="Task priority")
    due_date: Optional[date] = Field(None, description="Task due date")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    notes: Optional[str] = Field(None, description="Task notes")


class OnboardingTaskCreate(OnboardingTaskBase):
    """Schema for creating onboarding task"""
    pass


class OnboardingTaskUpdate(BaseModel):
    """Schema for updating onboarding task"""
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="Task status")
    priority: Optional[str] = Field(None)
    due_date: Optional[date] = Field(None)
    completed_by: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)


class OnboardingTaskResponse(BaseModel):
    """Schema for onboarding task response"""
    id: str
    title: str
    description: Optional[str]
    assigned_to: Optional[str]
    department: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    completed_at: Optional[datetime]
    completed_by: Optional[str]
    dependencies: List[str]
    attachments: List[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OnboardingBase(BaseModel):
    """Base onboarding schema"""
    employee_id: str = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    start_date: date = Field(..., description="Onboarding start date")
    expected_completion_date: date = Field(..., description="Expected completion date")
    
    # Checklist items
    documentation_completed: bool = Field(default=False, description="All documentation completed")
    it_setup_completed: bool = Field(default=False, description="IT setup completed")
    hr_briefing_completed: bool = Field(default=False, description="HR briefing completed")
    team_introduction_completed: bool = Field(default=False, description="Team introduction completed")
    
    # Hardware and software
    laptop_assigned: bool = Field(default=False, description="Laptop assigned")
    email_created: bool = Field(default=False, description="Email account created")
    system_access_granted: bool = Field(default=False, description="System access granted")
    software_installed: List[str] = Field(default_factory=list, description="Software installed")
    
    # Facilities and access
    id_card_issued: bool = Field(default=False, description="ID card issued")
    access_card_issued: bool = Field(default=False, description="Access card issued")
    workspace_allocated: bool = Field(default=False, description="Workspace allocated")
    
    # Training and orientation
    orientation_completed: bool = Field(default=False, description="Orientation session completed")
    policy_acknowledgment: bool = Field(default=False, description="Company policies acknowledged")
    compliance_training: bool = Field(default=False, description="Compliance training completed")
    role_specific_training: List[str] = Field(default_factory=list, description="Role-specific training completed")
    
    # Benefits and payroll
    benefits_enrollment: bool = Field(default=False, description="Benefits enrollment completed")
    payroll_setup: bool = Field(default=False, description="Payroll setup completed")
    bank_details_verified: bool = Field(default=False, description="Bank details verified")
    
    # Team integration
    buddy_assigned: Optional[str] = Field(None, description="Buddy/mentor assigned")
    manager_meeting_scheduled: bool = Field(default=False, description="Initial manager meeting scheduled")
    team_meeting_scheduled: bool = Field(default=False, description="Team introduction meeting scheduled")
    
    # Notes
    employee_feedback: Optional[str] = Field(None, description="Feedback from employee")
    hr_notes: Optional[str] = Field(None, description="HR team notes")
    manager_notes: Optional[str] = Field(None, description="Manager notes")


class OnboardingCreate(OnboardingBase):
    """Schema for creating onboarding"""
    assigned_to: Optional[str] = Field(None, description="HR personnel responsible for onboarding")
    tasks: Optional[List[OnboardingTaskCreate]] = Field(default_factory=list, description="Initial tasks")


class OnboardingUpdate(BaseModel):
    """Schema for updating onboarding"""
    expected_completion_date: Optional[date] = Field(None)
    status: Optional[str] = Field(None, description="Overall status")
    actual_completion_date: Optional[date] = Field(None)
    
    # Checklist items
    documentation_completed: Optional[bool] = Field(None)
    it_setup_completed: Optional[bool] = Field(None)
    hr_briefing_completed: Optional[bool] = Field(None)
    team_introduction_completed: Optional[bool] = Field(None)
    
    # Hardware and software
    laptop_assigned: Optional[bool] = Field(None)
    email_created: Optional[bool] = Field(None)
    system_access_granted: Optional[bool] = Field(None)
    software_installed: Optional[List[str]] = Field(None)
    
    # Facilities and access
    id_card_issued: Optional[bool] = Field(None)
    access_card_issued: Optional[bool] = Field(None)
    workspace_allocated: Optional[bool] = Field(None)
    
    # Training and orientation
    orientation_completed: Optional[bool] = Field(None)
    policy_acknowledgment: Optional[bool] = Field(None)
    compliance_training: Optional[bool] = Field(None)
    role_specific_training: Optional[List[str]] = Field(None)
    
    # Benefits and payroll
    benefits_enrollment: Optional[bool] = Field(None)
    payroll_setup: Optional[bool] = Field(None)
    bank_details_verified: Optional[bool] = Field(None)
    
    # Team integration
    buddy_assigned: Optional[str] = Field(None)
    manager_meeting_scheduled: Optional[bool] = Field(None)
    team_meeting_scheduled: Optional[bool] = Field(None)
    
    # Notes
    employee_feedback: Optional[str] = Field(None)
    hr_notes: Optional[str] = Field(None)
    manager_notes: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)


class OnboardingResponse(BaseModel):
    """Schema for onboarding response"""
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    department: str
    status: str
    start_date: date
    expected_completion_date: date
    actual_completion_date: Optional[date]
    tasks: List[OnboardingTaskResponse]
    
    # Checklist items
    documentation_completed: bool
    it_setup_completed: bool
    hr_briefing_completed: bool
    team_introduction_completed: bool
    
    # Hardware and software
    laptop_assigned: bool
    email_created: bool
    system_access_granted: bool
    software_installed: List[str]
    
    # Facilities and access
    id_card_issued: bool
    access_card_issued: bool
    workspace_allocated: bool
    
    # Training and orientation
    orientation_completed: bool
    policy_acknowledgment: bool
    compliance_training: bool
    role_specific_training: List[str]
    
    # Benefits and payroll
    benefits_enrollment: bool
    payroll_setup: bool
    bank_details_verified: bool
    
    # Team integration
    buddy_assigned: Optional[str]
    manager_meeting_scheduled: bool
    team_meeting_scheduled: bool
    
    # Progress tracking
    completion_percentage: float
    tasks_completed: int
    total_tasks: int
    
    # Issues and blockers
    blockers: List[Dict[str, Any]]
    escalation_required: bool
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    assigned_to: Optional[str]
    
    # Notes
    employee_feedback: Optional[str]
    hr_notes: Optional[str]
    manager_notes: Optional[str]
    
    class Config:
        from_attributes = True


class OnboardingListResponse(BaseModel):
    """Schema for onboarding list response"""
    onboardings: List[OnboardingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OnboardingSearch(BaseModel):
    """Schema for onboarding search"""
    query: Optional[str] = Field(None, description="Search query")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned person")
    start_date_from: Optional[date] = Field(None, description="Start date from")
    start_date_to: Optional[date] = Field(None, description="Start date to")
    completion_date_from: Optional[date] = Field(None, description="Completion date from")
    completion_date_to: Optional[date] = Field(None, description="Completion date to")
    overdue_only: bool = Field(default=False, description="Show only overdue onboardings")


class OnboardingTaskCreate(BaseModel):
    """Schema for creating a task in existing onboarding"""
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    priority: str = Field(default="medium")
    due_date: Optional[date] = Field(None)
    dependencies: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None)


class OnboardingTaskUpdate(BaseModel):
    """Schema for updating task status"""
    status: str = Field(..., description="Task status")
    notes: Optional[str] = Field(None, description="Task notes")


class OnboardingBlocker(BaseModel):
    """Schema for adding a blocker"""
    blocker_description: str = Field(..., description="Blocker description")
    severity: str = Field(default="medium", description="Blocker severity")


class OnboardingTemplate(BaseModel):
    """Schema for onboarding template"""
    name: str = Field(..., description="Template name")
    department: str = Field(..., description="Department")
    description: Optional[str] = Field(None, description="Template description")
    tasks: List[OnboardingTaskCreate] = Field(..., description="Template tasks")
    default_duration_days: int = Field(default=30, description="Default onboarding duration")
    is_active: bool = Field(default=True, description="Template active status")


class OnboardingStatistics(BaseModel):
    """Schema for onboarding statistics"""
    total_onboardings: int
    active_onboardings: int
    completed_onboardings: int
    overdue_onboardings: int
    average_completion_days: float
    department_breakdown: List[Dict[str, Any]]
    completion_rate: float
    tasks_by_status: Dict[str, int]


class OnboardingChecklistUpdate(BaseModel):
    """Schema for updating checklist items"""
    checklist_type: str = Field(..., description="Type of checklist")
    items: Dict[str, bool] = Field(..., description="Checklist items and their status")


class OnboardingFeedback(BaseModel):
    """Schema for onboarding feedback"""
    rating: int = Field(..., ge=1, le=5, description="Overall rating")
    process_rating: int = Field(..., ge=1, le=5, description="Process rating")
    support_rating: int = Field(..., ge=1, le=5, description="Support rating")
    what_went_well: List[str] = Field(default_factory=list, description="What went well")
    what_could_be_improved: List[str] = Field(default_factory=list, description="What could be improved")
    suggestions: Optional[str] = Field(None, description="Additional suggestions")
    would_recommend: bool = Field(..., description="Would recommend to others")
