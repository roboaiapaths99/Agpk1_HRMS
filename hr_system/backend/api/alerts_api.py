"""
Alerts API Module
Manages system alerts and notifications
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from core.database import Database
from core.config import settings

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/")
async def get_alerts(
    status: Optional[str] = Query(None, description="active, resolved, dismissed"),
    type: Optional[str] = Query(None, description="attendance, payroll, system, security"),
    severity: Optional[str] = Query(None, description="low, medium, high, critical"),
    skip: int = 0,
    limit: int = 50,
    org_id: Optional[str] = None
):
    """Get all alerts with optional filters"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        # Build filter
        filter_query = {}
        if status:
            filter_query["status"] = status
        if type:
            filter_query["type"] = type
        if severity:
            filter_query["severity"] = severity
        if org_id:
            filter_query["org_id"] = org_id
        
        # Get alerts
        alerts = []
        cursor = alerts_collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        
        async for alert in cursor:
            alert['_id'] = str(alert['_id'])
            alerts.append(alert)
        
        # Get total count
        total = await alerts_collection.count_documents(filter_query)
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total": total
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.post("/")
async def create_alert(alert_data: dict):
    """Create a new alert"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        # Prepare alert document
        alert_doc = {
            "_id": str(uuid.uuid4()),
            "title": alert_data.get("title"),
            "message": alert_data.get("message"),
            "type": alert_data.get("type", "system"),
            "severity": alert_data.get("severity", "medium"),
            "status": "active",
            "source": alert_data.get("source", "system"),
            "employee_id": alert_data.get("employee_id"),
            "org_id": alert_data.get("org_id", "test_org_123"),
            "metadata": alert_data.get("metadata", {}),
            "created_by": current_user.get("email", "system"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert alert
        result = await alerts_collection.insert_one(alert_doc)
        
        if result.inserted_id:
            alert_doc['_id'] = str(alert_doc['_id'])
            return {
                "success": True,
                "data": alert_doc,
                "message": "Alert created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create alert")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.patch("/{alert_id}")
async def update_alert(
    alert_id: str,
    update_data: dict
):
    """Update alert status or other fields"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        # Check if alert exists
        existing = await alerts_collection.find_one({"_id": alert_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Prepare update data
        allowed_fields = ["status", "severity", "message", "metadata"]
        update_fields = {}
        
        for field in allowed_fields:
            if field in update_data:
                update_fields[field] = update_data[field]
        
        update_fields["updated_at"] = datetime.utcnow()
        update_fields["updated_by"] = current_user.get("email", "system")
        
        # Add resolution details if status is being changed to resolved/dismissed
        new_status = update_data.get("status")
        if new_status in ["resolved", "dismissed"]:
            update_fields["resolved_at"] = datetime.utcnow()
            update_fields["resolved_by"] = current_user.get("email", "system")
            if "resolution_note" in update_data:
                update_fields["resolution_note"] = update_data["resolution_note"]
        
        # Update alert
        result = await alerts_collection.update_one(
            {"_id": alert_id},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            # Get updated alert
            updated_alert = await alerts_collection.find_one({"_id": alert_id})
            updated_alert['_id'] = str(updated_alert['_id'])
            
            return {
                "success": True,
                "data": updated_alert,
                "message": "Alert updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="No changes made")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        # Check if alert exists
        existing = await alerts_collection.find_one({"_id": alert_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Delete alert
        result = await alerts_collection.delete_one({"_id": alert_id})
        
        if result.deleted_count > 0:
            return {
                "success": True,
                "message": "Alert deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete alert")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

@router.get("/stats/summary")
async def get_alerts_summary(org_id: Optional[str] = None):
    """Get alerts summary statistics"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        # Build filter
        filter_query = {}
        if org_id:
            filter_query["org_id"] = org_id
        
        # Get alerts by status
        status_pipeline = [
            {"$match": filter_query},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_stats = {}
        async for stat in alerts_collection.aggregate(status_pipeline):
            status_stats[stat["_id"]] = stat["count"]
        
        # Get alerts by type
        type_pipeline = [
            {"$match": filter_query},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        
        type_stats = {}
        async for stat in alerts_collection.aggregate(type_pipeline):
            type_stats[stat["_id"]] = stat["count"]
        
        # Get alerts by severity
        severity_pipeline = [
            {"$match": filter_query},
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        
        severity_stats = {}
        async for stat in alerts_collection.aggregate(severity_pipeline):
            severity_stats[stat["_id"]] = stat["count"]
        
        # Get recent alerts (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = await alerts_collection.count_documents({
            **filter_query,
            "created_at": {"$gte": seven_days_ago}
        })
        
        # Get critical alerts
        critical_count = await alerts_collection.count_documents({
            **filter_query,
            "severity": "critical",
            "status": "active"
        })
        
        return {
            "success": True,
            "data": {
                "total_alerts": sum(status_stats.values()),
                "active_alerts": status_stats.get("active", 0),
                "resolved_alerts": status_stats.get("resolved", 0),
                "dismissed_alerts": status_stats.get("dismissed", 0),
                "recent_alerts": recent_count,
                "critical_alerts": critical_count,
                "by_status": status_stats,
                "by_type": type_stats,
                "by_severity": severity_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts summary: {str(e)}")

async def create_attendance_alert(employee_id: str, employee_name: str, alert_type: str, org_id: str = None):
    """Helper function to create attendance-related alerts"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        if alert_type == "absent":
            alert_data = {
                "title": "Employee Absent",
                "message": f"{employee_name} was absent today",
                "type": "attendance",
                "severity": "medium",
                "employee_id": employee_id,
                "org_id": org_id
            }
        elif alert_type == "late":
            alert_data = {
                "title": "Late Check-in",
                "message": f"{employee_name} checked in late today",
                "type": "attendance",
                "severity": "low",
                "employee_id": employee_id,
                "org_id": org_id
            }
        else:
            return
        
        # Check if similar alert already exists today
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        existing = await alerts_collection.find_one({
            "employee_id": employee_id,
            "type": "attendance",
            "title": alert_data["title"],
            "created_at": {"$gte": start_of_day, "$lte": end_of_day}
        })
        
        if not existing:
            alert_doc = {
                "_id": str(uuid.uuid4()),
                **alert_data,
                "status": "active",
                "source": "attendance_system",
                "metadata": {"auto_generated": True},
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await alerts_collection.insert_one(alert_doc)
            
    except Exception as e:
        print(f"Failed to create attendance alert: {e}")

async def create_payroll_alert(employee_id: str, employee_name: str, alert_type: str, org_id: str = None):
    """Helper function to create payroll-related alerts"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        
        if alert_type == "high_deduction":
            alert_data = {
                "title": "High Payroll Deduction",
                "message": f"{employee_name} has high deductions this month",
                "type": "payroll",
                "severity": "medium",
                "employee_id": employee_id,
                "org_id": org_id
            }
        elif alert_type == "negative_salary":
            alert_data = {
                "title": "Negative Net Salary",
                "message": f"{employee_name} has negative net salary - review required",
                "type": "payroll",
                "severity": "high",
                "employee_id": employee_id,
                "org_id": org_id
            }
        else:
            return
        
        alert_doc = {
            "_id": str(uuid.uuid4()),
            **alert_data,
            "status": "active",
            "source": "payroll_system",
            "metadata": {"auto_generated": True},
            "created_by": "system",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await alerts_collection.insert_one(alert_doc)
        
    except Exception as e:
        print(f"Failed to create payroll alert: {e}")

@router.post("/generate-system-alerts")
async def generate_system_alerts(org_id: Optional[str] = None):
    """Generate system alerts based on current data"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        alerts_collection = database.alerts
        employees_collection = database.employees
        attendance_collection = database.attendance_logs
        payroll_collection = database.payrolls
        
        generated_alerts = []
        
        # Check for absent employees today
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        # Get all active employees
        org_filter = {}
        if org_id:
            org_filter["org_id"] = org_id
        
        employees = []
        async for emp in employees_collection.find({"isActive": True, **org_filter}):
            emp['_id'] = str(emp['_id'])
            employees.append(emp)
        
        # Check attendance for each employee
        for emp in employees:
            # Check if employee checked in today
            checkin = await attendance_collection.find_one({
                "user_id": emp['_id'],
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
                "type": "check-in"
            })
            
            if not checkin:
                # Create absent alert
                await create_attendance_alert(emp['_id'], f"{emp.get('firstName', '')} {emp.get('lastName', '')}", "absent", org_id)
                generated_alerts.append(f"Absent alert created for {emp.get('firstName', '')} {emp.get('lastName', '')}")
        
        # Check payroll issues for current month
        current_month = datetime.now().strftime("%Y-%m")
        payroll_filter = {"month": current_month}
        if org_id:
            payroll_filter["org_id"] = org_id
        
        async for payroll in payroll_collection.find(payroll_filter):
            if payroll["net_salary"] < 0:
                # Create negative salary alert
                employee_name = payroll.get("employee_name", "Unknown")
                await create_payroll_alert(payroll["employee_id"], employee_name, "negative_salary", org_id)
                generated_alerts.append(f"Negative salary alert created for {employee_name}")
            
            elif payroll["total_deductions"] > (payroll["gross_earnings"] * 0.3):  # More than 30% deductions
                employee_name = payroll.get("employee_name", "Unknown")
                await create_payroll_alert(payroll["employee_id"], employee_name, "high_deduction", org_id)
                generated_alerts.append(f"High deduction alert created for {employee_name}")
        
        return {
            "success": True,
            "data": {
                "generated_alerts_count": len(generated_alerts),
                "generated_alerts": generated_alerts
            },
            "message": f"Generated {len(generated_alerts)} system alerts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate system alerts: {str(e)}")
