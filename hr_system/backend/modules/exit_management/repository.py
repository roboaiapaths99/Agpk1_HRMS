from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from .model import ExitManagement, ExitTask, ExitStatus, ExitReason, TaskStatus, TaskPriority
from .schema import ExitManagementCreate, ExitManagementUpdate, ExitSearch, ExitTaskCreate
from utils.helpers import create_pagination_params, get_notice_period_end_date


class ExitManagementRepository:
    """Repository for exit management operations"""
    
    async def create_exit_management(self, exit_data: ExitManagementCreate, created_by: str) -> ExitManagement:
        """Create a new exit management process"""
        # Check if exit process already exists for this employee
        existing_exit = await self.get_exit_by_employee(exit_data.employee_id)
        if existing_exit and existing_exit.status not in [ExitStatus.COMPLETED, ExitStatus.CANCELLED]:
            raise ValueError(f"Exit process already active for employee {exit_data.employee_code}")
        
        # Create exit management document
        exit_management = ExitManagement(
            **exit_data.dict(exclude={"tasks"}),
            created_by=created_by
        )
        
        # Add initial tasks if provided
        if exit_data.tasks:
            for task_data in exit_data.tasks:
                task = ExitTask(**task_data.dict())
                exit_management.tasks.append(task)
        
        # Calculate initial progress
        await exit_management.calculate_progress()
        
        await exit_management.insert()
        return exit_management
    
    async def get_exit_by_id(self, exit_id: str) -> Optional[ExitManagement]:
        """Get exit management by ID"""
        try:
            return await ExitManagement.get(PydanticObjectId(exit_id))
        except:
            return None
    
    async def get_exit_by_employee(self, employee_id: str) -> Optional[ExitManagement]:
        """Get exit management by employee ID"""
        return await ExitManagement.find_one(ExitManagement.employee_id == employee_id)
    
    async def update_exit_management(
        self, 
        exit_id: str, 
        update_data: ExitManagementUpdate, 
        modified_by: str = None
    ) -> Optional[ExitManagement]:
        """Update exit management details"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(exit_management, field, value)
        
        exit_management.updated_at = datetime.utcnow()
        
        # Recalculate progress
        await exit_management.calculate_progress()
        
        await exit_management.save()
        return exit_management
    
    async def delete_exit_management(self, exit_id: str) -> bool:
        """Delete exit management process"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return False
        
        await exit_management.delete()
        return True
    
    async def get_exits_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[ExitSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[ExitManagement], int]:
        """Get list of exit processes with pagination and filtering"""
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
            
            if search.exit_reason:
                query["exit_reason"] = search.exit_reason
            
            if search.assigned_to:
                query["assigned_to"] = search.assigned_to
            
            if search.resignation_date_from:
                if "resignation_date" in query:
                    query["resignation_date"]["$gte"] = search.resignation_date_from
                else:
                    query["resignation_date"] = {"$gte": search.resignation_date_from}
            
            if search.resignation_date_to:
                if "resignation_date" in query:
                    query["resignation_date"]["$lte"] = search.resignation_date_to
                else:
                    query["resignation_date"] = {"$lte": search.resignation_date_to}
            
            if search.last_working_day_from:
                if "last_working_day" in query:
                    query["last_working_day"]["$gte"] = search.last_working_day_from
                else:
                    query["last_working_day"] = {"$gte": search.last_working_day_from}
            
            if search.last_working_day_to:
                if "last_working_day" in query:
                    query["last_working_day"]["$lte"] = search.last_working_day_to
                else:
                    query["last_working_day"] = {"$lte": search.last_working_day_to}
            
            if search.overdue_only:
                today = date.today()
                query["last_working_day"] = {"$lt": today}
                query["status"] = {"$ne": ExitStatus.COMPLETED}
        
        # Get total count
        total = await ExitManagement.find(query).count()
        
        # Get exits with pagination and sorting
        exits = await ExitManagement.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return exits, total
    
    async def add_task_to_exit(
        self, 
        exit_id: str, 
        task_data: ExitTaskCreate
    ) -> Optional[ExitManagement]:
        """Add a new task to exit process"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.add_task(task_data.dict())
        return exit_management
    
    async def complete_task(
        self, 
        exit_id: str, 
        task_id: str, 
        completed_by: str, 
        notes: Optional[str] = None
    ) -> Optional[ExitManagement]:
        """Mark a task as completed"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.complete_task(task_id, completed_by, notes)
        return exit_management
    
    async def update_task_status(
        self, 
        exit_id: str, 
        task_id: str, 
        status: TaskStatus, 
        notes: Optional[str] = None
    ) -> Optional[ExitManagement]:
        """Update task status"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.update_task_status(task_id, status, notes)
        return exit_management
    
    async def get_overdue_tasks(self, exit_id: str) -> List[ExitTask]:
        """Get overdue tasks for an exit process"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return []
        
        return exit_management.get_overdue_tasks()
    
    async def get_exits_by_department(self, department: str) -> List[ExitManagement]:
        """Get exit processes by department"""
        return await ExitManagement.find(
            ExitManagement.department == department
        ).sort(ExitManagement.created_at, DESCENDING).to_list()
    
    async def get_exits_by_assignee(self, assignee: str) -> List[ExitManagement]:
        """Get exit processes assigned to a person"""
        return await ExitManagement.find(
            ExitManagement.assigned_to == assignee
        ).sort(ExitManagement.created_at, DESCENDING).to_list()
    
    async def get_active_exits_count(self) -> int:
        """Get count of active exit processes"""
        return await ExitManagement.find({
            "status": {"$in": [ExitStatus.INITIATED, ExitStatus.NOTICE_PERIOD, ExitStatus.HANDOVER_IN_PROGRESS]}
        }).count()
    
    async def get_completed_exits_count(self) -> int:
        """Get count of completed exit processes"""
        return await ExitManagement.find(ExitManagement.status == ExitStatus.COMPLETED).count()
    
    async def get_exit_statistics(self) -> Dict[str, Any]:
        """Get exit management statistics"""
        # Overall statistics
        total_exits = await ExitManagement.count()
        active_exits = await self.get_active_exits_count()
        completed_exits = await self.get_completed_exits_count()
        
        # Overdue exits
        today = date.today()
        overdue_pipeline = [
            {"$match": {"last_working_day": {"$lt": today}, "status": {"$ne": ExitStatus.COMPLETED}}},
            {"$count": "overdue"}
        ]
        overdue_result = await ExitManagement.aggregate(overdue_pipeline).to_list()
        overdue_exits = overdue_result[0]["overdue"] if overdue_result else 0
        
        # Average exit process duration
        pipeline = [
            {"$match": {"status": ExitStatus.COMPLETED, "actual_exit_date": {"$ne": None}}},
            {
                "$project": {
                    "duration": {
                        "$dateDiff": {
                            "startDate": "$resignation_date",
                            "endDate": "$actual_exit_date",
                            "unit": "day"
                        }
                    }
                }
            },
            {"$group": {"_id": None, "avgDuration": {"$avg": "$duration"}}}
        ]
        
        avg_result = await ExitManagement.aggregate(pipeline).to_list()
        average_exit_process_days = avg_result[0]["avgDuration"] if avg_result else 0
        
        # Department breakdown
        dept_pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "total": {"$sum": 1},
                    "completed": {
                        "$sum": {"$cond": [{"$eq": ["$status", ExitStatus.COMPLETED]}, 1, 0]}
                    }
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        department_breakdown = await ExitManagement.aggregate(dept_pipeline).to_list()
        
        # Exit reason breakdown
        reason_pipeline = [
            {
                "$group": {
                    "_id": "$exit_reason",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        exit_reason_breakdown = await ExitManagement.aggregate(reason_pipeline).to_list()
        
        # Monthly trend
        monthly_pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$resignation_date"},
                        "month": {"$month": "$resignation_date"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": -1, "_id.month": -1}},
            {
                "$project": {
                    "month": {
                        "$concat": [
                            {"$toString": "$_id.year"},
                            "-",
                            {"$toString": {
                                "$cond": [
                                    {"$lt": ["$_id.month", 10]},
                                    {"$concat": ["0", {"$toString": "$_id.month"}]},
                                    {"$toString": "$_id.month"}
                                ]
                            }}
                        ]
                    },
                    "count": "$count",
                    "_id": 0
                }
            }
        ]
        
        monthly_trend = await ExitManagement.aggregate(monthly_pipeline).to_list()
        
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
        
        tasks_by_status_result = await ExitManagement.aggregate(task_pipeline).to_list()
        tasks_by_status = {item["_id"]: item["count"] for item in tasks_by_status_result}
        
        # Completion rate
        completion_rate = (completed_exits / total_exits * 100) if total_exits > 0 else 0
        
        return {
            "total_exits": total_exits,
            "active_exits": active_exits,
            "completed_exits": completed_exits,
            "overdue_exits": overdue_exits,
            "average_exit_process_days": average_exit_process_days,
            "department_breakdown": department_breakdown,
            "exit_reason_breakdown": exit_reason_breakdown,
            "monthly_trend": monthly_trend,
            "completion_rate": completion_rate,
            "tasks_by_status": tasks_by_status
        }
    
    async def get_exits_completing_soon(self, days: int = 7) -> List[ExitManagement]:
        """Get exit processes completing in the next N days"""
        today = date.today()
        future_date = today + timedelta(days=days)
        
        return await ExitManagement.find({
            "last_working_day": {
                "$gte": today,
                "$lte": future_date
            },
            "status": {"$in": [ExitStatus.INITIATED, ExitStatus.NOTICE_PERIOD, ExitStatus.HANDOVER_IN_PROGRESS]}
        }).sort(ExitManagement.last_working_day).to_list()
    
    async def add_blocker(
        self, 
        exit_id: str, 
        blocker_description: str, 
        severity: str = "medium"
    ) -> Optional[ExitManagement]:
        """Add a blocker to exit process"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.add_blocker(blocker_description, severity)
        return exit_management
    
    async def resolve_blocker(
        self, 
        exit_id: str, 
        blocker_index: int, 
        resolution_notes: str
    ) -> Optional[ExitManagement]:
        """Resolve a blocker"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.resolve_blocker(blocker_index, resolution_notes)
        return exit_management
    
    async def complete_exit(self, exit_id: str, completion_date: date) -> Optional[ExitManagement]:
        """Complete the exit process"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.complete_exit(completion_date)
        return exit_management
    
    async def add_asset_return(
        self, 
        exit_id: str, 
        asset_name: str, 
        asset_id: str, 
        return_date: date, 
        condition: str
    ) -> Optional[ExitManagement]:
        """Add asset return record"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.add_asset_return(asset_name, asset_id, return_date, condition)
        return exit_management
    
    async def add_deduction(
        self, 
        exit_id: str, 
        deduction_type: str, 
        amount: float, 
        description: str
    ) -> Optional[ExitManagement]:
        """Add a deduction to final settlement"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.add_deduction(deduction_type, amount, description)
        return exit_management
    
    async def add_adjustment(
        self, 
        exit_id: str, 
        adjustment_type: str, 
        amount: float, 
        description: str
    ) -> Optional[ExitManagement]:
        """Add an adjustment to final settlement"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.add_adjustment(adjustment_type, amount, description)
        return exit_management
    
    async def bulk_update_exits(
        self,
        exit_ids: List[str],
        update_data: Dict[str, Any],
        modified_by: str = None
    ) -> int:
        """Bulk update exit processes"""
        result = await ExitManagement.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in exit_ids]}}
        ).update(
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def get_tasks_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a person across all exit processes"""
        pipeline = [
            {"$unwind": "$tasks"},
            {"$match": {"tasks.assigned_to": assignee}},
            {
                "$project": {
                    "exit_id": "$_id",
                    "employee_name": "$employee_name",
                    "employee_code": "$employee_code",
                    "task": "$tasks"
                }
            },
            {"$sort": {"task.due_date": 1}}
        ]
        
        return await ExitManagement.aggregate(pipeline).to_list()
    
    async def get_exits_by_reason(self, exit_reason: str) -> List[ExitManagement]:
        """Get exit processes by reason"""
        try:
            reason = ExitReason(exit_reason)
        except ValueError:
            return []
        
        return await ExitManagement.find(
            ExitManagement.exit_reason == reason
        ).sort(ExitManagement.created_at, DESCENDING).to_list()
    
    async def calculate_final_settlement(self, exit_id: str) -> Optional[ExitManagement]:
        """Calculate final settlement"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        await exit_management.calculate_final_settlement()
        return exit_management
    
    async def get_clearance_status(self, exit_id: str) -> Optional[Dict[str, Any]]:
        """Get clearance status for all departments"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        return exit_management.get_clearance_status()
    
    async def get_exit_summary(self, exit_id: str) -> Optional[Dict[str, Any]]:
        """Get exit process summary"""
        exit_management = await self.get_exit_by_id(exit_id)
        if not exit_management:
            return None
        
        return exit_management.get_exit_summary()
    
    async def get_exit_templates(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get exit process templates (could be stored in a separate collection)"""
        # This is a placeholder - in production, you'd have a separate templates collection
        templates = [
            {
                "name": "Standard Exit Process",
                "department": "general",
                "description": "Standard exit process for all departments",
                "tasks": [
                    {"title": "Exit interview", "priority": "high", "department": "HR"},
                    {"title": "Asset handover", "priority": "high", "department": "IT"},
                    {"title": "System access revocation", "priority": "high", "department": "IT"},
                    {"title": "Final settlement calculation", "priority": "high", "department": "Finance"},
                    {"title": "Experience letter issuance", "priority": "medium", "department": "HR"}
                ],
                "default_duration_days": 30
            },
            {
                "name": "IT Department Exit",
                "department": "engineering",
                "description": "Specialized exit process for IT roles",
                "tasks": [
                    {"title": "Code handover", "priority": "high", "department": "Engineering"},
                    {"title": "System credentials handover", "priority": "high", "department": "IT"},
                    {"title": "Knowledge transfer sessions", "priority": "medium", "department": "Engineering"},
                    {"title": "Exit interview", "priority": "high", "department": "HR"},
                    {"title": "Asset return", "priority": "high", "department": "IT"}
                ],
                "default_duration_days": 45
            }
        ]
        
        if department:
            templates = [t for t in templates if t["department"] == department or t["department"] == "general"]
        
        return templates
    
    async def create_exit_from_template(
        self, 
        template_name: str, 
        employee_data: Dict[str, Any],
        exit_data: Dict[str, Any],
        created_by: str
    ) -> Optional[ExitManagement]:
        """Create exit process from template"""
        templates = await self.get_exit_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        
        if not template:
            return None
        
        # Create exit management
        exit_management_data = ExitManagementCreate(
            **exit_data,
            tasks=[ExitTaskCreate(**task) for task in template["tasks"]]
        )
        
        return await self.create_exit_management(exit_management_data, created_by)
