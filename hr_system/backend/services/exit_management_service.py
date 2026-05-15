from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status
from decimal import Decimal

from models.exit_management_model import ExitManagement, ExitTask, ExitStatus, TaskStatus, TaskPriority
from schemas.exit_management_schema import (
    ExitManagementCreate, ExitManagementUpdate, ExitSearch, ExitTaskCreate, ExitTaskUpdate
)
from repositories.exit_management_repo import ExitManagementRepository
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
            audit_logger.log_user_action(
                created_by, "exit_management_created", str(exit_management.id),
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
                detail="Failed to create exit management"
            )
    
    async def get_exit_management_by_id(self, exit_id: str) -> ExitManagement:
        """Get exit management by ID"""
        exit_management = await self.repository.get_exit_management_by_id(exit_id)
        if not exit_management:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exit process not found"
            )
        return exit_management
    
    async def get_exit_management_by_employee(self, employee_id: str) -> ExitManagement:
        """Get exit management by employee ID"""
        exit_management = await self.repository.get_exit_management_by_employee(employee_id)
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
        # Validate the exit process exists
        existing_exit = await self.get_exit_management_by_id(exit_id)
        
        # Validate update data
        await self._validate_exit_update(update_data, existing_exit)
        
        try:
            updated_exit = await self.repository.update_exit_management(
                exit_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "exit_management_updated", exit_id,
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
                detail="Failed to update exit management"
            )
    
    async def delete_exit_management(self, exit_id: str, deleted_by: str) -> bool:
        """Delete exit management process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        try:
            success = await self.repository.delete_exit_management(exit_id)
            
            if success:
                # Log the action
                audit_logger.log_user_action(
                    deleted_by, "exit_management_deleted", exit_id,
                    f"Deleted exit process for employee {exit_management.employee_code}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete exit management"
            )
    
    async def get_exits_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[ExitSearch] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        exit_reason: Optional[str] = None,
        assigned_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of exit processes"""
        try:
            exits, total = await self.repository.get_exits_list(
                page, page_size, search, department, status, exit_reason, assigned_to, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "exit_processes": exits,
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
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        # Validate task data
        await self._validate_task_data(task_data)
        
        try:
            updated_exit = await self.repository.add_task_to_exit(exit_id, task_data)
            
            # Log the action
            audit_logger.log_user_action(
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
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        try:
            updated_exit = await self.repository.complete_task(
                exit_id, task_id, completed_by, notes
            )
            
            # Log the action
            audit_logger.log_user_action(
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
        exit_management = await self.get_exit_management_by_id(exit_id)
        
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
            audit_logger.log_user_action(
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
        exit_management = await self.get_exit_management_by_id(exit_id)
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
                detail="Failed to fetch exits by department"
            )
    
    async def get_exits_by_assignee(self, assignee: str) -> List[ExitManagement]:
        """Get exit processes assigned to a person"""
        try:
            return await self.repository.get_exits_by_assignee(assignee)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exits by assignee"
            )
    
    async def complete_exit(self, exit_id: str, completion_date: date, completed_by: str) -> ExitManagement:
        """Complete the exit process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        # Validate completion date
        if completion_date < exit_management.last_working_day:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completion date cannot be before last working day"
            )
        
        try:
            updated_exit = await self.repository.complete_exit(exit_id, completion_date, completed_by)
            
            # Log the action
            audit_logger.log_user_action(
                completed_by, "exit_process_completed", exit_id,
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
        interview_data: Dict[str, Any],
        conducted_by: str
    ) -> ExitManagement:
        """Conduct exit interview"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        # Validate interview data
        if not interview_data.get("interviewer"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interviewer is required"
            )
        
        if not interview_data.get("feedback"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview feedback is required"
            )
        
        try:
            # Add interview data to exit management
            interview_data["conducted_by"] = conducted_by
            interview_data["conducted_at"] = datetime.utcnow()
            
            exit_management.exit_interview = interview_data
            await exit_management.save()
            
            # Log the action
            audit_logger.log_user_action(
                conducted_by, "exit_interview_conducted", exit_id,
                f"Conducted exit interview for {exit_management.employee_code}"
            )
            
            return exit_management
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to conduct exit interview"
            )
    
    async def calculate_final_settlement(self, exit_id: str, calculated_by: str) -> ExitManagement:
        """Calculate final settlement"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        try:
            # Calculate settlement components
            settlement = await self._calculate_settlement_components(exit_management)
            
            exit_management.final_settlement = settlement
            exit_management.settlement_calculated_by = calculated_by
            exit_management.settlement_calculated_at = datetime.utcnow()
            
            await exit_management.save()
            
            # Log the action
            audit_logger.log_user_action(
                calculated_by, "final_settlement_calculated", exit_id,
                f"Calculated final settlement for {exit_management.employee_code}"
            )
            
            return exit_management
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate final settlement"
            )
    
    async def process_final_settlement(
        self, 
        exit_id: str, 
        settlement_data: Dict[str, Any],
        processed_by: str
    ) -> ExitManagement:
        """Process final settlement"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        try:
            # Update settlement with processed data
            settlement_data["processed_by"] = processed_by
            settlement_data["processed_at"] = datetime.utcnow()
            settlement_data["status"] = "processed"
            
            exit_management.final_settlement.update(settlement_data)
            await exit_management.save()
            
            # Log the action
            audit_logger.log_user_action(
                processed_by, "final_settlement_processed", exit_id,
                f"Processed final settlement for {exit_management.employee_code}"
            )
            
            return exit_management
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process final settlement"
            )
    
    async def submit_exit_feedback(
        self, 
        exit_id: str, 
        feedback_data: Dict[str, Any],
        submitted_by: str
    ) -> ExitManagement:
        """Submit exit feedback"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        # Validate feedback
        if not feedback_data.get("overall_experience"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Overall experience rating is required"
            )
        
        try:
            # Add feedback to exit management
            feedback_data["submitted_by"] = submitted_by
            feedback_data["submitted_at"] = datetime.utcnow()
            
            if not exit_management.employee_feedback:
                exit_management.employee_feedback = []
            
            exit_management.employee_feedback.append(feedback_data)
            await exit_management.save()
            
            # Log the action
            audit_logger.log_user_action(
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
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        clearance_status = {
            "hr_clearance": self._get_department_clearance_status(exit_management, "hr"),
            "it_clearance": self._get_department_clearance_status(exit_management, "it"),
            "finance_clearance": self._get_department_clearance_status(exit_management, "finance"),
            "admin_clearance": self._get_department_clearance_status(exit_management, "admin"),
            "overall_status": "completed" if all([
                self._get_department_clearance_status(exit_management, dept)["status"] == "completed"
                for dept in ["hr", "it", "finance", "admin"]
            ]) else "pending"
        }
        
        return clearance_status
    
    async def get_exit_summary(self, exit_id: str) -> Dict[str, Any]:
        """Get exit process summary"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        summary = {
            "employee_code": exit_management.employee_code,
            "employee_name": exit_management.employee_name,
            "department": exit_management.department,
            "exit_reason": exit_management.exit_reason,
            "resignation_date": exit_management.resignation_date,
            "last_working_day": exit_management.last_working_day,
            "status": exit_management.status.value,
            "progress": exit_management.calculate_progress(),
            "total_tasks": len(exit_management.tasks),
            "completed_tasks": len([t for t in exit_management.tasks if t.status == TaskStatus.COMPLETED]),
            "overdue_tasks": len([t for t in exit_management.tasks if t.is_overdue()]),
            "clearance_status": await self.get_clearance_status(exit_id),
            "final_settlement": exit_management.final_settlement,
            "exit_interview": exit_management.exit_interview,
            "employee_feedback": exit_management.employee_feedback
        }
        
        return summary
    
    async def get_exits_completing_soon(self, days: int = 7) -> List[ExitManagement]:
        """Get exit processes completing soon"""
        try:
            return await self.repository.get_exits_completing_soon(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exits completing soon"
            )
    
    async def issue_documents(self, exit_id: str, document_types: List[str], issued_by: str) -> ExitManagement:
        """Issue exit documents"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        
        # Validate document types
        valid_documents = ["experience_letter", "relieving_letter", "salary_certificate"]
        for doc_type in document_types:
            if doc_type not in valid_documents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document type: {doc_type}"
                )
        
        try:
            # Add documents to exit management
            documents = []
            for doc_type in document_types:
                documents.append({
                    "type": doc_type,
                    "issued_by": issued_by,
                    "issued_at": datetime.utcnow(),
                    "status": "issued"
                })
            
            exit_management.documents_issued.extend(documents)
            await exit_management.save()
            
            # Log the action
            audit_logger.log_user_action(
                issued_by, "exit_documents_issued", exit_id,
                f"Issued documents {document_types} for {exit_management.employee_code}"
            )
            
            return exit_management
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to issue documents"
            )
    
    async def get_compliance_report(self, payroll_month: str) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            return await self.repository.get_compliance_report(payroll_month)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate compliance report"
            )
    
    async def _validate_exit_data(self, exit_data: ExitManagementCreate):
        """Validate exit creation data"""
        # Date validation
        if exit_data.resignation_date > date.today():
            raise ValueError("Resignation date cannot be in the future")
        
        if exit_data.last_working_day <= exit_data.resignation_date:
            raise ValueError("Last working day must be after resignation date")
        
        # Validate tasks if provided
        for task in exit_data.tasks:
            await self._validate_task_data(task)
    
    async def _validate_exit_update(self, update_data: ExitManagementUpdate, existing_exit: ExitManagement):
        """Validate exit update data"""
        # Date validation
        if update_data.last_working_day:
            if update_data.last_working_day <= existing_exit.resignation_date:
                raise ValueError("Last working day must be after resignation date")
    
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
    
    async def _calculate_settlement_components(self, exit_management: ExitManagement) -> Dict[str, Any]:
        """Calculate settlement components"""
        # This would integrate with payroll system
        # For now, return placeholder data
        return {
            "salary_dues": 0,
            "leave_encashment": 0,
            "gratuity": 0,
            "bonus": 0,
            "other_earnings": 0,
            "notice_period_recovery": 0,
            "other_deductions": 0,
            "total_earnings": 0,
            "total_deductions": 0,
            "net_settlement": 0
        }
    
    def _get_department_clearance_status(self, exit_management: ExitManagement, department: str) -> Dict[str, Any]:
        """Get clearance status for a specific department"""
        # Find tasks related to the department
        dept_tasks = [t for t in exit_management.tasks if department.lower() in t.title.lower()]
        
        if not dept_tasks:
            return {"status": "not_applicable", "completed_tasks": 0, "total_tasks": 0}
        
        completed_tasks = len([t for t in dept_tasks if t.status == TaskStatus.COMPLETED])
        
        return {
            "status": "completed" if completed_tasks == len(dept_tasks) else "pending",
            "completed_tasks": completed_tasks,
            "total_tasks": len(dept_tasks),
            "progress": (completed_tasks / len(dept_tasks)) * 100
        }
