"""
Payroll API Module
Handles payroll generation and management with real calculations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import uuid

from core.database import Database
from core.config import settings
from api.attendance_api import get_attendance_summary_for_month

router = APIRouter(prefix="/api/payroll", tags=["payroll"])

def calculate_payroll_components(
    monthly_salary: float,
    attendance_summary: Dict[str, Any],
    payroll_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate payroll components based on salary and attendance
    """
    
    # Default payroll settings
    default_settings = {
        "standard_work_hours": 8,  # per day
        "overtime_rate": 1.5,      # 1.5x hourly rate
        "late_deduction_rate": 0,  # percentage of daily salary
        "absent_deduction_rate": 1,  # full day deduction
        "half_day_deduction_rate": 0.5,  # 50% deduction
        "provident_fund_rate": 0.12,  # 12% of basic
        "professional_tax": 200,    # fixed amount
        "income_tax_rate": 0.1      # 10% (simplified)
    }
    
    settings = payroll_settings or default_settings
    
    # Calculate daily salary
    working_days = attendance_summary.get("working_days", 30)
    present_days = attendance_summary.get("present_days", 0)
    absent_days = attendance_summary.get("absent_days", 0)
    late_days = attendance_summary.get("late_days", 0)
    half_days = attendance_summary.get("half_days", 0)
    overtime_hours = attendance_summary.get("overtime_hours", 0)
    
    daily_salary = monthly_salary / working_days
    hourly_salary = daily_salary / settings["standard_work_hours"]
    
    # Calculate earnings
    basic_salary = monthly_salary
    overtime_amount = overtime_hours * hourly_salary * settings["overtime_rate"]
    bonus = 0  # Can be added later
    
    gross_earnings = basic_salary + overtime_amount + bonus
    
    # Calculate deductions
    attendance_deduction = 0
    
    # Absent days deduction
    attendance_deduction += absent_days * daily_salary * settings["absent_deduction_rate"]
    
    # Half days deduction
    attendance_deduction += half_days * daily_salary * settings["half_day_deduction_rate"]
    
    # Late days deduction (if configured)
    if settings["late_deduction_rate"] > 0:
        attendance_deduction += late_days * daily_salary * settings["late_deduction_rate"]
    
    # Other deductions
    provident_fund = basic_salary * settings["provident_fund_rate"]
    professional_tax = settings["professional_tax"]
    
    # Income tax (simplified calculation)
    taxable_income = gross_earnings - provident_fund - professional_tax - attendance_deduction
    income_tax = max(0, taxable_income * settings["income_tax_rate"])
    
    total_deductions = attendance_deduction + provident_fund + professional_tax + income_tax
    
    # Net salary
    net_salary = gross_earnings - total_deductions
    
    return {
        "basic_salary": round(basic_salary, 2),
        "daily_salary": round(daily_salary, 2),
        "hourly_salary": round(hourly_salary, 2),
        "overtime_hours": overtime_hours,
        "overtime_amount": round(overtime_amount, 2),
        "bonus": round(bonus, 2),
        "gross_earnings": round(gross_earnings, 2),
        "attendance_deduction": round(attendance_deduction, 2),
        "provident_fund": round(provident_fund, 2),
        "professional_tax": round(professional_tax, 2),
        "income_tax": round(income_tax, 2),
        "total_deductions": round(total_deductions, 2),
        "net_salary": round(net_salary, 2),
        "attendance_summary": {
            "working_days": working_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "half_days": half_days,
            "overtime_hours": overtime_hours
        }
    }

