from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from .model import Onboarding, OnboardingTask, OnboardingStatus, TaskStatus, TaskPriority
from .schema import OnboardingCreate, OnboardingUpdate, OnboardingSearch, OnboardingTaskCreate
from utils.helpers import create_pagination_params


class OnboardingRepository:
    """Repository for onboarding operations"""
    
    async def create_onboarding(self, onboarding_data: OnboardingCreate, created_by: str) -> Onboarding:
        """Create a new onboarding process"""
        # Create onboarding document
        onboarding = Onboarding(
            **onboarding_data.dict(exclude={"tasks"}),
            created_by=created_by
        )
        
        # Add initial tasks if provided
        if onboarding_data.tasks:
            for task_data in onboarding_data.tasks:
                task = OnboardingTask(**task_data.dict())
                onboarding.tasks.append(task)
        
        # Calculate initial progress
        await onboarding.calculate_progress()
        
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
        return await Onboarding.find_one(Onboarding.employee_id == employee_id)
    
    async def update_onboarding(
        self, 
        onboarding_id: str, 
        update_data: OnboardingUpdate, 
        modified_by: str = None
    ) -> Optional[Onboarding]:
        """Update onboarding details"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(onboarding, field, value)
        
        onboarding.updated_at = datetime.utcnow()
        
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
        search: Optional[OnboardingSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Onboarding], int]:
        """Get list of onboardings with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            if search.query:
                query["$or"] = [
                    {"employee_name": {"$regex": search.query, "$options": "i"}},
                    {"employee_code": {"$regex": search.query, "$options": "i"}},
                    {"department": {"$regex": search.query, "$options": "i"}}
                ]
            
            if search.department:
                query["department"] = search.department
            
            if search.status:
                query["status"] = search.status
            
            if search.assigned_to:
                query["assigned_to"] = search.assigned_to
            
            if search.start_date_from:
                if "start_date" in query:
                    query["start_date"]["$gte"] = search.start_date_from
                else:
                    query["start_date"] = {"$gte": search.start_date_from}
            
            if search.start_date_to:
                if "start_date" in query:
                    query["start_date"]["$lte"] = search.start_date_to
                else:
                    query["start_date"] = {"$lte": search.start_date_to}
            
            if search.completion_date_from:
                if "actual_completion_date" in query:
                    query["actual_completion_date"]["$gte"] = search.completion_date_from
                else:
                    query["actual_completion_date"] = {"$gte": search.completion_date_from}
            
            if search.completion_date_to:
                if "actual_completion_date" in query:
                    query["actual_completion_date"]["$lte"] = search.completion_date_to
                else:
                    query["actual_completion_date"] = {"$lte": search.completion_date_to}
            
            if search.overdue_only:
                today = date.today()
                query["expected_completion_date"] = {"$lt": today}
                query["status"] = {"$ne": OnboardingStatus.COMPLETED}
        
        # Get total count
        total = await Onboarding.find(query).count()
        
        # Get onboardings with pagination and sorting
        onboardings = await Onboarding.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return onboardings, total
    
    async def add_task_to_onboarding(
        self, 
        onboarding_id: str, 
        task_data: OnboardingTaskCreate
    ) -> Optional[Onboarding]:
        """Add a new task to onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        await onboarding.add_task(task_data.dict())
        return onboarding
    
    async def complete_task(
        self, 
        onboarding_id: str, 
        task_id: str, 
        completed_by: str, 
        notes: Optional[str] = None
    ) -> Optional[Onboarding]:
        """Mark a task as completed"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        await onboarding.complete_task(task_id, completed_by, notes)
        return onboarding
    
    async def update_task_status(
        self, 
        onboarding_id: str, 
        task_id: str, 
        status: TaskStatus, 
        notes: Optional[str] = None
    ) -> Optional[Onboarding]:
        """Update task status"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        await onboarding.update_task_status(task_id, status, notes)
        return onboarding
    
    async def get_overdue_tasks(self, onboarding_id: str) -> List[OnboardingTask]:
        """Get overdue tasks for an onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return []
        
        return onboarding.get_overdue_tasks()
    
    async def get_critical_tasks(self, onboarding_id: str) -> List[OnboardingTask]:
        """Get critical tasks for an onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return []
        
        return onboarding.get_critical_tasks()
    
    async def get_overdue_onboardings(self) -> List[Onboarding]:
        """Get all overdue onboardings"""
        today = date.today()
        return await Onboarding.find({
            "expected_completion_date": {"$lt": today},
            "status": {"$ne": OnboardingStatus.COMPLETED}
        }).sort(Onboarding.expected_completion_date).to_list()
    
    async def get_onboardings_by_department(self, department: str) -> List[Onboarding]:
        """Get onboardings by department"""
        return await Onboarding.find(
            Onboarding.department == department
        ).sort(Onboarding.created_at, DESCENDING).to_list()
    
    async def get_onboardings_by_assignee(self, assignee: str) -> List[Onboarding]:
        """Get onboardings assigned to a person"""
        return await Onboarding.find(
            Onboarding.assigned_to == assignee
        ).sort(Onboarding.created_at, DESCENDING).to_list()
    
    async def get_active_onboardings_count(self) -> int:
        """Get count of active onboardings"""
        return await Onboarding.find({
            "status": {"$in": [OnboardingStatus.PENDING, OnboardingStatus.IN_PROGRESS]}
        }).count()
    
    async def get_completed_onboardings_count(self) -> int:
        """Get count of completed onboardings"""
        return await Onboarding.find(Onboarding.status == OnboardingStatus.COMPLETED).count()
    
    async def get_onboarding_statistics(self) -> Dict[str, Any]:
        """Get onboarding statistics"""
        # Overall statistics
        total_onboardings = await Onboarding.count()
        active_onboardings = await self.get_active_onboardings_count()
        completed_onboardings = await self.get_completed_onboardings_count()
        overdue_onboardings = len(await self.get_overdue_onboardings())
        
        # Average completion time
        pipeline = [
            {"$match": {"status": OnboardingStatus.COMPLETED, "actual_completion_date": {"$ne": None}}},
            {
                "$project": {
                    "duration": {
                        "$dateDiff": {
                            "startDate": "$start_date",
                            "endDate": "$actual_completion_date",
                            "unit": "day"
                        }
                    }
                }
            },
            {"$group": {"_id": None, "avgDuration": {"$avg": "$duration"}}}
        ]
        
        avg_completion_result = await Onboarding.aggregate(pipeline).to_list()
        average_completion_days = avg_completion_result[0]["avgDuration"] if avg_completion_result else 0
        
        # Department breakdown
        dept_pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "total": {"$sum": 1},
                    "completed": {
                        "$sum": {"$cond": [{"$eq": ["$status", OnboardingStatus.COMPLETED]}, 1, 0]}
                    }
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        department_breakdown = await Onboarding.aggregate(dept_pipeline).to_list()
        
        # Task status breakdown
        task_pipeline = [
            {"$unwind": "$tasks"},
            {
                "$group": {
                    "_id": "$tasks.status",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        tasks_by_status = await Onboarding.aggregate(task_pipeline).to_list()
        tasks_status_dict = {item["_id"]: item["count"] for item in tasks_by_status}
        
        # Completion rate
        completion_rate = (completed_onboardings / total_onboardings * 100) if total_onboardings > 0 else 0
        
        return {
            "total_onboardings": total_onboardings,
            "active_onboardings": active_onboardings,
            "completed_onboardings": completed_onboardings,
            "overdue_onboardings": overdue_onboardings,
            "average_completion_days": average_completion_days,
            "department_breakdown": department_breakdown,
            "completion_rate": completion_rate,
            "tasks_by_status": tasks_status_dict
        }
    
    async def get_onboardings_starting_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings starting in the next N days"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return await Onboarding.find({
            "start_date": {
                "$gte": today,
                "$lte": future_date
            },
            "status": OnboardingStatus.PENDING
        }).sort(Onboarding.start_date).to_list()
    
    async def get_onboardings_completing_soon(self, days: int = 7) -> List[Onboarding]:
        """Get onboardings completing in the next N days"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return await Onboarding.find({
            "expected_completion_date": {
                "$gte": today,
                "$lte": future_date
            },
            "status": {"$in": [OnboardingStatus.PENDING, OnboardingStatus.IN_PROGRESS]}
        }).sort(Onboarding.expected_completion_date).to_list()
    
    async def add_blocker(
        self, 
        onboarding_id: str, 
        blocker_description: str, 
        severity: str = "medium"
    ) -> Optional[Onboarding]:
        """Add a blocker to onboarding"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        await onboarding.add_blocker(blocker_description, severity)
        return onboarding
    
    async def resolve_blocker(
        self, 
        onboarding_id: str, 
        blocker_index: int, 
        resolution_notes: str
    ) -> Optional[Onboarding]:
        """Resolve a blocker"""
        onboarding = await self.get_onboarding_by_id(onboarding_id)
        if not onboarding:
            return None
        
        await onboarding.resolve_blocker(blocker_index, resolution_notes)
        return onboarding
    
    async def bulk_update_onboardings(
        self,
        onboarding_ids: List[str],
        update_data: Dict[str, Any],
        modified_by: str = None
    ) -> int:
        """Bulk update onboardings"""
        result = await Onboarding.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in onboarding_ids]}}
        ).update(
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def get_tasks_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a person across all onboardings"""
        pipeline = [
            {"$unwind": "$tasks"},
            {"$match": {"tasks.assigned_to": assignee}},
            {
                "$project": {
                    "onboarding_id": "$_id",
                    "employee_name": "$employee_name",
                    "employee_code": "$employee_code",
                    "task": "$tasks"
                }
            },
            {"$sort": {"task.due_date": 1}}
        ]
        
        return await Onboarding.aggregate(pipeline).to_list()
    
    async def get_onboarding_templates(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get onboarding templates (could be stored in a separate collection)"""
        # This is a placeholder - in production, you'd have a separate templates collection
        templates = [
            {
                "name": "Standard IT Onboarding",
                "department": "engineering",
                "description": "Standard onboarding for IT roles",
                "tasks": [
                    {"title": "System account setup", "priority": "high", "department": "IT"},
                    {"title": "Laptop configuration", "priority": "high", "department": "IT"},
                    {"title": "Software installation", "priority": "medium", "department": "IT"},
                    {"title": "Security training", "priority": "high", "department": "HR"},
                    {"title": "Team introduction", "priority": "medium", "department": "HR"}
                ],
                "default_duration_days": 5
            },
            {
                "name": "Sales Onboarding",
                "department": "sales",
                "description": "Onboarding process for sales team",
                "tasks": [
                    {"title": "CRM access setup", "priority": "high", "department": "IT"},
                    {"title": "Sales training", "priority": "high", "department": "Sales"},
                    {"title": "Product training", "priority": "medium", "department": "Product"},
                    {"title": "Client meeting shadowing", "priority": "medium", "department": "Sales"}
                ],
                "default_duration_days": 7
            }
        ]
        
        if department:
            templates = [t for t in templates if t["department"] == department]
        
        return templates
    
    async def create_onboarding_from_template(
        self, 
        template_name: str, 
        employee_data: Dict[str, Any],
        created_by: str
    ) -> Optional[Onboarding]:
        """Create onboarding from template"""
        templates = await self.get_onboarding_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        
        if not template:
            return None
        
        # Calculate dates
        start_date = employee_data.get("joining_date", date.today())
        duration_days = template.get("default_duration_days", 30)
        expected_completion_date = start_date + timedelta(days=duration_days)
        
        # Create onboarding
        onboarding_data = OnboardingCreate(
            employee_id=employee_data["employee_id"],
            employee_code=employee_data["employee_code"],
            employee_name=employee_data["employee_name"],
            department=employee_data["department"],
            start_date=start_date,
            expected_completion_date=expected_completion_date,
            tasks=[OnboardingTaskCreate(**task) for task in template["tasks"]]
        )
        
        return await self.create_onboarding(onboarding_data, created_by)
