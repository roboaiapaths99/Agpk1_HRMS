from typing import List, Dict, Any, Optional
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.database import Database
import logging

logger = logging.getLogger(__name__)


class AttendanceRepository:
    """Repository for attendance records"""
    
    def __init__(self):
        self.db = None  # Will be set in async init
        self.collection = None  # Will be set in async init
    
    async def init_db(self):
        """Initialize database connection"""
        if not self.db:
            self.db = await Database.get_database()
            self.collection = self.db["attendance_logs"]  # Use your existing collection
    
    async def get_employee_attendance(
        self, 
        employee_id: str, 
        month: str,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records for an employee for a specific month"""
        try:
            await self.init_db()
            
            # Parse month and year from month string (e.g., "2024-01")
            if "-" in month:
                year, month_num = month.split("-")
                year = int(year)
                month_num = month_num
            else:
                # If just month name like "January", use provided year
                month_num = month
                year = year or datetime.now().year
            
            query = {
                "employee_id": employee_id,
                "year": year,
                "month": month_num
            }
            
            records = await self.collection.find(query).to_list(None)
            logger.info(f"Found {len(records)} attendance records for employee {employee_id}")
            return records
            
        except Exception as e:
            logger.error(f"Error fetching attendance: {e}")
            return []
    
    async def get_attendance_summary(
        self,
        employee_id: str,
        month: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get attendance summary for an employee"""
        try:
            records = await self.get_employee_attendance(employee_id, month, year)
            
            if not records:
                return {
                    "total_days": 0,
                    "present_days": 0,
                    "absent_days": 0,
                    "leave_days": 0,
                    "holidays": 0,
                    "attendance_percentage": 0
                }
            
            # Calculate summary
            total_days = len(records)
            present_days = len([r for r in records if r.get("status") == "present"])
            absent_days = len([r for r in records if r.get("status") == "absent"])
            leave_days = len([r for r in records if r.get("status") == "leave"])
            holidays = len([r for r in records if r.get("status") == "holiday"])
            
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            summary = {
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "leave_days": leave_days,
                "holidays": holidays,
                "attendance_percentage": round(attendance_percentage, 2)
            }
            
            logger.info(f"Attendance summary for {employee_id}: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating attendance summary: {e}")
            return {
                "total_days": 0,
                "present_days": 0,
                "absent_days": 0,
                "leave_days": 0,
                "holidays": 0,
                "attendance_percentage": 0
            }
    
    async def get_monthly_attendance(
        self,
        month: str,
        year: Optional[int] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance for all employees for a specific month"""
        try:
            # Parse month and year
            if "-" in month:
                year, month_num = month.split("-")
                year = int(year)
                month_num = month_num
            else:
                month_num = month
                year = year or datetime.now().year
            
            query = {
                "year": year,
                "month": month_num
            }
            
            if department:
                query["department"] = department
            
            records = await self.collection.find(query).to_list(None)
            logger.info(f"Found {len(records)} attendance records for {month}")
            return records
            
        except Exception as e:
            logger.error(f"Error fetching monthly attendance: {e}")
            return []
    
    async def create_attendance_record(
        self,
        attendance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new attendance record"""
        try:
            attendance_data["created_at"] = datetime.utcnow()
            attendance_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.insert_one(attendance_data)
            attendance_data["_id"] = result.inserted_id
            
            logger.info(f"Created attendance record: {attendance_data.get('employee_id')}")
            return attendance_data
            
        except Exception as e:
            logger.error(f"Error creating attendance record: {e}")
            return {}
    
    async def update_attendance_record(
        self,
        record_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """Update an attendance record"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": record_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated attendance record: {record_id}")
                return True
            else:
                logger.warning(f"No attendance record found with ID: {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating attendance record: {e}")
            return False
    
    async def get_attendance_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get attendance statistics for a date range"""
        try:
            query = {}
            
            if start_date:
                query["date"] = {"$gte": start_date}
            
            if end_date:
                if "date" in query:
                    query["date"]["$lte"] = end_date
                else:
                    query["date"] = {"$lte": end_date}
            
            # Aggregate pipeline for statistics
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await self.collection.aggregate(pipeline).to_list(None)
            
            # Process results
            stats = {
                "total_records": 0,
                "present": 0,
                "absent": 0,
                "leave": 0,
                "holiday": 0
            }
            
            for result in results:
                status = result["_id"]
                count = result["count"]
                stats["total_records"] += count
                
                if status == "present":
                    stats["present"] = count
                elif status == "absent":
                    stats["absent"] = count
                elif status == "leave":
                    stats["leave"] = count
                elif status == "holiday":
                    stats["holiday"] = count
            
            # Calculate percentages
            if stats["total_records"] > 0:
                stats["present_percentage"] = round(
                    (stats["present"] / stats["total_records"]) * 100, 2
                )
                stats["absent_percentage"] = round(
                    (stats["absent"] / stats["total_records"]) * 100, 2
                )
            else:
                stats["present_percentage"] = 0
                stats["absent_percentage"] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating attendance statistics: {e}")
            return {
                "total_records": 0,
                "present": 0,
                "absent": 0,
                "leave": 0,
                "holiday": 0,
                "present_percentage": 0,
                "absent_percentage": 0
            }
    
    async def check_database_connection(self) -> bool:
        """Check if we can connect to the attendance database"""
        try:
            # Try to get collection info
            await self.collection.find_one()
            logger.info("Successfully connected to attendance database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to attendance database: {e}")
            return False
