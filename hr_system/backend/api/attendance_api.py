"""
Attendance API Module
Handles attendance operations and generates summaries from raw logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from core.database import Database
from core.config import settings

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

def calculate_worked_hours(check_in: datetime, check_out: datetime) -> float:
    """Calculate worked hours between check-in and check-out"""
    if not check_in or not check_out:
        return 0.0
    
    # Difference in hours
    diff = check_out - check_in
    hours = diff.total_seconds() / 3600
    
    # Cap at reasonable limits (e.g., max 16 hours per day)
    return min(max(hours, 0), 16)

def is_late_check_in(check_in: datetime, standard_time: datetime.time = datetime.strptime("09:00", "%H:%M").time()) -> bool:
    """Check if check-in is late"""
    return check_in.time() > standard_time

async def get_attendance_summary_for_month(employee_id: str, month: str, org_id: str = None) -> Dict[str, Any]:
    """
    Generate attendance summary for an employee for a specific month
    from raw attendance logs
    """
    try:
        database = Database.client[settings.DATABASE_NAME]
        attendance_collection = database.attendance_logs
        
        # Parse month (format: YYYY-MM)
        year, month_num = map(int, month.split('-'))
        
        # Get first and last day of month
        first_day = datetime(year, month_num, 1)
        last_day = datetime(year, month_num, calendar.monthrange(year, month_num)[1], 23, 59, 59)
        
        # Get all attendance logs for the employee in the month
        filter_query = {
            "user_id": employee_id,
            "timestamp": {"$gte": first_day, "$lte": last_day}
        }
        
        if org_id:
            filter_query["org_id"] = org_id
        
        logs = []
        async for log in attendance_collection.find(filter_query).sort("timestamp", 1):
            logs.append(log)
        
        # Group logs by date
        daily_logs = {}
        for log in logs:
            date_key = log["timestamp"].date()
            if date_key not in daily_logs:
                daily_logs[date_key] = []
            daily_logs[date_key].append(log)
        
        # Calculate daily summaries
        present_days = 0
        absent_days = 0
        late_days = 0
        half_days = 0
        total_worked_hours = 0
        overtime_hours = 0
        
        working_days_in_month = calendar.monthrange(year, month_num)[1]
        
        for day in range(1, working_days_in_month + 1):
            current_date = datetime(year, month_num, day).date()
            
            # Skip weekends (Saturday, Sunday)
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
            
            if current_date in daily_logs:
                day_logs = daily_logs[current_date]
                
                # Find check-in and check-out pairs
                check_ins = [log for log in day_logs if log["type"] == "check-in"]
                check_outs = [log for log in day_logs if log["type"] == "check-out"]
                
                if check_ins:
                    present_days += 1
                    
                    # Use first check-in and last check-out
                    first_check_in = min(check_ins, key=lambda x: x["timestamp"])["timestamp"]
                    
                    if check_outs:
                        last_check_out = max(check_outs, key=lambda x: x["timestamp"])["timestamp"]
                        
                        # Calculate worked hours
                        worked_hours = calculate_worked_hours(first_check_in, last_check_out)
                        total_worked_hours += worked_hours
                        
                        # Check if late
                        if is_late_check_in(first_check_in):
                            late_days += 1
                        
                        # Check for half day (less than 4 hours)
                        if worked_hours < 4:
                            half_days += 1
                        
                        # Calculate overtime (more than 8 hours)
                        if worked_hours > 8:
                            overtime_hours += (worked_hours - 8)
                    else:
                        # Check-in without check-out - count as present but no hours
                        pass
                else:
                    absent_days += 1
        
        return {
            "employee_id": employee_id,
            "month": month,
            "working_days": working_days_in_month,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "half_days": half_days,
            "total_worked_hours": round(total_worked_hours, 2),
            "overtime_hours": round(overtime_hours, 2),
            "attendance_percentage": round((present_days / working_days_in_month) * 100, 2) if working_days_in_month > 0 else 0
        }
        
    except Exception as e:
        print(f"Error calculating attendance summary: {e}")
        return {
            "employee_id": employee_id,
            "month": month,
            "working_days": 0,
            "present_days": 0,
            "absent_days": 0,
            "late_days": 0,
            "half_days": 0,
            "total_worked_hours": 0,
            "overtime_hours": 0,
            "attendance_percentage": 0
        }

@router.get("/today")
async def get_today_attendance(org_id: Optional[str] = None):
    """Get today's attendance summary"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        attendance_collection = database.attendance_logs
        employees_collection = database.employees
        
        # Get today's date range
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        # Build filter
        filter_query = {
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        }
        
        if org_id:
            filter_query["org_id"] = org_id
        
        # Get today's attendance logs
        today_logs = []
        async for log in attendance_collection.find(filter_query):
            today_logs.append(log)
        
        # Group by employee
        employee_attendance = {}
        for log in today_logs:
            emp_id = log["user_id"]
            if emp_id not in employee_attendance:
                employee_attendance[emp_id] = {"check_in": None, "check_out": None, "logs": []}
            employee_attendance[emp_id]["logs"].append(log)
            
            if log["type"] == "check-in":
                if not employee_attendance[emp_id]["check_in"] or log["timestamp"] < employee_attendance[emp_id]["check_in"]:
                    employee_attendance[emp_id]["check_in"] = log["timestamp"]
            elif log["type"] == "check-out":
                if not employee_attendance[emp_id]["check_out"] or log["timestamp"] > employee_attendance[emp_id]["check_out"]:
                    employee_attendance[emp_id]["check_out"] = log["timestamp"]
        
        # Get employee details
        employee_ids = list(employee_attendance.keys())
        employees = {}
        
        if employee_ids:
            cursor = employees_collection.find({"_id": {"$in": employee_ids}})
            async for emp in cursor:
                emp['_id'] = str(emp['_id'])
                employees[emp['_id']] = emp
        
        # Prepare response
        attendance_summary = []
        for emp_id, attendance in employee_attendance.items():
            emp_data = employees.get(emp_id, {})
            
            # Calculate status
            if attendance["check_in"] and attendance["check_out"]:
                status = "present"
                worked_hours = calculate_worked_hours(attendance["check_in"], attendance["check_out"])
            elif attendance["check_in"]:
                status = "checked_in"
                worked_hours = 0
            else:
                status = "absent"
                worked_hours = 0
            
            attendance_summary.append({
                "employee_id": emp_id,
                "employee_name": f"{emp_data.get('firstName', '')} {emp_data.get('lastName', '')}",
                "employee_code": emp_data.get("employeeCode", ""),
                "department": emp_data.get("department", ""),
                "check_in": attendance["check_in"],
                "check_out": attendance["check_out"],
                "worked_hours": worked_hours,
                "status": status,
                "is_late": is_late_check_in(attendance["check_in"]) if attendance["check_in"] else False
            })
        
        # Calculate totals
        total_employees = await employees_collection.count_documents({"isActive": True})
        present_today = len([a for a in attendance_summary if a["status"] == "present"])
        checked_in_today = len([a for a in attendance_summary if a["status"] in ["present", "checked_in"]])
        absent_today = total_employees - checked_in_today
        late_today = len([a for a in attendance_summary if a["is_late"]])
        
        return {
            "success": True,
            "data": {
                "date": today.isoformat(),
                "summary": {
                    "total_employees": total_employees,
                    "present_today": present_today,
                    "checked_in_today": checked_in_today,
                    "absent_today": absent_today,
                    "late_today": late_today
                },
                "attendance_records": attendance_summary
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch today's attendance: {str(e)}")

@router.get("/employee/{employee_id}")
async def get_employee_attendance(
    employee_id: str,
    month: Optional[str] = Query(None, description="Format: YYYY-MM")
):
    """Get attendance for a specific employee"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        attendance_collection = database.attendance_logs
        
        # Default to current month
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        # Get attendance summary
        summary = await get_attendance_summary_for_month(employee_id, month)
        
        # Get raw logs for detailed view
        year, month_num = map(int, month.split('-'))
        first_day = datetime(year, month_num, 1)
        last_day = datetime(year, month_num, calendar.monthrange(year, month_num)[1], 23, 59, 59)
        
        logs = []
        async for log in attendance_collection.find({
            "user_id": employee_id,
            "timestamp": {"$gte": first_day, "$lte": last_day}
        }).sort("timestamp", 1):
            log['_id'] = str(log['_id'])
            logs.append(log)
        
        return {
            "success": True,
            "data": {
                "summary": summary,
                "detailed_logs": logs
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee attendance: {str(e)}")

@router.get("/monthly-summary")
async def get_monthly_attendance_summary(
    month: str = Query(..., description="Format: YYYY-MM"),
    org_id: Optional[str] = None
):
    """Get monthly attendance summary for all employees"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        # Get all active employees
        filter_query = {"isActive": True}
        if org_id:
            filter_query["organizationId"] = org_id
        
        employees = []
        async for emp in employees_collection.find(filter_query):
            emp['_id'] = str(emp['_id'])
            employees.append(emp)
        
        # Get attendance summary for each employee
        summaries = []
        for emp in employees:
            summary = await get_attendance_summary_for_month(emp['_id'], month, org_id)
            summary["employee_name"] = f"{emp.get('firstName', '')} {emp.get('lastName', '')}"
            summary["employee_code"] = emp.get("employeeCode", "")
            summary["department"] = emp.get("department", "")
            summaries.append(summary)
        
        # Calculate overall summary
        total_present = sum(s["present_days"] for s in summaries)
        total_absent = sum(s["absent_days"] for s in summaries)
        total_late = sum(s["late_days"] for s in summaries)
        total_worked_hours = sum(s["total_worked_hours"] for s in summaries)
        total_overtime = sum(s["overtime_hours"] for s in summaries)
        
        return {
            "success": True,
            "data": {
                "month": month,
                "overall_summary": {
                    "total_employees": len(employees),
                    "total_present_days": total_present,
                    "total_absent_days": total_absent,
                    "total_late_days": total_late,
                    "total_worked_hours": round(total_worked_hours, 2),
                    "total_overtime_hours": round(total_overtime, 2),
                    "average_attendance_percentage": round(sum(s["attendance_percentage"] for s in summaries) / len(summaries), 2) if summaries else 0
                },
                "employee_summaries": summaries
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch monthly attendance summary: {str(e)}")

@router.get("/live")
async def get_live_attendance(org_id: Optional[str] = None):
    """Get live attendance status of all employees"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        attendance_collection = database.attendance_logs
        employees_collection = database.employees
        
        # Get current time
        now = datetime.now()
        
        # Get all active employees
        filter_query = {"isActive": True}
        if org_id:
            filter_query["organizationId"] = org_id
        
        employees = []
        async for emp in employees_collection.find(filter_query):
            emp['_id'] = str(emp['_id'])
            employees.append(emp)
        
        live_status = []
        for emp in employees:
            # Get today's attendance for this employee
            today = now.date()
            start_of_day = datetime.combine(today, datetime.min.time())
            
            latest_log = await attendance_collection.find_one({
                "user_id": emp['_id'],
                "timestamp": {"$gte": start_of_day}
            }).sort("timestamp", -1)
            
            if latest_log:
                status = latest_log["type"]
                last_seen = latest_log["timestamp"]
                is_late = status == "check-in" and is_late_check_in(last_seen)
            else:
                status = "not_checked_in"
                last_seen = None
                is_late = False
            
            live_status.append({
                "employee_id": emp['_id'],
                "employee_name": f"{emp.get('firstName', '')} {emp.get('lastName', '')}",
                "employee_code": emp.get("employeeCode", ""),
                "department": emp.get("department", ""),
                "status": status,
                "last_seen": last_seen,
                "is_late": is_late
            })
        
        return {
            "success": True,
            "data": {
                "timestamp": now.isoformat(),
                "employees": live_status
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live attendance: {str(e)}")
