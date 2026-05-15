from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

from .model import ExitManagement, ExitTask, ExitStatus, ExitReason, TaskStatus, TaskPriority
from .schema import (
    ExitManagementCreate, ExitManagementUpdate, ExitSearch, ExitTaskCreate,
    ExitTaskUpdate, ExitBlocker, ExitFeedback, ExitInterview, ExitAsset, ExitSettlement
)
from .repository import ExitManagementRepository
from utils.logger import audit_logger


class ExitManagementService:
    """Service layer for exit management operations"""
    
    def __init__(self):
        self.repository = ExitManagementRepository()
    
    async def create_exit_management(self, exit_data: ExitManagementCreate, created_by: str) -> ExitManagement:
        """Create a new exit management process"""
        # Validate input data
        await self._validate_exit_data(exit_data)
        
        try:
            exit_management = await self.repository.create_exit_management(exit_data, created_by)
            
            # Log the action
            audit_logger.log_employee_action(
                created_by, "exit_created", str(exit_management.id),
                f"Created exit process for employee {exit_management.employee_code}"
            )
            
            return exit_management
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create exit process"
            )
    
    async def get_exit_management(self, exit_id: str) -> ExitManagement:
        """Get exit management by ID"""
        exit_management = await self.repository.get_exit_by_id(exit_id)
        if not exit_management:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exit process not found"
            )
        return exit_management
    
    async def get_exit_by_employee(self, employee_id: str) -> ExitManagement:
        """Get exit management by employee ID"""
        exit_management = await self.repository.get_exit_by_employee(employee_id)
        if not exit_management:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exit process not found for this employee"
            )
        return exit_management
    
    async def update_exit_management(
        self, 
        exit_id: str, 
        update_data: ExitManagementUpdate, 
        modified_by: str = None
    ) -> ExitManagement:
        """Update exit management details"""
        # Validate the exit exists
        existing_exit = await self.get_exit_management(exit_id)
        
        # Validate update data
        await self._validate_exit_update(update_data, existing_exit)
        
        try:
            updated_exit = await self.repository.update_exit_management(
                exit_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                modified_by or "system", "exit_updated", exit_id,
                f"Updated exit process for employee {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update exit process"
            )
    
    async def delete_exit_management(self, exit_id: str, deleted_by: str) -> bool:
        """Delete exit management process"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            success = await self.repository.delete_exit_management(exit_id)
            
            if success:
                # Log the action
                audit_logger.log_employee_action(
                    deleted_by, "exit_deleted", exit_id,
                    f"Deleted exit process for employee {exit_management.employee_code}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete exit process"
            )
    
    async def get_exits_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[ExitSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of exit processes"""
        try:
            exits, total = await self.repository.get_exits_list(
                page, page_size, search, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "exits": exits,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exit processes"
            )
    
    async def add_task_to_exit(
        self, 
        exit_id: str, 
        task_data: ExitTaskCreate,
        created_by: str
    ) -> ExitManagement:
        """Add a new task to exit process"""
        exit_management = await self.get_exit_management(exit_id)
        
        # Validate task data
        await self._validate_task_data(task_data)
        
        try:
            updated_exit = await self.repository.add_task_to_exit(
                exit_id, task_data
            )
            
            # Log the action
            audit_logger.log_employee_action(
                created_by, "exit_task_added", exit_id,
                f"Added task '{task_data.title}' to exit process for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add task to exit process"
            )
    
    async def complete_task(
        self, 
        exit_id: str, 
        task_id: str, 
        completed_by: str, 
        notes: Optional[str] = None
    ) -> ExitManagement:
        """Mark a task as completed"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.complete_task(
                exit_id, task_id, completed_by, notes
            )
            
            # Log the action
            audit_logger.log_employee_action(
                completed_by, "exit_task_completed", exit_id,
                f"Completed task {task_id} for exit process of {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete task"
            )
    
    async def update_task_status(
        self, 
        exit_id: str, 
        task_id: str, 
        task_update: ExitTaskUpdate,
        modified_by: str
    ) -> ExitManagement:
        """Update task status"""
        exit_management = await self.get_exit_management(exit_id)
        
        # Validate status
        try:
            status = TaskStatus(task_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task status"
            )
        
        try:
            updated_exit = await self.repository.update_task_status(
                exit_id, task_id, status, task_update.notes
            )
            
            # Log the action
            audit_logger.log_employee_action(
                modified_by, "exit_task_status_updated", exit_id,
                f"Updated task {task_id} status to {task_update.status} for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task status"
            )
    
    async def get_overdue_tasks(self, exit_id: str) -> List[ExitTask]:
        """Get overdue tasks for an exit process"""
        exit_management = await self.get_exit_management(exit_id)
        return await self.repository.get_overdue_tasks(exit_id)
    
    async def get_exit_statistics(self) -> Dict[str, Any]:
        """Get exit management statistics"""
        try:
            return await self.repository.get_exit_statistics()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exit statistics"
            )
    
    async def get_exits_by_department(self, department: str) -> List[ExitManagement]:
        """Get exit processes by department"""
        try:
            return await self.repository.get_exits_by_department(department)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exit processes by department"
            )
    
    async def get_exits_by_assignee(self, assignee: str) -> List[ExitManagement]:
        """Get exit processes assigned to a person"""
        try:
            return await self.repository.get_exits_by_assignee(assignee)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exit processes by assignee"
            )
    
    async def add_blocker(
        self, 
        exit_id: str, 
        blocker_data: ExitBlocker,
        created_by: str
    ) -> ExitManagement:
        """Add a blocker to exit process"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.add_blocker(
                exit_id, blocker_data.blocker_description, blocker_data.severity
            )
            
            # Log the action
            audit_logger.log_employee_action(
                created_by, "exit_blocker_added", exit_id,
                f"Added blocker to exit process for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add blocker"
            )
    
    async def resolve_blocker(
        self, 
        exit_id: str, 
        blocker_index: int, 
        resolution_notes: str,
        resolved_by: str
    ) -> ExitManagement:
        """Resolve a blocker"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.resolve_blocker(
                exit_id, blocker_index, resolution_notes
            )
            
            # Log the action
            audit_logger.log_employee_action(
                resolved_by, "exit_blocker_resolved", exit_id,
                f"Resolved blocker #{blocker_index} for exit process of {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resolve blocker"
            )
    
    async def complete_exit(self, exit_id: str, completion_date: date, completed_by: str) -> ExitManagement:
        """Complete the exit process"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.complete_exit(exit_id, completion_date)
            
            # Log the action
            audit_logger.log_employee_action(
                completed_by, "exit_completed", exit_id,
                f"Completed exit process for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete exit process"
            )
    
    async def conduct_exit_interview(
        self, 
        exit_id: str, 
        interview_data: ExitInterview,
        interviewer: str
    ) -> ExitManagement:
        """Conduct exit interview"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            # Update exit management with interview details
            update_data = ExitManagementUpdate(
                exit_interview_scheduled=True,
                exit_interview_date=interview_data.interview_date,
                exit_interview_conducted=True,
                exit_interviewer=interview_data.interviewer,
                exit_interview_notes=str(interview_data.questions),
                exit_interview_feedback=interview_data.feedback
            )
            
            updated_exit = await self.repository.update_exit_management(
                exit_id, update_data, interviewer
            )
            
            # Log the action
            audit_logger.log_employee_action(
                interviewer, "exit_interview_conducted", exit_id,
                f"Conducted exit interview for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to conduct exit interview"
            )
    
    async def add_asset_return(
        self, 
        exit_id: str, 
        asset_data: ExitAsset,
        processed_by: str
    ) -> ExitManagement:
        """Add asset return record"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.add_asset_return(
                exit_id, asset_data.asset_name, asset_data.asset_id, 
                asset_data.return_date, asset_data.condition
            )
            
            # Log the action
            audit_logger.log_employee_action(
                processed_by, "asset_returned", exit_id,
                f"Recorded asset return for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record asset return"
            )
    
    async def calculate_final_settlement(self, exit_id: str, calculated_by: str) -> ExitManagement:
        """Calculate final settlement"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            updated_exit = await self.repository.calculate_final_settlement(exit_id)
            
            # Log the action
            audit_logger.log_employee_action(
                calculated_by, "final_settlement_calculated", exit_id,
                f"Calculated final settlement for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate final settlement"
            )
    
    async def process_final_settlement(
        self, 
        exit_id: str, 
        settlement_data: ExitSettlement,
        processed_by: str
    ) -> ExitManagement:
        """Process final settlement"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            # Update exit management with settlement details
            update_data = ExitManagementUpdate(
                final_settlement_amount=settlement_data.settlement_amount,
                final_settlement_date=settlement_data.settlement_date,
                final_settlement_paid=True
            )
            
            updated_exit = await self.repository.update_exit_management(
                exit_id, update_data, processed_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                processed_by, "final_settlement_processed", exit_id,
                f"Processed final settlement for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process final settlement"
            )
    
    async def submit_exit_feedback(
        self, 
        exit_id: str, 
        feedback_data: ExitFeedback,
        submitted_by: str
    ) -> ExitManagement:
        """Submit exit feedback"""
        exit_management = await self.get_exit_management(exit_id)
        
        # Validate feedback
        if not all(1 <= rating <= 5 for rating in [
            feedback_data.overall_experience, feedback_data.management_support,
            feedback_data.work_environment, feedback_data.compensation, 
            feedback_data.growth_opportunities
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ratings must be between 1 and 5"
            )
        
        try:
            # Add feedback to exit management
            feedback_dict = feedback_data.dict()
            feedback_dict["submitted_by"] = submitted_by
            feedback_dict["submitted_at"] = datetime.utcnow()
            
            if not exit_management.employee_feedback:
                exit_management.employee_feedback = []
            
            exit_management.employee_feedback.append(feedback_dict)
            await exit_management.save()
            
            # Log the action
            audit_logger.log_employee_action(
                submitted_by, "exit_feedback_submitted", exit_id,
                f"Submitted exit feedback for {exit_management.employee_code}"
            )
            
            return exit_management
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit exit feedback"
            )
    
    async def get_clearance_status(self, exit_id: str) -> Dict[str, Any]:
        """Get clearance status for all departments"""
        exit_management = await self.get_exit_management(exit_id)
        return await self.repository.get_clearance_status(exit_id)
    
    async def get_exit_summary(self, exit_id: str) -> Dict[str, Any]:
        """Get exit process summary"""
        exit_management = await self.get_exit_management(exit_id)
        return await self.repository.get_exit_summary(exit_id)
    
    async def get_tasks_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a person"""
        try:
            return await self.repository.get_tasks_by_assignee(assignee)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tasks by assignee"
            )
    
    async def get_exits_completing_soon(self, days: int = 7) -> List[ExitManagement]:
        """Get exit processes completing soon"""
        try:
            return await self.repository.get_exits_completing_soon(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exits completing soon"
            )
    
    async def issue_documents(
        self, 
        exit_id: str, 
        document_types: List[str],
        issued_by: str
    ) -> ExitManagement:
        """Issue exit documents"""
        exit_management = await self.get_exit_management(exit_id)
        
        try:
            update_data = ExitManagementUpdate()
            
            for doc_type in document_types:
                if doc_type == "experience_letter":
                    update_data.experience_letter_issued = True
                elif doc_type == "relieving_letter":
                    update_data.relieving_letter_issued = True
            
            updated_exit = await self.repository.update_exit_management(
                exit_id, update_data, issued_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                issued_by, "documents_issued", exit_id,
                f"Issued documents {document_types} for {updated_exit.employee_code}"
            )
            
            return updated_exit
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to issue documents"
            )
    
    async def _validate_exit_data(self, exit_data: ExitManagementCreate):
        """Validate exit creation data"""
        # Date validation
        if exit_data.resignation_date > date.today():
            raise ValueError("Resignation date cannot be in the future")
        
        if exit_data.last_working_day <= exit_data.resignation_date:
            raise ValueError("Last working day must be after resignation date")
        
        # Validate exit reason
        try:
            ExitReason(exit_data.exit_reason)
        except ValueError:
            raise ValueError("Invalid exit reason")
        
        # Validate notice period
        if exit_data.notice_period_days < 0:
            raise ValueError("Notice period days cannot be negative")
        
        # Validate tasks if provided
        for task in exit_data.tasks:
            await self._validate_task_data(task)
    
    async def _validate_exit_update(self, update_data: ExitManagementUpdate, existing_exit: ExitManagement):
        """Validate exit update data"""
        # Date validation
        if update_data.actual_exit_date:
            if update_data.actual_exit_date < existing_exit.resignation_date:
                raise ValueError("Actual exit date cannot be before resignation date")
        
        if update_data.exit_interview_date:
            if update_data.exit_interview_date > existing_exit.last_working_day:
                raise ValueError("Exit interview date cannot be after last working day")
        
        # Validate status
        if update_data.status:
            try:
                ExitStatus(update_data.status)
            except ValueError:
                raise ValueError("Invalid exit status")
        
        # Validate notice period served
        if update_data.notice_period_served is not None:
            if update_data.notice_period_served < 0:
                raise ValueError("Notice period served cannot be negative")
            if update_data.notice_period_served > existing_exit.notice_period_days:
                raise ValueError("Notice period served cannot exceed total notice period")
    
    async def _validate_task_data(self, task_data: ExitTaskCreate):
        """Validate task data"""
        if not task_data.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if task_data.due_date and task_data.due_date < date.today():
            raise ValueError("Task due date cannot be in the past")
        
        # Validate priority
        valid_priorities = [p.value for p in TaskPriority]
        if task_data.priority not in valid_priorities:
            raise ValueError(f"Invalid priority. Valid priorities: {valid_priorities}")
