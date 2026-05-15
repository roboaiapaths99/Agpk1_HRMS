from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from models.exit_management_model import ExitManagement, ExitTask, ExitStatus, TaskStatus, TaskPriority
from utils.helpers import create_pagination_params


class ExitManagementRepository:
    """Repository for exit management operations"""
    
    async def create_exit_management(self, exit_data, created_by: str = None) -> ExitManagement:
        """Create a new exit management process"""
        exit_management = ExitManagement(**exit_data.dict())
        if created_by:
            exit_management.created_by = created_by
        await exit_management.insert()
        return exit_management
    
    async def get_exit_management_by_id(self, exit_id: str) -> Optional[ExitManagement]:
        """Get exit management by ID"""
        try:
            return await ExitManagement.get(PydanticObjectId(exit_id))
        except:
            return None
    
    async def get_exit_management_by_employee(self, employee_id: str) -> Optional[ExitManagement]:
        """Get exit management by employee ID"""
        return await ExitManagement.find_one({"employee_id": employee_id})
    
    async def update_exit_management(self, exit_id: str, update_data, modified_by: str = None) -> Optional[ExitManagement]:
        """Update exit management details"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if modified_by:
            update_dict["last_modified_by"] = modified_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            if hasattr(exit_management, field):
                setattr(exit_management, field, value)
        
        await exit_management.save()
        return exit_management
    
    async def delete_exit_management(self, exit_id: str) -> bool:
        """Delete exit management process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return False
        
        await exit_management.delete()
        return True
    
    async def get_exits_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[dict] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        exit_reason: Optional[str] = None,
        assigned_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[ExitManagement], int]:
        """Get list of exit processes with pagination and filtering"""
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
                query["status"] = ExitStatus(status)
            except ValueError:
                pass
        
        if exit_reason:
            query["exit_reason"] = exit_reason
        
        if assigned_to:
            query["assigned_to"] = assigned_to
        
        # Get total count
        total = await ExitManagement.find(query).count()
        
        # Get exit processes with pagination and sorting
        exits = await ExitManagement.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return exits, total
    
    async def add_task_to_exit(self, exit_id: str, task_data) -> Optional[ExitManagement]:
        """Add a new task to exit process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return None
        
        # Create new task
        task = ExitTask(**task_data.dict())
        task.created_at = datetime.utcnow()
        
        exit_management.tasks.append(task)
        await exit_management.save()
        
        return exit_management
    
    async def complete_task(self, exit_id: str, task_id: str, completed_by: str, notes: Optional[str] = None) -> Optional[ExitManagement]:
        """Mark a task as completed"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return None
        
        # Find and update the task
        for task in exit_management.tasks:
            if str(task.id) == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.completed_by = completed_by
                if notes:
                    task.notes = notes
                break
        
        await exit_management.save()
        return exit_management
    
    async def update_task_status(self, exit_id: str, task_id: str, status: TaskStatus, notes: Optional[str] = None) -> Optional[ExitManagement]:
        """Update task status"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return None
        
        # Find and update the task
        for task in exit_management.tasks:
            if str(task.id) == task_id:
                task.status = status
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                if notes:
                    task.notes = notes
                break
        
        await exit_management.save()
        return exit_management
    
    async def get_overdue_tasks(self, exit_id: str) -> List[ExitTask]:
        """Get overdue tasks for an exit process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return []
        
        overdue_tasks = []
        for task in exit_management.tasks:
            if task.is_overdue():
                overdue_tasks.append(task)
        
        return overdue_tasks
    
    async def get_exit_statistics(self) -> dict:
        """Get exit management statistics"""
        total_exits = await ExitManagement.count()
        
        # Status breakdown
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = await ExitManagement.aggregate(status_pipeline).to_list()
        
        # Exit reason breakdown
        reason_pipeline = [
            {"$group": {"_id": "$exit_reason", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        reason_stats = await ExitManagement.aggregate(reason_pipeline).to_list()
        
        # Department breakdown
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        dept_stats = await ExitManagement.aggregate(dept_pipeline).to_list()
        
        # Recent exits (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_exits = await ExitManagement.find({
            "created_at": {"$gte": thirty_days_ago}
        }).count()
        
        # Average exit process duration
        completed_exits = await ExitManagement.find({
            "status": ExitStatus.COMPLETED,
            "completed_at": {"$ne": None}
        }).to_list()
        
        avg_duration_days = 0
        if completed_exits:
            total_days = 0
            for exit_process in completed_exits:
                if exit_process.completed_at and exit_process.resignation_date:
                    days = (exit_process.completed_at.date() - exit_process.resignation_date).days
                    total_days += days
            
            avg_duration_days = total_days / len(completed_exits)
        
        return {
            "total_exits": total_exits,
            "status_breakdown": status_stats,
            "exit_reason_breakdown": reason_stats,
            "department_breakdown": dept_stats,
            "recent_exits": recent_exits,
            "average_exit_process_days": round(avg_duration_days, 2)
        }
    
    async def get_exits_by_department(self, department: str) -> List[ExitManagement]:
        """Get exit processes by department"""
        return await ExitManagement.find(
            {"department": department}
        ).sort(ExitManagement.created_at, DESCENDING).to_list()
    
    async def get_exits_by_assignee(self, assignee: str) -> List[ExitManagement]:
        """Get exit processes assigned to a person"""
        return await ExitManagement.find(
            {"assigned_to": assignee}
        ).sort(ExitManagement.created_at, DESCENDING).to_list()
    
    async def complete_exit(self, exit_id: str, completion_date: date, completed_by: str) -> Optional[ExitManagement]:
        """Complete the exit process"""
        exit_management = await self.get_exit_management_by_id(exit_id)
        if not exit_management:
            return None
        
        exit_management.status = ExitStatus.COMPLETED
        exit_management.completed_at = datetime.utcnow()
        exit_management.completion_date = completion_date
        exit_management.completed_by = completed_by
        
        await exit_management.save()
        return exit_management
    
    async def get_exits_completing_soon(self, days: int = 7) -> List[ExitManagement]:
        """Get exit processes completing in the next N days"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return await ExitManagement.find({
            "status": {"$ne": ExitStatus.COMPLETED},
            "last_working_day": {"$gte": today, "$lte": end_date}
        }).sort(ExitManagement.last_working_day, ASCENDING).to_list()
    
    async def get_compliance_report(self, payroll_month: str) -> dict:
        """Generate compliance report"""
        # Get all exits for the month
        start_of_month = datetime.strptime(payroll_month, "%Y-%m")
        end_of_month = start_of_month.replace(day=28) + timedelta(days=4)  # End of month
        end_of_month = end_of_month - timedelta(days=end_of_month.day)
        
        exits = await ExitManagement.find({
            "last_working_day": {"$gte": start_of_month.date(), "$lte": end_of_month.date()}
        }).to_list()
        
        total_exits = len(exits)
        completed_exits = len([e for e in exits if e.status == ExitStatus.COMPLETED])
        
        # Calculate compliance metrics
        with_final_settlement = len([e for e in exits if e.final_settlement])
        with_exit_interview = len([e for e in exits if e.exit_interview])
        with_feedback = len([e for e in exits if e.employee_feedback])
        
        return {
            "payroll_month": payroll_month,
            "total_exits": total_exits,
            "completed_exits": completed_exits,
            "completion_rate": (completed_exits / total_exits * 100) if total_exits > 0 else 0,
            "final_settlement_rate": (with_final_settlement / total_exits * 100) if total_exits > 0 else 0,
            "exit_interview_rate": (with_exit_interview / total_exits * 100) if total_exits > 0 else 0,
            "feedback_rate": (with_feedback / total_exits * 100) if total_exits > 0 else 0
        }
