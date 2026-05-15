from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

from models.onboarding_model import Onboarding, OnboardingTask, OnboardingStatus, TaskStatus, TaskPriority
from schemas.onboarding_schema import (
    OnboardingCreate, OnboardingUpdate, OnboardingSearch, OnboardingTaskCreate, OnboardingTaskUpdate
)
from repositories.onboarding_repo import OnboardingRepository
from utils.logger import audit_logger


class OnboardingService:
    """Service layer for onboarding operations"""
    
    def __init__(self):
        self.repository = OnboardingRepository()
    
    async def create_onboarding(self, onboarding_data: OnboardingCreate, created_by: str) -> Onboarding:
        """Create a new onboarding process"""
        # Validate input data
        await self._validate_onboarding_data(onboarding_data)
        
        try:
            onboarding = await self.repository.create_onboarding(onboarding_data, created_by)
            
            # Log the action
            audit_logger.log_user_action(
                created_by, "onboarding_created", str(onboarding.id),
                f"Created onboarding for employee {onboarding.employee_code}"
            )
            
            return onboarding
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create onboarding"
            )
    
    async def get_onboarding_by_id(self, onboarding_id: str) -> Onboarding:
        """Get onboarding by ID"""
        onboarding = await self.repository.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding not found"
            )
        return onboarding
    
    async def get_onboarding_by_employee(self, employee_id: str) -> Onboarding:
        """Get onboarding by employee ID"""
        onboarding = await self.repository.get_onboarding_by_employee(employee_id)
        if not onboarding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding not found for this employee"
            )
        return onboarding
    
    async def update_onboarding(
        self, 
        onboarding_id: str, 
        update_data: OnboardingUpdate, 
        modified_by: str = None
    ) -> Onboarding:
        """Update onboarding details"""
        # Validate the onboarding exists
        existing_onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        # Validate update data
        await self._validate_onboarding_update(update_data, existing_onboarding)
        
        try:
            updated_onboarding = await self.repository.update_onboarding(
                onboarding_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "onboarding_updated", onboarding_id,
                f"Updated onboarding for employee {updated_onboarding.employee_code}"
            )
            
            return updated_onboarding
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update onboarding"
            )
    
    async def delete_onboarding(self, onboarding_id: str, deleted_by: str) -> bool:
        """Delete onboarding process"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        try:
            success = await self.repository.delete_onboarding(onboarding_id)
            
            if success:
                # Log the action
                audit_logger.log_user_action(
                    deleted_by, "onboarding_deleted", onboarding_id,
                    f"Deleted onboarding for employee {onboarding.employee_code}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete onboarding"
            )
    
    async def get_onboardings_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[OnboardingSearch] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of onboardings"""
        try:
            onboardings, total = await self.repository.get_onboardings_list(
                page, page_size, search, department, status, assigned_to, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "onboardings": onboardings,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboardings"
            )
    
    async def add_task_to_onboarding(
        self, 
        onboarding_id: str, 
        task_data: OnboardingTaskCreate,
        created_by: str
    ) -> Onboarding:
        """Add a new task to onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        # Validate task data
        await self._validate_task_data(task_data)
        
        try:
            updated_onboarding = await self.repository.add_task_to_onboarding(
                onboarding_id, task_data
            )
            
            # Log the action
            audit_logger.log_user_action(
                created_by, "onboarding_task_added", onboarding_id,
                f"Added task '{task_data.title}' to onboarding for {updated_onboarding.employee_code}"
            )
            
            return updated_onboarding
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add task to onboarding"
            )
    
    async def complete_task(
        self, 
        onboarding_id: str, 
        task_id: str, 
        completed_by: str, 
        notes: Optional[str] = None
    ) -> Onboarding:
        """Mark a task as completed"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        try:
            updated_onboarding = await self.repository.complete_task(
                onboarding_id, task_id, completed_by, notes
            )
            
            # Log the action
            audit_logger.log_user_action(
                completed_by, "onboarding_task_completed", onboarding_id,
                f"Completed task {task_id} for onboarding of {updated_onboarding.employee_code}"
            )
            
            return updated_onboarding
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete task"
            )
    
    async def update_task_status(
        self, 
        onboarding_id: str, 
        task_id: str, 
        task_update: OnboardingTaskUpdate,
        modified_by: str
    ) -> Onboarding:
        """Update task status"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        # Validate status
        try:
            status = TaskStatus(task_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task status"
            )
        
        try:
            updated_onboarding = await self.repository.update_task_status(
                onboarding_id, task_id, status, task_update.notes
            )
            
            # Log the action
            audit_logger.log_user_action(
                modified_by, "onboarding_task_status_updated", onboarding_id,
                f"Updated task {task_id} status to {task_update.status} for {updated_onboarding.employee_code}"
            )
            
            return updated_onboarding
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task status"
            )
    
    async def get_overdue_tasks(self, onboarding_id: str) -> List[OnboardingTask]:
        """Get overdue tasks for an onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        return await self.repository.get_overdue_tasks(onboarding_id)
    
    async def get_overdue_onboardings(self) -> List[Onboarding]:
        """Get all overdue onboardings"""
        try:
            return await self.repository.get_overdue_onboardings()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch overdue onboardings"
            )
    
    async def get_onboarding_statistics(self) -> Dict[str, Any]:
        """Get onboarding statistics"""
        try:
            return await self.repository.get_onboarding_statistics()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboarding statistics"
            )
    
    async def get_onboardings_by_department(self, department: str) -> List[Onboarding]:
        """Get onboardings by department"""
        try:
            return await self.repository.get_onboardings_by_department(department)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboardings by department"
            )
    
    async def get_onboardings_by_assignee(self, assignee: str) -> List[Onboarding]:
        """Get onboardings assigned to a person"""
        try:
            return await self.repository.get_onboardings_by_assignee(assignee)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboardings by assignee"
            )
    
    async def get_onboardings_starting_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings starting soon"""
        try:
            return await self.repository.get_onboardings_starting_soon(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch upcoming onboardings"
            )
    
    async def get_onboardings_completing_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings completing soon"""
        try:
            return await self.repository.get_onboardings_completing_soon(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboardings completing soon"
            )
    
    async def get_onboarding_templates(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get onboarding templates"""
        try:
            return await self.repository.get_onboarding_templates(department)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch onboarding templates"
            )
    
    async def create_onboarding_from_template(
        self, 
        template_name: str, 
        employee_id: str,
        created_by: str
    ) -> Optional[Onboarding]:
        """Create onboarding from template"""
        try:
            onboarding = await self.repository.create_onboarding_from_template(
                template_name, employee_id, created_by
            )
            
            if onboarding:
                # Log the action
                audit_logger.log_user_action(
                    created_by, "onboarding_created_from_template", str(onboarding.id),
                    f"Created onboarding from template '{template_name}' for {onboarding.employee_code}"
                )
            
            return onboarding
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create onboarding from template"
            )
    
    async def submit_feedback(
        self, 
        onboarding_id: str, 
        feedback_data: Dict[str, Any],
        submitted_by: str
    ) -> Onboarding:
        """Submit onboarding feedback"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        
        # Validate feedback
        if not all(1 <= rating <= 5 for rating in [
            feedback_data.get("rating", 5), 
            feedback_data.get("process_rating", 5), 
            feedback_data.get("support_rating", 5)
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ratings must be between 1 and 5"
            )
        
        try:
            # Add feedback to onboarding
            feedback_data["submitted_by"] = submitted_by
            feedback_data["submitted_at"] = datetime.utcnow()
            
            if not onboarding.employee_feedback:
                onboarding.employee_feedback = []
            
            onboarding.employee_feedback.append(feedback_data)
            await onboarding.save()
            
            # Log the action
            audit_logger.log_user_action(
                submitted_by, "onboarding_feedback_submitted", onboarding_id,
                f"Submitted feedback for onboarding of {onboarding.employee_code}"
            )
            
            return onboarding
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit feedback"
            )
    
    async def _validate_onboarding_data(self, onboarding_data: OnboardingCreate):
        """Validate onboarding creation data"""
        # Date validation
        if onboarding_data.start_date > date.today():
            raise ValueError("Start date cannot be in the future")
        
        if onboarding_data.expected_completion_date <= onboarding_data.start_date:
            raise ValueError("Expected completion date must be after start date")
        
        # Validate tasks if provided
        for task in onboarding_data.tasks:
            await self._validate_task_data(task)
    
    async def _validate_onboarding_update(self, update_data: OnboardingUpdate, existing_onboarding: Onboarding):
        """Validate onboarding update data"""
        # Date validation
        if update_data.expected_completion_date:
            if update_data.expected_completion_date <= existing_onboarding.start_date:
                raise ValueError("Expected completion date must be after start date")
    
    async def _validate_task_data(self, task_data: OnboardingTaskCreate):
        """Validate task data"""
        if not task_data.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if task_data.due_date and task_data.due_date < date.today():
            raise ValueError("Task due date cannot be in the past")
        
        # Validate priority
        valid_priorities = [p.value for p in TaskPriority]
        if task_data.priority not in valid_priorities:
            raise ValueError(f"Invalid priority. Valid priorities: {valid_priorities}")
