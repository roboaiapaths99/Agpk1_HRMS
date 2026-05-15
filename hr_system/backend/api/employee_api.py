"""
Employee API Module
Handles all employee-related operations for HRMS
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from core.database import Database
from core.config import settings

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/")
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all employees with optional filters"""
    try:
        # Direct database connection
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client.lmsfull
        employees_collection = database.employees
        
        print(f"Fetching employees from database...")
        
        # Build filter
        filter_query = {}
        if department:
            filter_query["department"] = department
        if status:
            filter_query["status"] = status
        
        # Get employees
        employees = await employees_collection.find(filter_query).skip(skip).limit(limit).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        for employee in employees:
            if "_id" in employee:
                employee["_id"] = str(employee["_id"])
        
        print(f"Found {len(employees)} employees")
        
        return {
            "success": True,
            "employees": employees,
            "total": len(employees),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return {
            "success": False,
            "error": str(e),
            "employees": [],
            "total": 0
        }
    finally:
        if 'client' in locals():
            client.close()

@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    """Get a specific employee by ID"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        employee = await employees_collection.find_one({"_id": employee_id})
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee['_id'] = str(employee['_id'])
        
        return {
            "success": True,
            "data": employee
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee: {str(e)}")

@router.post("/")
async def create_employee(employee_data: dict):
    """Create a new employee"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        # Check if employee with same email exists
        existing = await employees_collection.find_one({"email": employee_data.get("email")})
        if existing:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
        
        # Prepare employee document
        employee_doc = {
            "_id": str(uuid.uuid4()),
            "employeeCode": employee_data.get("employeeCode", f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "firstName": employee_data.get("firstName"),
            "lastName": employee_data.get("lastName"),
            "email": employee_data.get("email"),
            "phone": employee_data.get("phone", ""),
            "department": employee_data.get("department"),
            "designation": employee_data.get("designation"),
            "monthlySalary": employee_data.get("monthlySalary", 0),
            "payrollType": employee_data.get("payrollType", "monthly"),
            "joiningDate": employee_data.get("joiningDate", datetime.utcnow()),
            "status": employee_data.get("status", "active"),
            "isActive": employee_data.get("isActive", True),
            "organizationId": employee_data.get("organizationId", "test_org_123"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            # HRMS specific fields
            "employeeType": employee_data.get("employeeType", "regular"),
            "workLocation": employee_data.get("workLocation", "office"),
            "reportingManager": employee_data.get("reportingManager", ""),
            "skills": employee_data.get("skills", []),
            "emergencyContact": employee_data.get("emergencyContact", {}),
            "bankDetails": employee_data.get("bankDetails", {}),
            "documents": employee_data.get("documents", [])
        }
        
        # Insert employee
        result = await employees_collection.insert_one(employee_doc)
        
        if result.inserted_id:
            employee_doc['_id'] = str(employee_doc['_id'])
            return {
                "success": True,
                "data": employee_doc,
                "message": "Employee created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create employee")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@router.put("/{employee_id}")
async def update_employee(employee_id: str, employee_data: dict):
    """Update an existing employee"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        # Check if employee exists
        existing = await employees_collection.find_one({"_id": employee_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Prepare update data
        update_data = {
            "firstName": employee_data.get("firstName", existing.get("firstName")),
            "lastName": employee_data.get("lastName", existing.get("lastName")),
            "email": employee_data.get("email", existing.get("email")),
            "phone": employee_data.get("phone", existing.get("phone")),
            "department": employee_data.get("department", existing.get("department")),
            "designation": employee_data.get("designation", existing.get("designation")),
            "monthlySalary": employee_data.get("monthlySalary", existing.get("monthlySalary", 0)),
            "payrollType": employee_data.get("payrollType", existing.get("payrollType")),
            "status": employee_data.get("status", existing.get("status")),
            "isActive": employee_data.get("isActive", existing.get("isActive")),
            "updated_at": datetime.utcnow(),
            # Update other HRMS fields if provided
            "workLocation": employee_data.get("workLocation", existing.get("workLocation")),
            "reportingManager": employee_data.get("reportingManager", existing.get("reportingManager")),
            "skills": employee_data.get("skills", existing.get("skills")),
            "emergencyContact": employee_data.get("emergencyContact", existing.get("emergencyContact")),
            "bankDetails": employee_data.get("bankDetails", existing.get("bankDetails"))
        }
        
        # Update employee
        result = await employees_collection.update_one(
            {"_id": employee_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Get updated employee
            updated_employee = await employees_collection.find_one({"_id": employee_id})
            updated_employee['_id'] = str(updated_employee['_id'])
            
            return {
                "success": True,
                "data": updated_employee,
                "message": "Employee updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="No changes made")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")

@router.delete("/{employee_id}")
async def delete_employee(employee_id: str):
    """Delete an employee"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        # Check if employee exists
        existing = await employees_collection.find_one({"_id": employee_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Soft delete - mark as inactive
        result = await employees_collection.update_one(
            {"_id": employee_id},
            {"$set": {
                "status": "inactive",
                "isActive": False,
                "deleted_at": datetime.utcnow(),
                "deleted_by": "system"
            }}
        )
        
        if result.modified_count > 0:
            return {
                "success": True,
                "message": "Employee deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete employee")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {str(e)}")

@router.get("/stats/overview")
async def get_employee_stats():
    """Get employee overview statistics"""
    try:
        database = Database.client[settings.DATABASE_NAME]
        employees_collection = database.employees
        
        # Get total employees
        total_employees = await employees_collection.count_documents({"isActive": True})
        
        # Get employees by department
        dept_pipeline = [
            {"$match": {"isActive": True}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        department_stats = []
        async for dept in employees_collection.aggregate(dept_pipeline):
            department_stats.append({
                "department": dept["_id"] or "Unassigned",
                "count": dept["count"]
            })
        
        # Get employees by status
        status_pipeline = [
            {"$match": {"isActive": True}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_stats = {}
        async for status in employees_collection.aggregate(status_pipeline):
            status_stats[status["_id"]] = status["count"]
        
        return {
            "success": True,
            "data": {
                "total_employees": total_employees,
                "by_department": department_stats,
                "by_status": status_stats,
                "active_employees": status_stats.get("active", 0),
                "inactive_employees": status_stats.get("inactive", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee stats: {str(e)}")
