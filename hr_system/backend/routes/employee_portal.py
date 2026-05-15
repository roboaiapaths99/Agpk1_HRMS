from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from models.user_model import User, UserRole
from models.employee_model import Employee
from models.payroll_model import Payroll
from core.security import SecurityManager
from utils.logger import setup_logging

logger = setup_logging()
security = HTTPBearer()
router = APIRouter()

# Pydantic models for responses
class EmployeeStats(BaseModel):
    present_days: int
    leave_balance: int
    attendance_rate: float
    current_salary: str

class LeaveRequest(BaseModel):
    type: str
    from_date: str
    to_date: str
    status: str

class Payslip(BaseModel):
    month: str
    amount: str
    status: str

class Announcement(BaseModel):
    id: int
    message: str
    date: str

class TodayStatus(BaseModel):
    check_in: str
    check_out: str
    shift: str
    working_hours: str

class EmployeeDashboardData(BaseModel):
    stats: EmployeeStats
    leave_requests: List[LeaveRequest]
    payslips: List[Payslip]
    announcements: List[Announcement]
    today_status: TodayStatus

# Dependency to get current employee
async def get_current_employee(token: str = Depends(security)) -> Employee:
    """Get current authenticated employee"""
    try:
        # Decode token to get user info
        payload = SecurityManager.decode_access_token(token.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = await User.get(user_id)
        if not user or user.role != UserRole.EMPLOYEE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Employee role required."
            )
        
        # Get employee associated with user
        employee = await Employee.find_one(Employee.user_id == user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        
        return employee
        
    except Exception as e:
        logger.error(f"Error authenticating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.get("/dashboard", response_model=EmployeeDashboardData)
async def get_employee_dashboard(current_employee: Employee = Depends(get_current_employee)):
    """Get employee dashboard data"""
    try:
        # Mock data for now - replace with actual database queries
        stats = EmployeeStats(
            present_days=22,
            leave_balance=8,
            attendance_rate=92.5,
            current_salary="₹35,000"
        )
        
        leave_requests = [
            LeaveRequest(
                type="Casual Leave",
                from_date="2026-04-10",
                to_date="2026-04-11",
                status="Pending"
            ),
            LeaveRequest(
                type="Sick Leave",
                from_date="2026-03-20",
                to_date="2026-03-20",
                status="Approved"
            )
        ]
        
        payslips = [
            Payslip(
                month="March 2026",
                amount="₹35,000",
                status="Available"
            ),
            Payslip(
                month="February 2026",
                amount="₹35,000",
                status="Available"
            )
        ]
        
        announcements = [
            Announcement(
                id=1,
                message="Office will remain closed on 14 April for Ambedkar Jayanti.",
                date="2026-04-08"
            ),
            Announcement(
                id=2,
                message="Please submit timesheets before Friday evening.",
                date="2026-04-07"
            ),
            Announcement(
                id=3,
                message="New HR policy update is now available.",
                date="2026-04-06"
            )
        ]
        
        today_status = TodayStatus(
            check_in="09:15 AM",
            check_out="Not marked",
            shift="General Shift",
            working_hours="6h 20m"
        )
        
        return EmployeeDashboardData(
            stats=stats,
            leave_requests=leave_requests,
            payslips=payslips,
            announcements=announcements,
            today_status=today_status
        )
        
    except Exception as e:
        logger.error(f"Error fetching employee dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data"
        )

@router.post("/mark-attendance")
async def mark_attendance(
    action: str,  # "check_in" or "check_out"
    current_employee: Employee = Depends(get_current_employee)
):
    """Mark employee attendance"""
    try:
        # Mock implementation - replace with actual attendance logic
        if action not in ["check_in", "check_out"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'check_in' or 'check_out'"
            )
        
        # Here you would:
        # 1. Check if attendance already marked for today
        # 2. Create attendance record
        # 3. Update employee attendance stats
        
        return {
            "success": True,
            "message": f"Attendance {action.replace('_', ' ')} marked successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark attendance"
        )

@router.post("/apply-leave")
async def apply_leave(
    leave_type: str,
    from_date: date,
    to_date: date,
    reason: str,
    current_employee: Employee = Depends(get_current_employee)
):
    """Apply for leave"""
    try:
        # Validate dates
        if from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="From date cannot be after to date"
            )
        
        if from_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot apply for leave in the past"
            )
        
        # Here you would:
        # 1. Check leave balance
        # 2. Create leave request
        # 3. Send notification to manager
        
        return {
            "success": True,
            "message": "Leave application submitted successfully",
            "leave_id": "leave_12345",  # Mock ID
            "status": "Pending"
        }
        
    except Exception as e:
        logger.error(f"Error applying leave: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply leave"
        )

@router.get("/payslips/{month}")
async def download_payslip(
    month: str,
    current_employee: Employee = Depends(get_current_employee)
):
    """Download payslip for a specific month"""
    try:
        # Here you would:
        # 1. Validate month format
        # 2. Check if payslip exists for employee
        # 3. Generate or retrieve payslip PDF
        # 4. Return file download URL
        
        return {
            "success": True,
            "download_url": f"/api/v1/files/payslips/{current_employee.employee_id}_{month}.pdf",
            "message": "Payslip ready for download"
        }
        
    except Exception as e:
        logger.error(f"Error downloading payslip: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download payslip"
        )

@router.get("/profile")
async def get_employee_profile(current_employee: Employee = Depends(get_current_employee)):
    """Get employee profile information"""
    try:
        # Get associated user for additional info
        user = await User.get(current_employee.user_id)
        
        return {
            "employee_id": current_employee.employee_id,
            "full_name": current_employee.full_name,
            "email": user.email if user else "",
            "department": current_employee.department,
            "position": current_employee.position,
            "join_date": current_employee.hire_date.isoformat() if current_employee.hire_date else "",
            "phone": current_employee.phone,
            "address": current_employee.address,
            "emergency_contact": current_employee.emergency_contact
        }
        
    except Exception as e:
        logger.error(f"Error fetching employee profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.put("/profile")
async def update_employee_profile(
    profile_data: dict,
    current_employee: Employee = Depends(get_current_employee)
):
    """Update employee profile information"""
    try:
        # Here you would:
        # 1. Validate update data
        # 2. Update employee record
        # 3. Log the change
        
        # Mock update
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating employee profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
