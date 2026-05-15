from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from models.onboarding_model import Onboarding, OnboardingTask, OnboardingStatus, TaskStatus, TaskPriority
from utils.helpers import create_pagination_params


class OnboardingRepository:
    """Repository for onboarding operations"""
    
    async def create_onboarding(self, onboarding_data, created_by: str = None) -> Onboarding:
        """Create a new onboarding process"""
        onboarding = Onboarding(**onboarding_data.dict())
        if created_by:
            onboarding.created_by = created_by
        await onboarding.insert()
        return onboarding
    
    async def get_onboarding_by_id(self, onboarding_id: str) -> Optional[Onboarding]:
        """Get onboarding by ID"""
        try:
            return await Onboarding.get(PydanticObjectId(onboarding_id))
        except:
            return None
    
    async def get_onboarding_by_employee(self, employee_id: str) -> Optional[Onboarding]:
        """Get onboarding by employee ID"""
        return await Onboarding.find_one({"employee_id": employee_id})
    
    async def update_onboarding(self, onboarding_id: str, update_data, modified_by: str = None) -> Optional[Onboarding]:
        """Update onboarding details"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if modified_by:
            update_dict["last_modified_by"] = modified_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            if hasattr(onboarding, field):
                setattr(onboarding, field, value)
        
        await onboarding.save()
        return onboarding
    
    async def delete_onboarding(self, onboarding_id: str) -> bool:
        """Delete onboarding process"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return False
        
        await onboarding.delete()
        return True
    
    async def get_onboardings_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[dict] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Onboarding], int]:
        """Get list of onboardings with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            if search.get("query"):
                query["$or"] = [
                    {"employee_code": {"$regex": search["query"], "$options": "i"}},
                    {"employee_name": {"$regex": search["query"], "$options": "i"}},
                    {"department": {"$regex": search["query"], "$options": "i"}}
                ]
        
        if department:
            query["department"] = department
        
        if status:
            try:
                query["status"] = OnboardingStatus(status)
            except ValueError:
                pass
        
        if assigned_to:
            query["assigned_to"] = assigned_to
        
        # Get total count
        total = await Onboarding.find(query).count()
        
        # Get onboardings with pagination and sorting
        onboardings = await Onboarding.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return onboardings, total
    
    async def add_task_to_onboarding(self, onboarding_id: str, task_data) -> Optional[Onboarding]:
        """Add a new task to onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        # Create new task
        task = OnboardingTask(**task_data.dict())
        task.created_at = datetime.utcnow()
        
        onboarding.tasks.append(task)
        await onboarding.save()
        
        return onboarding
    
    async def complete_task(self, onboarding_id: str, task_id: str, completed_by: str, notes: Optional[str] = None) -> Optional[Onboarding]:
        """Mark a task as completed"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        # Find and update the task
        for task in onboarding.tasks:
            if str(task.id) == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.completed_by = completed_by
                if notes:
                    task.notes = notes
                break
        
        await onboarding.save()
        return onboarding
    
    async def update_task_status(self, onboarding_id: str, task_id: str, status: TaskStatus, notes: Optional[str] = None) -> Optional[Onboarding]:
        """Update task status"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        # Find and update the task
        for task in onboarding.tasks:
            if str(task.id) == task_id:
                task.status = status
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                if notes:
                    task.notes = notes
                break
        
        await onboarding.save()
        return onboarding
    
    async def get_overdue_tasks(self, onboarding_id: str) -> List[OnboardingTask]:
        """Get overdue tasks for an onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return []
        
        overdue_tasks = []
        for task in onboarding.tasks:
            if task.is_overdue():
                overdue_tasks.append(task)
        
        return overdue_tasks
    
    async def get_overdue_onboardings(self) -> List[Onboarding]:
        """Get all overdue onboardings"""
        today = date.today()
        
        return await Onboarding.find({
            "status": {"$ne": OnboardingStatus.COMPLETED},
            "expected_completion_date": {"$lt": today}
        }).sort(Onboarding.expected_completion_date, ASCENDING).to_list()
    
    async def get_onboarding_statistics(self) -> dict:
        """Get onboarding statistics"""
        total_onboardings = await Onboarding.count()
        
        # Status breakdown
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = await Onboarding.aggregate(status_pipeline).to_list()
        
        # Department breakdown
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        dept_stats = await Onboarding.aggregate(dept_pipeline).to_list()
        
        # Recent onboardings (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_onboardings = await Onboarding.find({
            "created_at": {"$gte": thirty_days_ago}
        }).count()
        
        # Overdue onboardings
        today = date.today()
        overdue_count = await Onboarding.find({
            "status": {"$ne": OnboardingStatus.COMPLETED},
            "expected_completion_date": {"$lt": today}
        }).count()
        
        # Average completion time
        completed_onboardings = await Onboarding.find({
            "status": OnboardingStatus.COMPLETED,
            "completed_at": {"$ne": None}
        }).to_list()
        
        avg_completion_days = 0
        if completed_onboardings:
            total_days = 0
            for onboarding in completed_onboardings:
                if onboarding.completed_at and onboarding.start_date:
                    days = (onboarding.completed_at.date() - onboarding.start_date).days
                    total_days += days
            
            avg_completion_days = total_days / len(completed_onboardings)
        
        return {
            "total_onboardings": total_onboardings,
            "status_breakdown": status_stats,
            "department_breakdown": dept_stats,
            "recent_onboardings": recent_onboardings,
            "overdue_onboardings": overdue_count,
            "average_completion_days": round(avg_completion_days, 2)
        }
    
    async def get_onboardings_by_department(self, department: str) -> List[Onboarding]:
        """Get onboardings by department"""
        return await Onboarding.find(
            {"department": department}
        ).sort(Onboarding.created_at, DESCENDING).to_list()
    
    async def get_onboardings_by_assignee(self, assignee: str) -> List[Onboarding]:
        """Get onboardings assigned to a person"""
        return await Onboarding.find(
            {"assigned_to": assignee}
        ).sort(Onboarding.created_at, DESCENDING).to_list()
    
    async def get_onboardings_starting_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings starting in the next N days"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return await Onboarding.find({
            "status": OnboardingStatus.PENDING,
            "start_date": {"$gte": today, "$lte": end_date}
        }).sort(Onboarding.start_date, ASCENDING).to_list()
    
    async def get_onboardings_completing_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings completing in the next N days"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return await Onboarding.find({
            "status": {"$ne": OnboardingStatus.COMPLETED},
            "expected_completion_date": {"$gte": today, "$lte": end_date}
        }).sort(Onboarding.expected_completion_date, ASCENDING).to_list()
    
    async def get_onboarding_templates(self, department: Optional[str] = None) -> List[dict]:
        """Get onboarding templates"""
        # This would integrate with a template collection
        # For now, return placeholder templates
        templates = [
            {
                "name": "Standard Onboarding",
                "department": "All",
                "tasks": [
                    {
                        "title": "Documentation Submission",
                        "description": "Submit required documents",
                        "priority": "high",
                        "category": "documentation",
                        "estimated_duration_days": 1
                    },
                    {
                        "title": "IT Setup",
                        "description": "Setup computer and accounts",
                        "priority": "high",
                        "category": "it",
                        "estimated_duration_days": 2
                    },
                    {
                        "title": "HR Briefing",
                        "description": "Company policies and benefits overview",
                        "priority": "medium",
                        "category": "hr",
                        "estimated_duration_days": 1
                    },
                    {
                        "title": "Team Introduction",
                        "description": "Meet with team members",
                        "priority": "medium",
                        "category": "team",
                        "estimated_duration_days": 1
                    }
                ]
            },
            {
                "name": "Technical Role Onboarding",
                "department": "Engineering",
                "tasks": [
                    {
                        "title": "Development Environment Setup",
                        "description": "Setup development tools and access",
                        "priority": "high",
                        "category": "technical",
                        "estimated_duration_days": 2
                    },
                    {
                        "title": "Code Repository Access",
                        "description": "Setup Git and repository access",
                        "priority": "high",
                        "category": "technical",
                        "estimated_duration_days": 1
                    },
                    {
                        "title": "Technical Training",
                        "description": "Complete technical training modules",
                        "priority": "medium",
                        "category": "training",
                        "estimated_duration_days": 3
                    }
                ]
            },
            {
                "name": "Sales Role Onboarding",
                "department": "Sales",
                "tasks": [
                    {
                        "title": "CRM Training",
                        "description": "Learn CRM system",
                        "priority": "high",
                        "category": "training",
                        "estimated_duration_days": 2
                    },
                    {
                        "title": "Product Knowledge",
                        "description": "Complete product training",
                        "priority": "high",
                        "category": "training",
                        "estimated_duration_days": 3
                    },
                    {
                        "title": "Sales Process Training",
                        "description": "Learn company sales process",
                        "priority": "medium",
                        "category": "training",
                        "estimated_duration_days": 2
                    }
                ]
            }
        ]
        
        if department:
            return [t for t in templates if t["department"] == department or t["department"] == "All"]
        
        return templates
    
    async def create_onboarding_from_template(self, template_name: str, employee_id: str, created_by: str) -> Optional[Onboarding]:
        """Create onboarding from template"""
        templates = await self.get_onboarding_templates()
        
        # Find the template
        template = None
        for t in templates:
            if t["name"] == template_name:
                template = t
                break
        
        if not template:
            return None
        
        # Get employee details (this would integrate with employee repository)
        # For now, use placeholder data
        from models.employee_model import Employee, Department
        employee = await Employee.get(employee_id)
        if not employee:
            return None
        
        # Create onboarding with template tasks
        onboarding_data = {
            "employee_id": employee_id,
            "employee_code": employee.employee_code,
            "employee_name": employee.full_name,
            "department": employee.department.value,
            "start_date": date.today(),
            "expected_completion_date": date.today() + timedelta(days=30),
            "assigned_to": "hr_manager",
            "tasks": template["tasks"]
        }
        
        onboarding = await self.create_onboarding(onboarding_data, created_by)
        return onboarding