@router.post("/generate")
async def generate_payroll(request: dict):
    """
    Generate payroll for all employees for a specific month
    """
    try:
        month = request.get("month")
        organization_id = request.get("organizationId", "test_org_123")
        payroll_settings = request.get("settings", {})
        
        if not month:
            raise HTTPException(status_code=400, detail="Month is required (format: YYYY-MM)")
        
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        payroll_collection = database.payrolls
        
        # Get all active employees
        employees = []
        async for emp in employees_collection.find({
            "isActive": True,
            "organizationId": organization_id
        }):
            emp['_id'] = str(emp['_id'])
            employees.append(emp)
        
        if not employees:
            raise HTTPException(status_code=404, detail="No active employees found")
        
        generated_payrolls = []
        errors = []
        
        for emp in employees:
            try:
                # Get attendance summary for the employee
                attendance_summary = await get_attendance_summary_for_month(
                    emp['_id'], month, organization_id
                )
                
                # Calculate payroll components
                payroll_components = calculate_payroll_components(
                    emp.get("monthlySalary", 0),
                    attendance_summary,
                    payroll_settings
                )
                
                # Create payroll record
                payroll_record = {
                    "_id": str(uuid.uuid4()),
                    "employee_id": emp['_id'],
                    "org_id": organization_id,
                    "month": month,
                    "employee_name": f"{emp.get('firstName', '')} {emp.get('lastName', '')}",
                    "employee_code": emp.get("employeeCode", ""),
                    "department": emp.get("department", ""),
                    "designation": emp.get("designation", ""),
                    "basic_salary": payroll_components["basic_salary"],
                    "daily_salary": payroll_components["daily_salary"],
                    "hourly_salary": payroll_components["hourly_salary"],
                    "present_days": payroll_components["attendance_summary"]["present_days"],
                    "absent_days": payroll_components["attendance_summary"]["absent_days"],
                    "late_days": payroll_components["attendance_summary"]["late_days"],
                    "half_days": payroll_components["attendance_summary"]["half_days"],
                    "overtime_hours": payroll_components["attendance_summary"]["overtime_hours"],
                    "overtime_amount": payroll_components["overtime_amount"],
                    "bonus": payroll_components["bonus"],
                    "gross_earnings": payroll_components["gross_earnings"],
                    "attendance_deduction": payroll_components["attendance_deduction"],
                    "provident_fund": payroll_components["provident_fund"],
                    "professional_tax": payroll_components["professional_tax"],
                    "income_tax": payroll_components["income_tax"],
                    "total_deductions": payroll_components["total_deductions"],
                    "net_salary": payroll_components["net_salary"],
                    "status": "processed",
                    "generated_by": current_user.get("email", "system"),
                    "generated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Check if payroll already exists for this employee and month
                existing = await payroll_collection.find_one({
                    "employee_id": emp['_id'],
                    "month": month,
                    "org_id": organization_id
                })
                
                if existing:
                    # Update existing payroll
                    await payroll_collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": payroll_record}
                    )
                    payroll_record["_id"] = str(existing["_id"])
                else:
                    # Insert new payroll
                    result = await payroll_collection.insert_one(payroll_record)
                    payroll_record["_id"] = str(result.inserted_id)
                
                generated_payrolls.append(payroll_record)
                
            except Exception as e:
                errors.append({
                    "employee_id": emp['_id'],
                    "employee_name": f"{emp.get('firstName', '')} {emp.get('lastName', '')}",
                    "error": str(e)
                })
        
        # Calculate summary statistics
        total_employees = len(employees)
        total_generated = len(generated_payrolls)
        total_net_salary = sum(p["net_salary"] for p in generated_payrolls)
        total_gross_salary = sum(p["gross_earnings"] for p in generated_payrolls)
        
        return {
            "success": True,
            "data": {
                "month": month,
                "organization_id": organization_id,
                "summary": {
                    "total_employees": total_employees,
                    "total_generated": total_generated,
                    "total_errors": len(errors),
                    "total_net_salary": round(total_net_salary, 2),
                    "total_gross_salary": round(total_gross_salary, 2),
                    "average_net_salary": round(total_net_salary / total_generated, 2) if total_generated > 0 else 0
                },
                "payroll_records": generated_payrolls,
                "errors": errors
            },
            "message": f"Payroll generated for {total_generated} employees"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate payroll: {str(e)}")

@router.get("/")
async def get_payroll_records(
    month: Optional[str] = Query(None, description="Format: YYYY-MM"),
    employee_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    org_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get payroll records with optional filters"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        payroll_collection = database.payrolls
        
        # Build filter
        filter_query = {}
        if month:
            filter_query["month"] = month
        if employee_id:
            filter_query["employee_id"] = employee_id
        if status:
            filter_query["status"] = status
        if org_id:
            filter_query["org_id"] = org_id
        
        # Get payroll records
        records = []
        cursor = payroll_collection.find(filter_query).sort("generated_at", -1).skip(skip).limit(limit)
        
        async for record in cursor:
            record['_id'] = str(record['_id'])
            records.append(record)
        
        # Get total count
        total = await payroll_collection.count_documents(filter_query)
        
        # Calculate summary
        total_net_salary = sum(r["net_salary"] for r in records)
        total_gross_salary = sum(r["gross_earnings"] for r in records)
        
        return {
            "success": True,
            "data": {
                "records": records,
                "summary": {
                    "total_records": total,
                    "total_net_salary": round(total_net_salary, 2),
                    "total_gross_salary": round(total_gross_salary, 2),
                    "average_net_salary": round(total_net_salary / len(records), 2) if records else 0
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payroll records: {str(e)}")

@router.get("/{payroll_id}")
async def get_payroll_by_id(payroll_id: str):
    """Get a specific payroll record by ID"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        payroll_collection = database.payrolls
        
        payroll = await payroll_collection.find_one({"_id": payroll_id})
        
        if not payroll:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        payroll['_id'] = str(payroll['_id'])
        
        return {
            "success": True,
            "data": payroll
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payroll record: {str(e)}")

@router.patch("/{payroll_id}/status")
async def update_payroll_status(
    payroll_id: str,
    status_update: dict
):
    """Update payroll status"""
    try:
        new_status = status_update.get("status")
        
        if new_status not in ["pending", "processed", "paid", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        database = Database.client[settings.DATABASE_NAME]
        payroll_collection = database.payrolls
        
        # Check if payroll exists
        existing = await payroll_collection.find_one({"_id": payroll_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        # Prepare update data
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow(),
            "updated_by": current_user.get("email", "system")
        }
        
        # Add paid_at if status is paid
        if new_status == "paid":
            update_data["paid_at"] = datetime.utcnow()
            update_data["paid_by"] = current_user.get("email", "system")
        
        # Update payroll
        result = await payroll_collection.update_one(
            {"_id": payroll_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated payroll
            updated_payroll = await payroll_collection.find_one({"_id": payroll_id})
            updated_payroll['_id'] = str(updated_payroll['_id'])
            
            return {
                "success": True,
                "data": updated_payroll,
                "message": f"Payroll status updated to {new_status}"
            }
        else:
            raise HTTPException(status_code=500, detail="No changes made")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payroll status: {str(e)}")

@router.post("/{payroll_id}/regenerate")
async def regenerate_payroll_for_employee(
    payroll_id: str
):
    """Regenerate payroll for a specific employee"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        payroll_collection = database.payrolls
        employees_collection = database.employees
        
        # Get existing payroll
        existing_payroll = await payroll_collection.find_one({"_id": payroll_id})
        if not existing_payroll:
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        # Get employee details
        employee = await employees_collection.find_one({"_id": existing_payroll["employee_id"]})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get updated attendance summary
        attendance_summary = await get_attendance_summary_for_month(
            existing_payroll["employee_id"], 
            existing_payroll["month"], 
            existing_payroll["org_id"]
        )
        
        # Recalculate payroll
        payroll_components = calculate_payroll_components(
            employee.get("monthlySalary", 0),
            attendance_summary
        )
        
        # Update payroll record
        update_data = {
            "basic_salary": payroll_components["basic_salary"],
            "daily_salary": payroll_components["daily_salary"],
            "hourly_salary": payroll_components["hourly_salary"],
            "present_days": payroll_components["attendance_summary"]["present_days"],
            "absent_days": payroll_components["attendance_summary"]["absent_days"],
            "late_days": payroll_components["attendance_summary"]["late_days"],
            "half_days": payroll_components["attendance_summary"]["half_days"],
            "overtime_hours": payroll_components["attendance_summary"]["overtime_hours"],
            "overtime_amount": payroll_components["overtime_amount"],
            "gross_earnings": payroll_components["gross_earnings"],
            "attendance_deduction": payroll_components["attendance_deduction"],
            "total_deductions": payroll_components["total_deductions"],
            "net_salary": payroll_components["net_salary"],
            "status": "processed",
            "regenerated_at": datetime.utcnow(),
            "regenerated_by": current_user.get("email", "system"),
            "updated_at": datetime.utcnow()
        }
        
        result = await payroll_collection.update_one(
            {"_id": payroll_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated payroll
            updated_payroll = await payroll_collection.find_one({"_id": payroll_id})
            updated_payroll['_id'] = str(updated_payroll['_id'])
            
            return {
                "success": True,
                "data": updated_payroll,
                "message": "Payroll regenerated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to regenerate payroll")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate payroll: {str(e)}")

@router.get("/stats/summary")
async def get_payroll_summary(
    month: Optional[str] = Query(None, description="Format: YYYY-MM"),
    org_id: Optional[str] = None
):
    """Get payroll summary statistics"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        payroll_collection = database.payrolls
        
        # Build filter
        filter_query = {}
        if month:
            filter_query["month"] = month
        if org_id:
            filter_query["org_id"] = org_id
        
        # Aggregate payroll data
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_net_salary": {"$sum": "$net_salary"},
                "total_gross_salary": {"$sum": "$gross_earnings"},
                "average_net_salary": {"$avg": "$net_salary"}
            }}
        ]
        
        status_stats = {}
        async for stat in payroll_collection.aggregate(pipeline):
            status_stats[stat["_id"]] = {
                "count": stat["count"],
                "total_net_salary": round(stat["total_net_salary"], 2),
                "total_gross_salary": round(stat["total_gross_salary"], 2),
                "average_net_salary": round(stat["average_net_salary"], 2)
            }
        
        # Get overall totals
        total_pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": None,
                "total_records": {"$sum": 1},
                "total_net_salary": {"$sum": "$net_salary"},
                "total_gross_salary": {"$sum": "$gross_earnings"},
                "average_net_salary": {"$avg": "$net_salary"},
                "max_net_salary": {"$max": "$net_salary"},
                "min_net_salary": {"$min": "$net_salary"}
            }}
        ]
        
        overall_stats = {}
        async for stat in payroll_collection.aggregate(total_pipeline):
            overall_stats = {
                "total_records": stat["total_records"],
                "total_net_salary": round(stat["total_net_salary"], 2),
                "total_gross_salary": round(stat["total_gross_salary"], 2),
                "average_net_salary": round(stat["average_net_salary"], 2),
                "max_net_salary": round(stat["max_net_salary"], 2),
                "min_net_salary": round(stat["min_net_salary"], 2)
            }
        
        return {
            "success": True,
            "data": {
                "month": month,
                "overall": overall_stats,
                "by_status": status_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payroll summary: {str(e)}")
