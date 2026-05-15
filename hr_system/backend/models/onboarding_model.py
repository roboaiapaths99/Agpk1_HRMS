from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
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


class OnboardingTask(Document):
    """Onboarding task document"""
    
    # Task Details
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    category: str = Field(..., description="Task category")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    # Assignment
    assigned_to: Optional[str] = Field(None, description="Assigned to user")
    department: Optional[str] = Field(None, description="Responsible department")
    
    # Dates
    due_date: Optional[date] = Field(None, description="Task due date")
    start_date: Optional[date] = Field(None, description="Task start date")
    
    # Status
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    progress: int = Field(default=0, ge=0, le=100, description="Task progress percentage")
    
    # Completion
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    completed_by: Optional[str] = Field(None, description="User who completed task")
    
    # Additional Information
    notes: Optional[str] = Field(None, description="Task notes")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Task attachments")
    checklist: List[Dict[str, Any]] = Field(default_factory=list, description="Task checklist")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created task")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "onboarding_tasks"
    #     # indexes = [
    #     #     "status",
    #     #     "priority",
    #     #     "assigned_to",
    #     #     "department",
    #     #     "due_date",
    #     #     "created_at"
    #     # ]
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return date.today() > self.due_date and self.status != TaskStatus.CANCELLED
    
    def get_days_until_due(self) -> Optional[int]:
        """Get days until due date"""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days
    
    def mark_completed(self, completed_by: str, notes: Optional[str] = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by
        if notes:
            self.notes = notes
        self.updated_at = datetime.utcnow()
    
    def assign_to(self, assigned_to: str):
        """Assign task to user"""
        self.assigned_to = assigned_to
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, progress: int):
        """Update task progress"""
        self.progress = max(0, min(100, progress))
        if progress == 100:
            self.status = TaskStatus.COMPLETED
        elif progress > 0:
            self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
    
    def add_attachment(self, file_url: str, file_name: str = None):
        """Add attachment to task"""
        attachment = {
            "file_url": file_url,
            "file_name": file_name or file_url.split('/')[-1],
            "uploaded_at": datetime.utcnow()
        }
        self.attachments.append(attachment)
        return attachment
    
    def add_checklist_item(self, title: str, completed: bool = False):
        """Add checklist item"""
        item = {
            "title": title,
            "completed": completed,
            "added_at": datetime.utcnow()
        }
        self.checklist.append(item)
        return item
    
    def update_checklist_item(self, index: int, completed: bool):
        """Update checklist item completion"""
        if 0 <= index < len(self.checklist):
            self.checklist[index]["completed"] = completed
            self.checklist[index]["updated_at"] = datetime.utcnow()
            
            # Update overall progress
            completed_items = sum(1 for item in self.checklist if item["completed"])
            total_items = len(self.checklist)
            self.progress = (completed_items / total_items * 100) if total_items > 0 else 0
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get task summary"""
        return {
            "title": self.title,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress": self.progress,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date,
            "days_until_due": self.get_days_until_due(),
            "is_overdue": self.is_overdue(),
            "completed_at": self.completed_at,
            "completed_by": self.completed_by,
            "checklist_progress": {
                "total_items": len(self.checklist),
                "completed_items": sum(1 for item in self.checklist if item["completed"]),
                "completion_percentage": (sum(1 for item in self.checklist if item["completed"]) / len(self.checklist) * 100) if self.checklist else 0
            }
        }


class Onboarding(Document):
    """Onboarding document for MongoDB"""
    
    # Employee Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Department")
    designation: str = Field(..., description="Designation")
    
    # Onboarding Schedule
    start_date: date = Field(..., description="Onboarding start date")
    expected_completion_date: date = Field(..., description="Expected completion date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    
    # Status
    status: OnboardingStatus = Field(default=OnboardingStatus.PENDING, description="Onboarding status")
    progress: int = Field(default=0, ge=0, le=100, description="Overall progress percentage")
    
    # Assignment
    assigned_to: str = Field(..., description="HR manager assigned")
    buddy: Optional[str] = Field(None, description="Buddy/mentor assigned")
    
    # Tasks
    tasks: List[OnboardingTask] = Field(default_factory=list, description="Onboarding tasks")
    
    # Documents
    documents_required: List[str] = Field(default_factory=list, description="Required documents")
    documents_submitted: List[Dict[str, Any]] = Field(default_factory=list, description="Submitted documents")
    
    # Checklists
    hr_checklist: List[Dict[str, Any]] = Field(default_factory=list, description="HR checklist")
    it_checklist: List[Dict[str, Any]] = Field(default_factory=list, description="IT checklist")
    team_checklist: List[Dict[str, Any]] = Field(default_factory=list, description="Team checklist")
    
    # Feedback
    employee_feedback: Optional[Dict[str, Any]] = Field(None, description="Employee feedback")
    hr_feedback: Optional[Dict[str, Any]] = Field(None, description="HR feedback")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created onboarding")
    last_modified_by: Optional[str] = Field(None, description="User who last modified onboarding")
    
    # Additional Information
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "onboardings"
    #     # indexes = [
    #     #     "employee_id",
    #     #     "employee_code",
    #     #     "department",
    #     #     "status",
    #     #     "start_date",
    #     #     "expected_completion_date",
    #     #     "assigned_to"
    #     # ]
    
    @validator('expected_completion_date')
    def validate_completion_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('Expected completion date must be after start date')
        return v
    
    def calculate_progress(self) -> int:
        """Calculate overall progress based on tasks"""
        if not self.tasks:
            return 0
        
        total_progress = sum(task.progress for task in self.tasks)
        return int(total_progress / len(self.tasks))
    
    def update_progress(self):
        """Update overall progress"""
        self.progress = self.calculate_progress()
        self.updated_at = datetime.utcnow()
        
        # Update status based on progress
        if self.progress == 100:
            self.status = OnboardingStatus.COMPLETED
            self.actual_completion_date = date.today()
        elif self.progress > 0:
            self.status = OnboardingStatus.IN_PROGRESS
    
    def get_completed_tasks(self) -> List[OnboardingTask]:
        """Get completed tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]
    
    def get_pending_tasks(self) -> List[OnboardingTask]:
        """Get pending tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]
    
    def get_overdue_tasks(self) -> List[OnboardingTask]:
        """Get overdue tasks"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_tasks_by_category(self, category: str) -> List[OnboardingTask]:
        """Get tasks by category"""
        return [task for task in self.tasks if task.category == category]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[OnboardingTask]:
        """Get tasks by priority"""
        return [task for task in self.tasks if task.priority == priority]
    
    def add_task(self, task_data: Dict[str, Any]) -> OnboardingTask:
        """Add new task to onboarding"""
        task = OnboardingTask(**task_data)
        self.tasks.append(task)
        self.update_progress()
        return task
    
    def complete_task(self, task_id: str, completed_by: str, notes: Optional[str] = None):
        """Complete a specific task"""
        for task in self.tasks:
            if str(task.id) == task_id:
                task.mark_completed(completed_by, notes)
                break
        self.update_progress()
    
    def assign_buddy(self, buddy: str):
        """Assign buddy/mentor"""
        self.buddy = buddy
        self.updated_at = datetime.utcnow()
    
    def add_document(self, doc_type: str, file_url: str, file_name: str = None):
        """Add submitted document"""
        document = {
            "type": doc_type,
            "file_url": file_url,
            "file_name": file_name or file_url.split('/')[-1],
            "submitted_at": datetime.utcnow()
        }
        self.documents_submitted.append(document)
        return document
    
    def get_document_by_type(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """Get document by type"""
        for doc in self.documents_submitted:
            if doc["type"] == doc_type:
                return doc
        return None
    
    def has_all_required_documents(self) -> bool:
        """Check if all required documents are submitted"""
        for doc_type in self.documents_required:
            if not self.get_document_by_type(doc_type):
                return False
        return True
    
    def update_checklist_item(self, checklist_type: str, index: int, completed: bool):
        """Update checklist item completion"""
        checklists = {
            "hr": self.hr_checklist,
            "it": self.it_checklist,
            "team": self.team_checklist
        }
        
        if checklist_type in checklists:
            checklist = checklists[checklist_type]
            if 0 <= index < len(checklist):
                checklist[index]["completed"] = completed
                checklist[index]["updated_at"] = datetime.utcnow()
                self.update_progress()
    
    def add_employee_feedback(self, feedback_data: Dict[str, Any]):
        """Add employee feedback"""
        feedback_data["submitted_at"] = datetime.utcnow()
        self.employee_feedback = feedback_data
        self.updated_at = datetime.utcnow()
    
    def add_hr_feedback(self, feedback_data: Dict[str, Any]):
        """Add HR feedback"""
        feedback_data["submitted_at"] = datetime.utcnow()
        self.hr_feedback = feedback_data
        self.updated_at = datetime.utcnow()
    
    def get_completion_duration(self) -> Optional[int]:
        """Get completion duration in days"""
        if not self.actual_completion_date:
            return None
        return (self.actual_completion_date - self.start_date).days
    
    def get_days_remaining(self) -> Optional[int]:
        """Get days remaining until expected completion"""
        if self.status == OnboardingStatus.COMPLETED:
            return None
        return (self.expected_completion_date - date.today()).days
    
    def is_overdue(self) -> bool:
        """Check if onboarding is overdue"""
        if self.status == OnboardingStatus.COMPLETED:
            return False
        return date.today() > self.expected_completion_date
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total_tasks = len(self.tasks)
        completed_tasks = len(self.get_completed_tasks())
        pending_tasks = len(self.get_pending_tasks())
        overdue_tasks = len(self.get_overdue_tasks())
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "tasks_by_category": {
                category: len(self.get_tasks_by_category(category))
                for category in set(task.category for task in self.tasks)
            },
            "tasks_by_priority": {
                priority.value: len(self.get_tasks_by_priority(priority))
                for priority in TaskPriority
            }
        }
    
    def get_onboarding_summary(self) -> Dict[str, Any]:
        """Get complete onboarding summary"""
        return {
            "employee_info": {
                "employee_code": self.employee_code,
                "employee_name": self.employee_name,
                "department": self.department,
                "designation": self.designation
            },
            "schedule": {
                "start_date": self.start_date,
                "expected_completion_date": self.expected_completion_date,
                "actual_completion_date": self.actual_completion_date,
                "days_remaining": self.get_days_remaining(),
                "is_overdue": self.is_overdue()
            },
            "status": {
                "status": self.status.value,
                "progress": self.progress
            },
            "assignment": {
                "assigned_to": self.assigned_to,
                "buddy": self.buddy
            },
            "tasks": self.get_task_statistics(),
            "documents": {
                "required_documents": self.documents_required,
                "submitted_documents": len(self.documents_submitted),
                "has_all_documents": self.has_all_required_documents()
            },
            "checklists": {
                "hr_checklist_completed": sum(1 for item in self.hr_checklist if item.get("completed", False)),
                "it_checklist_completed": sum(1 for item in self.it_checklist if item.get("completed", False)),
                "team_checklist_completed": sum(1 for item in self.team_checklist if item.get("completed", False))
            },
            "feedback": {
                "employee_feedback": self.employee_feedback,
                "hr_feedback": self.hr_feedback
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed fields"""
        data = self.dict()
        data.update({
            "task_statistics": self.get_task_statistics(),
            "onboarding_summary": self.get_onboarding_summary(),
            "days_remaining": self.get_days_remaining(),
            "is_overdue": self.is_overdue(),
            "completion_duration": self.get_completion_duration(),
            "has_all_required_documents": self.has_all_required_documents()
        })
        return data
