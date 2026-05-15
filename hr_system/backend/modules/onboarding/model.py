from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum


class OnboardingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


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
    CRITICAL = "critical"


class OnboardingTask(Document):
    """Individual task within onboarding process"""
    
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to: Optional[str] = Field(None, description="Person responsible for task")
    department: Optional[str] = Field(None, description="Department responsible")
    
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    due_date: Optional[date] = Field(None, description="Task due date")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    completed_by: Optional[str] = Field(None, description="Who completed the task")
    
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    attachments: List[dict] = Field(default_factory=list, description="Task attachments")
    notes: Optional[str] = Field(None, description="Task notes")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "onboarding_tasks"
        indexes = [
            "assigned_to",
            "status",
            "priority",
            "due_date",
            "department"
        ]


class Onboarding(Document):
    """Main onboarding process document"""
    
    # Basic Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    
    # Onboarding Process
    status: OnboardingStatus = Field(default=OnboardingStatus.PENDING, description="Overall status")
    start_date: date = Field(..., description="Onboarding start date")
    expected_completion_date: date = Field(..., description="Expected completion date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    
    # Tasks
    tasks: List[OnboardingTask] = Field(default_factory=list, description="Onboarding tasks")
    
    # Checklist Items (Standard HR items)
    documentation_completed: bool = Field(default=False, description="All documentation completed")
    it_setup_completed: bool = Field(default=False, description="IT setup completed")
    hr_briefing_completed: bool = Field(default=False, description="HR briefing completed")
    team_introduction_completed: bool = Field(default=False, description="Team introduction completed")
    
    # Hardware and Software
    laptop_assigned: bool = Field(default=False, description="Laptop assigned")
    email_created: bool = Field(default=False, description="Email account created")
    system_access_granted: bool = Field(default=False, description="System access granted")
    software_installed: List[str] = Field(default_factory=list, description="Software installed")
    
    # Facilities and Access
    id_card_issued: bool = Field(default=False, description="ID card issued")
    access_card_issued: bool = Field(default=False, description="Access card issued")
    workspace_allocated: bool = Field(default=False, description="Workspace allocated")
    
    # Training and Orientation
    orientation_completed: bool = Field(default=False, description="Orientation session completed")
    policy_acknowledgment: bool = Field(default=False, description="Company policies acknowledged")
    compliance_training: bool = Field(default=False, description="Compliance training completed")
    role_specific_training: List[str] = Field(default_factory=list, description="Role-specific training completed")
    
    # Benefits and Payroll
    benefits_enrollment: bool = Field(default=False, description="Benefits enrollment completed")
    payroll_setup: bool = Field(default=False, description="Payroll setup completed")
    bank_details_verified: bool = Field(default=False, description="Bank details verified")
    
    # Team Integration
    buddy_assigned: Optional[str] = Field(None, description="Buddy/mentor assigned")
    manager_meeting_scheduled: bool = Field(default=False, description="Initial manager meeting scheduled")
    team_meeting_scheduled: bool = Field(default=False, description="Team introduction meeting scheduled")
    
    # Progress Tracking
    completion_percentage: float = Field(default=0, ge=0, le=100, description="Overall completion percentage")
    tasks_completed: int = Field(default=0, description="Number of tasks completed")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    
    # Issues and Blockers
    blockers: List[dict] = Field(default_factory=list, description="Current blockers/issues")
    escalation_required: bool = Field(default=False, description="Escalation required")
    
    # Feedback and Notes
    employee_feedback: Optional[str] = Field(None, description="Feedback from employee")
    hr_notes: Optional[str] = Field(None, description="HR team notes")
    manager_notes: Optional[str] = Field(None, description="Manager notes")
    
    # Audit Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="HR personnel who created onboarding")
    assigned_to: Optional[str] = Field(None, description="HR personnel responsible for onboarding")
    
    class Settings:
        name = "onboarding"
        indexes = [
            "employee_id",
            "employee_code",
            "status",
            "start_date",
            "department",
            "assigned_to"
        ]
    
    @validator('expected_completion_date')
    def validate_completion_date(cls, v, values):
        """Validate completion date is after start date"""
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('Expected completion date must be after start date')
        return v
    
    async def calculate_progress(self):
        """Calculate onboarding progress percentage"""
        if not self.tasks:
            self.completion_percentage = 0
            self.tasks_completed = 0
            self.total_tasks = 0
            await self.save()
            return
        
        completed_tasks = sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
        total_tasks = len(self.tasks)
        
        self.tasks_completed = completed_tasks
        self.total_tasks = total_tasks
        self.completion_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Check if all tasks are completed
        if completed_tasks == total_tasks and total_tasks > 0:
            self.status = OnboardingStatus.COMPLETED
            self.actual_completion_date = date.today()
        
        await self.save()
    
    async def add_task(self, task_data: dict):
        """Add a new task to onboarding"""
        task = OnboardingTask(**task_data)
        self.tasks.append(task)
        await self.calculate_progress()
    
    async def complete_task(self, task_id: str, completed_by: str, notes: Optional[str] = None):
        """Mark a task as completed"""
        for task in self.tasks:
            if str(task.id) == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.completed_by = completed_by
                if notes:
                    task.notes = notes
                break
        
        await self.calculate_progress()
    
    async def update_task_status(self, task_id: str, status: TaskStatus, notes: Optional[str] = None):
        """Update task status"""
        for task in self.tasks:
            if str(task.id) == task_id:
                task.status = status
                if notes:
                    task.notes = notes
                task.updated_at = datetime.utcnow()
                break
        
        await self.calculate_progress()
    
    def get_overdue_tasks(self) -> List[OnboardingTask]:
        """Get list of overdue tasks"""
        today = date.today()
        overdue_tasks = []
        
        for task in self.tasks:
            if (task.due_date and 
                task.due_date < today and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                task.status = TaskStatus.OVERDUE
                overdue_tasks.append(task)
        
        return overdue_tasks
    
    def get_critical_tasks(self) -> List[OnboardingTask]:
        """Get list of critical priority tasks"""
        return [task for task in self.tasks if task.priority == TaskPriority.CRITICAL]
    
    @property
    def days_since_start(self) -> int:
        """Calculate days since onboarding started"""
        return (date.today() - self.start_date).days
    
    @property
    def is_overdue(self) -> bool:
        """Check if onboarding is overdue"""
        return (date.today() > self.expected_completion_date and 
                self.status != OnboardingStatus.COMPLETED)
    
    async def add_blocker(self, blocker_description: str, severity: str = "medium"):
        """Add a blocker to the onboarding process"""
        blocker = {
            "description": blocker_description,
            "severity": severity,
            "created_at": datetime.utcnow(),
            "resolved": False
        }
        self.blockers.append(blocker)
        await self.save()
    
    async def resolve_blocker(self, blocker_index: int, resolution_notes: str):
        """Mark a blocker as resolved"""
        if 0 <= blocker_index < len(self.blockers):
            self.blockers[blocker_index]["resolved"] = True
            self.blockers[blocker_index]["resolved_at"] = datetime.utcnow()
            self.blockers[blocker_index]["resolution_notes"] = resolution_notes
            await self.save()
