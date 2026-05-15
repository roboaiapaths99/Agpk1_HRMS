from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field, validator
from enum import Enum


class ExitStatus(str, Enum):
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


class ExitTask(Document):
    """Exit task document"""
    
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
    #     name = "exit_tasks"
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


class ExitManagement(Document):
    """Exit management document for MongoDB"""
    
    # Employee Information
    employee_id: Indexed(str) = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Department")
    designation: str = Field(..., description="Designation")
    
    # Exit Details
    exit_reason: str = Field(..., description="Reason for exit")
    resignation_date: date = Field(..., description="Date of resignation")
    last_working_day: date = Field(..., description="Last working day")
    notice_period_days: int = Field(..., description="Notice period in days")
    
    # Status
    status: ExitStatus = Field(default=ExitStatus.PENDING, description="Exit process status")
    progress: int = Field(default=0, ge=0, le=100, description="Overall progress percentage")
    
    # Assignment
    assigned_to: str = Field(..., description="HR manager assigned")
    exit_interviewer: Optional[str] = Field(None, description="Exit interviewer")
    
    # Tasks
    tasks: List[ExitTask] = Field(default_factory=list, description="Exit tasks")
    
    # Clearance Process
    hr_clearance: Dict[str, Any] = Field(default_factory=dict, description="HR clearance status")
    it_clearance: Dict[str, Any] = Field(default_factory=dict, description="IT clearance status")
    finance_clearance: Dict[str, Any] = Field(default_factory=dict, description="Finance clearance status")
    asset_clearance: Dict[str, Any] = Field(default_factory=dict, description="Asset clearance status")
    
    # Documents
    documents_required: List[str] = Field(default_factory=list, description="Required documents")
    documents_submitted: List[Dict[str, Any]] = Field(default_factory=list, description="Submitted documents")
    documents_issued: List[Dict[str, Any]] = Field(default_factory=list, description="Documents issued")
    
    # Interview and Feedback
    exit_interview: Optional[Dict[str, Any]] = Field(None, description="Exit interview details")
    employee_feedback: Optional[Dict[str, Any]] = Field(None, description="Employee feedback")
    
    # Financial Settlement
    final_settlement: Optional[Dict[str, Any]] = Field(None, description="Final settlement details")
    settlement_calculated_by: Optional[str] = Field(None, description="User who calculated settlement")
    settlement_calculated_at: Optional[datetime] = Field(None, description="Settlement calculation timestamp")
    settlement_processed_by: Optional[str] = Field(None, description="User who processed settlement")
    settlement_processed_at: Optional[datetime] = Field(None, description="Settlement processing timestamp")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created exit process")
    last_modified_by: Optional[str] = Field(None, description="User who last modified exit process")
    
    # Completion Details
    completed_at: Optional[datetime] = Field(None, description="Exit completion timestamp")
    completed_by: Optional[str] = Field(None, description="User who completed exit process")
    completion_date: Optional[date] = Field(None, description="Actual completion date")
    
    # Additional Information
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Settings class temporarily disabled to avoid index conflicts
    # class Settings:
    #     name = "exit_management"
    #     # indexes = [
    #     #     "employee_id",
    #     #     "employee_code",
    #     #     "department",
    #     #     "status",
    #     #     "resignation_date",
    #     #     "last_working_day",
    #     #     "assigned_to"
    #     # ]
    
    @validator('last_working_day')
    def validate_last_working_day(cls, v, values):
        if 'resignation_date' in values and v <= values['resignation_date']:
            raise ValueError('Last working day must be after resignation date')
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
            self.status = ExitStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            self.completion_date = date.today()
        elif self.progress > 0:
            self.status = ExitStatus.IN_PROGRESS
    
    def get_completed_tasks(self) -> List[ExitTask]:
        """Get completed tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]
    
    def get_pending_tasks(self) -> List[ExitTask]:
        """Get pending tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]
    
    def get_overdue_tasks(self) -> List[ExitTask]:
        """Get overdue tasks"""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_tasks_by_category(self, category: str) -> List[ExitTask]:
        """Get tasks by category"""
        return [task for task in self.tasks if task.category == category]
    
    def get_tasks_by_department(self, department: str) -> List[ExitTask]:
        """Get tasks by department"""
        return [task for task in self.tasks if task.department == department]
    
    def add_task(self, task_data: Dict[str, Any]) -> ExitTask:
        """Add new task to exit process"""
        task = ExitTask(**task_data)
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
    
    def assign_interviewer(self, interviewer: str):
        """Assign exit interviewer"""
        self.exit_interviewer = interviewer
        self.updated_at = datetime.utcnow()
    
    def conduct_exit_interview(self, interview_data: Dict[str, Any]):
        """Conduct exit interview"""
        interview_data["conducted_at"] = datetime.utcnow()
        self.exit_interview = interview_data
        self.updated_at = datetime.utcnow()
    
    def add_employee_feedback(self, feedback_data: Dict[str, Any]):
        """Add employee feedback"""
        feedback_data["submitted_at"] = datetime.utcnow()
        self.employee_feedback = feedback_data
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
    
    def issue_document(self, doc_type: str, file_url: str, file_name: str = None):
        """Issue document to employee"""
        document = {
            "type": doc_type,
            "file_url": file_url,
            "file_name": file_name or file_url.split('/')[-1],
            "issued_at": datetime.utcnow(),
            "status": "issued"
        }
        self.documents_issued.append(document)
        return document
    
    def get_document_by_type(self, doc_type: str, submitted: bool = True) -> Optional[Dict[str, Any]]:
        """Get document by type"""
        documents = self.documents_submitted if submitted else self.documents_issued
        for doc in documents:
            if doc["type"] == doc_type:
                return doc
        return None
    
    def has_all_required_documents(self) -> bool:
        """Check if all required documents are submitted"""
        for doc_type in self.documents_required:
            if not self.get_document_by_type(doc_type):
                return False
        return True
    
    def calculate_final_settlement(self, calculated_by: str) -> Dict[str, Any]:
        """Calculate final settlement"""
        # This would integrate with payroll system
        # For now, return placeholder calculation
        settlement = {
            "salary_dues": 0,
            "leave_encashment": 0,
            "gratuity": 0,
            "bonus": 0,
            "other_earnings": 0,
            "notice_period_recovery": 0,
            "other_deductions": 0,
            "total_earnings": 0,
            "total_deductions": 0,
            "net_settlement": 0,
            "status": "calculated"
        }
        
        self.final_settlement = settlement
        self.settlement_calculated_by = calculated_by
        self.settlement_calculated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        return settlement
    
    def process_final_settlement(self, processed_by: str, settlement_data: Dict[str, Any]):
        """Process final settlement"""
        if self.final_settlement:
            self.final_settlement.update(settlement_data)
            self.final_settlement["status"] = "processed"
            self.final_settlement["processed_at"] = datetime.utcnow()
        
        self.settlement_processed_by = processed_by
        self.settlement_processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_clearance_status(self, department: str, status: str, notes: Optional[str] = None):
        """Update clearance status for department"""
        clearance_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if notes:
            clearance_data["notes"] = notes
        
        if department == "hr":
            self.hr_clearance.update(clearance_data)
        elif department == "it":
            self.it_clearance.update(clearance_data)
        elif department == "finance":
            self.finance_clearance.update(clearance_data)
        elif department == "asset":
            self.asset_clearance.update(clearance_data)
        
        self.updated_at = datetime.utcnow()
    
    def get_clearance_status(self, department: str) -> Dict[str, Any]:
        """Get clearance status for department"""
        clearance_map = {
            "hr": self.hr_clearance,
            "it": self.it_clearance,
            "finance": self.finance_clearance,
            "asset": self.asset_clearance
        }
        
        return clearance_map.get(department, {})
    
    def is_all_clearances_completed(self) -> bool:
        """Check if all clearances are completed"""
        all_clearances = [self.hr_clearance, self.it_clearance, self.finance_clearance, self.asset_clearance]
        return all(clearance.get("status") == "completed" for clearance in all_clearances if clearance)
    
    def get_notice_period_remaining(self) -> int:
        """Get remaining notice period days"""
        return (self.last_working_day - date.today()).days
    
    def is_notice_period_completed(self) -> bool:
        """Check if notice period is completed"""
        return date.today() >= self.last_working_day
    
    def get_exit_duration(self) -> int:
        """Get exit process duration in days"""
        end_date = self.completion_date if self.completion_date else date.today()
        return (end_date - self.resignation_date).days
    
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
            "tasks_by_department": {
                department: len(self.get_tasks_by_department(department))
                for department in set(task.department for task in self.tasks if task.department)
            }
        }
    
    def get_clearance_summary(self) -> Dict[str, Any]:
        """Get clearance summary"""
        departments = ["hr", "it", "finance", "asset"]
        clearance_summary = {}
        
        for dept in departments:
            status = self.get_clearance_status(dept)
            clearance_summary[dept] = {
                "status": status.get("status", "pending"),
                "updated_at": status.get("updated_at"),
                "notes": status.get("notes")
            }
        
        clearance_summary["overall_completed"] = self.is_all_clearances_completed()
        clearance_summary["completed_count"] = sum(
            1 for dept in departments 
            if self.get_clearance_status(dept).get("status") == "completed"
        )
        
        return clearance_summary
    
    def get_exit_summary(self) -> Dict[str, Any]:
        """Get complete exit summary"""
        return {
            "employee_info": {
                "employee_code": self.employee_code,
                "employee_name": self.employee_name,
                "department": self.department,
                "designation": self.designation
            },
            "exit_details": {
                "exit_reason": self.exit_reason,
                "resignation_date": self.resignation_date,
                "last_working_day": self.last_working_day,
                "notice_period_days": self.notice_period_days,
                "notice_period_remaining": self.get_notice_period_remaining(),
                "is_notice_period_completed": self.is_notice_period_completed()
            },
            "status": {
                "status": self.status.value,
                "progress": self.progress,
                "exit_duration": self.get_exit_duration()
            },
            "assignment": {
                "assigned_to": self.assigned_to,
                "exit_interviewer": self.exit_interviewer
            },
            "tasks": self.get_task_statistics(),
            "clearance": self.get_clearance_summary(),
            "documents": {
                "required_documents": self.documents_required,
                "submitted_documents": len(self.documents_submitted),
                "issued_documents": len(self.documents_issued),
                "has_all_required_documents": self.has_all_required_documents()
            },
            "settlement": self.final_settlement,
            "interview": self.exit_interview,
            "feedback": self.employee_feedback
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed fields"""
        data = self.dict()
        data.update({
            "task_statistics": self.get_task_statistics(),
            "clearance_summary": self.get_clearance_summary(),
            "exit_summary": self.get_exit_summary(),
            "notice_period_remaining": self.get_notice_period_remaining(),
            "is_notice_period_completed": self.is_notice_period_completed(),
            "exit_duration": self.get_exit_duration(),
            "has_all_required_documents": self.has_all_required_documents(),
            "is_all_clearances_completed": self.is_all_clearances_completed()
        })
        return data
