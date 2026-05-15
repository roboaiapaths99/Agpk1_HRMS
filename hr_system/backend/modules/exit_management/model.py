from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum


class ExitStatus(str, Enum):
    INITIATED = "initiated"
    NOTICE_PERIOD = "notice_period"
    HANDOVER_IN_PROGRESS = "handover_in_progress"
    FINAL_CLEARANCE = "final_clearance"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class ExitReason(str, Enum):
    RESIGNATION = "resignation"
    TERMINATION = "termination"
    RETIREMENT = "retirement"
    CONTRACT_END = "contract_end"
    ABSENTEEISM = "absenteeism"
    MUTUAL_CONSENT = "mutual_consent"
    OTHER = "other"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ExitTask(Document):
    """Individual task in exit management process"""
    
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to: Optional[str] = Field(None, description="Person responsible")
    department: Optional[str] = Field(None, description="Department responsible")
    
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: str = Field(default="medium", description="Task priority")
    
    due_date: Optional[date] = Field(None, description="Task due date")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    completed_by: Optional[str] = Field(None, description="Who completed the task")
    
    attachments: List[dict] = Field(default_factory=list, description="Task attachments")
    notes: Optional[str] = Field(None, description="Task notes")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "exit_tasks"


class ExitManagement(Document):
    """Exit management process document"""
    
    # Basic Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    designation: str = Field(..., description="Employee designation")
    
    # Exit Details
    exit_reason: ExitReason = Field(..., description="Reason for exit")
    resignation_date: date = Field(..., description="Date of resignation/initiation")
    last_working_day: date = Field(..., description="Last working day")
    actual_exit_date: Optional[date] = Field(None, description="Actual exit date")
    
    # Status and Workflow
    status: ExitStatus = Field(default=ExitStatus.INITIATED, description="Exit process status")
    
    # Notice Period
    notice_period_days: int = Field(..., ge=0, description="Notice period in days")
    notice_period_served: int = Field(default=0, ge=0, description="Notice period days served")
    notice_period_waived: bool = Field(default=False, description="Notice period waived")
    notice_period_waiver_reason: Optional[str] = Field(None, description="Reason for waiver")
    
    # Exit Interview
    exit_interview_scheduled: bool = Field(default=False, description="Exit interview scheduled")
    exit_interview_date: Optional[date] = Field(None, description="Exit interview date")
    exit_interview_conducted: bool = Field(default=False, description="Exit interview conducted")
    exit_interviewer: Optional[str] = Field(None, description="Exit interviewer")
    exit_interview_notes: Optional[str] = Field(None, description="Exit interview notes")
    exit_interview_feedback: Optional[str] = Field(None, description="Exit interview feedback")
    
    # Handover Process
    handover_responsible_person: Optional[str] = Field(None, description="Handover responsible person")
    handover_plan_submitted: bool = Field(default=False, description="Handover plan submitted")
    handover_plan_date: Optional[date] = Field(None, description="Handover plan submission date")
    handover_completed: bool = Field(default=False, description="Handover completed")
    handover_completion_date: Optional[date] = Field(None, description="Handover completion date")
    
    # Tasks
    tasks: List[ExitTask] = Field(default_factory=list, description="Exit process tasks")
    
    # Asset and Access Management
    company_assets_returned: bool = Field(default=False, description="All company assets returned")
    asset_return_details: List[dict] = Field(default_factory=list, description="Asset return details")
    
    # System Access
    email_deactivated: bool = Field(default=False, description="Email account deactivated")
    system_access_revoked: bool = Field(default=False, description="System access revoked")
    access_cards_returned: bool = Field(default=False, description="Access cards returned")
    
    # Financial Clearance
    final_settlement_calculated: bool = Field(default=False, description="Final settlement calculated")
    final_settlement_amount: Optional[float] = Field(None, description="Final settlement amount")
    final_settlement_date: Optional[date] = Field(None, description="Final settlement date")
    final_settlement_paid: bool = Field(default=False, description="Final settlement paid")
    
    # Deductions and Adjustments
    notice_period_deduction: Optional[float] = Field(None, description="Notice period deduction")
    other_deductions: List[dict] = Field(default_factory=list, description="Other deductions")
    adjustments: List[dict] = Field(default_factory=list, description="Adjustments")
    
    # Documents
    exit_form_submitted: bool = Field(default=False, description="Exit form submitted")
    experience_letter_requested: bool = Field(default=False, description="Experience letter requested")
    experience_letter_issued: bool = Field(default=False, description="Experience letter issued")
    relieving_letter_issued: bool = Field(default=False, description="Relieving letter issued")
    
    # Compliance and Legal
    nda_signed: bool = Field(default=False, description="NDA signed")
    legal_clearance: bool = Field(default=False, description="Legal clearance completed")
    
    # Feedback and Surveys
    hr_feedback: Optional[str] = Field(None, description="HR team feedback")
    manager_feedback: Optional[str] = Field(None, description="Manager feedback")
    team_feedback: Optional[str] = Field(None, description="Team feedback")
    
    # Progress Tracking
    completion_percentage: float = Field(default=0, ge=0, le=100, description="Completion percentage")
    tasks_completed: int = Field(default=0, description="Completed tasks count")
    total_tasks: int = Field(default=0, description="Total tasks count")
    
    # Issues and Blockers
    blockers: List[dict] = Field(default_factory=list, description="Current blockers")
    escalation_required: bool = Field(default=False, description="Escalation required")
    
    # Audit Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="HR personnel who initiated exit")
    assigned_to: Optional[str] = Field(None, description="HR personnel responsible for exit")
    
    # Comments and Notes
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    employee_notes: Optional[str] = Field(None, description="Employee notes")
    
    class Settings:
        name = "exit_management"
        indexes = [
            "employee_id",
            "employee_code",
            "status",
            "resignation_date",
            "last_working_day",
            "department",
            "assigned_to"
        ]
    
    @validator('last_working_day')
    def validate_last_working_day(cls, v, values):
        """Validate last working day is after resignation date"""
        resignation_date = values.get('resignation_date')
        if resignation_date and v <= resignation_date:
            raise ValueError('Last working day must be after resignation date')
        return v
    
    async def calculate_progress(self):
        """Calculate exit process progress"""
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
        
        # Check if all critical tasks are completed
        if self.is_exit_ready():
            self.status = ExitStatus.FINAL_CLEARANCE
        
        await self.save()
    
    def is_exit_ready(self) -> bool:
        """Check if exit is ready for final clearance"""
        required_items = [
            self.handover_completed,
            self.company_assets_returned,
            self.email_deactivated,
            self.system_access_revoked,
            self.exit_interview_conducted,
            self.legal_clearance
        ]
        return all(required_items)
    
    async def calculate_final_settlement(self):
        """Calculate final settlement amount"""
        # This would integrate with payroll system
        # For now, it's a placeholder
        from datetime import timedelta
        
        # Calculate days worked in final month
        last_day = self.last_working_day
        first_day = last_day.replace(day=1)
        days_worked = (last_day - first_day).days + 1
        
        # Get employee salary (would fetch from employee record)
        daily_salary = 1000  # Placeholder
        
        # Basic settlement
        settlement = days_worked * daily_salary
        
        # Add leave encashment, bonus, etc.
        # Subtract notice period deduction if applicable
        
        self.final_settlement_amount = settlement
        self.final_settlement_calculated = True
        await self.save()
    
    async def add_task(self, task_data: dict):
        """Add a new exit task"""
        task = ExitTask(**task_data)
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
    
    def get_overdue_tasks(self) -> List[ExitTask]:
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
    
    @property
    def days_until_exit(self) -> int:
        """Calculate days until exit"""
        return (self.last_working_day - date.today()).days
    
    @property
    def notice_period_remaining(self) -> int:
        """Calculate remaining notice period"""
        return max(0, self.days_until_exit)
    
    @property
    def is_overdue(self) -> bool:
        """Check if exit process is overdue"""
        return date.today() > self.last_working_day and self.status != ExitStatus.COMPLETED
    
    async def add_asset_return(self, asset_name: str, asset_id: str, return_date: date, condition: str):
        """Add asset return record"""
        asset = {
            "name": asset_name,
            "asset_id": asset_id,
            "return_date": return_date,
            "condition": condition,
            "received_by": "HR",
            "notes": ""
        }
        self.asset_return_details.append(asset)
        await self.save()
    
    async def add_deduction(self, deduction_type: str, amount: float, description: str):
        """Add a deduction to final settlement"""
        deduction = {
            "type": deduction_type,
            "amount": amount,
            "description": description,
            "created_at": datetime.utcnow()
        }
        self.other_deductions.append(deduction)
        await self.save()
    
    async def add_adjustment(self, adjustment_type: str, amount: float, description: str):
        """Add an adjustment to final settlement"""
        adjustment = {
            "type": adjustment_type,
            "amount": amount,
            "description": description,
            "created_at": datetime.utcnow()
        }
        self.adjustments.append(adjustment)
        await self.save()
    
    async def complete_exit(self, completion_date: date):
        """Complete the exit process"""
        self.status = ExitStatus.COMPLETED
        self.actual_exit_date = completion_date
        await self.save()
    
    def get_exit_summary(self) -> dict:
        """Get exit process summary"""
        return {
            "employee_code": self.employee_code,
            "employee_name": self.employee_name,
            "exit_reason": self.exit_reason.value,
            "resignation_date": self.resignation_date,
            "last_working_day": self.last_working_day,
            "status": self.status.value,
            "completion_percentage": self.completion_percentage,
            "days_until_exit": self.days_until_exit
        }
    
    def get_clearance_status(self) -> dict:
        """Get clearance status for all departments"""
        return {
            "hr_clearance": self.exit_interview_conducted,
            "it_clearance": self.system_access_revoked,
            "asset_clearance": self.company_assets_returned,
            "finance_clearance": self.final_settlement_calculated,
            "admin_clearance": self.access_cards_returned,
            "legal_clearance": self.legal_clearance
        }
