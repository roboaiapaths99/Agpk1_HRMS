from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from models.employee_model import Employee, EmploymentType, EmployeeStatus, Department
from utils.helpers import create_pagination_params


class EmployeeRepository:
    """Repository for employee operations"""
    
    async def create_employee(self, employee_data, created_by: str = None) -> Employee:
        """Create a new employee"""
        employee = Employee(**employee_data.dict())
        if created_by:
            employee.created_by = created_by
        await employee.insert()
        return employee
    
    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            return await Employee.get(PydanticObjectId(employee_id))
        except:
            return None
    
    async def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        """Get employee by code"""
        return await Employee.find_one(Employee.employee_code == employee_code)
    
    async def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return await Employee.find_one(Employee.email == email)
    
    async def get_employee_by_phone(self, phone: str) -> Optional[Employee]:
        """Get employee by phone"""
        return await Employee.find_one(Employee.phone == phone)
    
    async def update_employee(self, employee_id: str, update_data, modified_by: str = None) -> Optional[Employee]:
        """Update employee details"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if modified_by:
            update_dict["last_modified_by"] = modified_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            if hasattr(employee, field):
                setattr(employee, field, value)
        
        await employee.save()
        return employee
    
    async def delete_employee(self, employee_id: str) -> bool:
        """Delete employee (soft delete)"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.status = EmployeeStatus.INACTIVE
        employee.is_active = False
        await employee.save()
        return True
    
    async def get_employees_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Employee], int]:
        """Get list of employees with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            query["$or"] = [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"employee_code": {"$regex": search, "$options": "i"}},
                {"department": {"$regex": search, "$options": "i"}}
            ]
        
        if department:
            query["department"] = department
        
        if status:
            try:
                query["status"] = EmployeeStatus(status)
            except ValueError:
                pass
        
        # Get total count
        total = await Employee.find(query).count()
        
        # Get employees with pagination and sorting
        employees = await Employee.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return employees, total
    
    async def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get employees by department"""
        return await Employee.find(Employee.department == department).sort(
            Employee.full_name, ASCENDING
        ).to_list()
    
    async def get_active_employees_count(self) -> int:
        """Get count of active employees"""
        return await Employee.find(Employee.is_active == True).count()
    
    async def get_employees_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """Get employees by status"""
        return await Employee.find(Employee.status == status).sort(
            Employee.created_at, DESCENDING
        ).to_list()
    
    async def search_employees(self, query: str, limit: int = 10) -> List[Employee]:
        """Search employees"""
        return await Employee.find(
            {"$or": [
                {"full_name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"employee_code": {"$regex": query, "$options": "i"}},
                {"department": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(limit).to_list()
    
    async def get_employees_created_between(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Employee]:
        """Get employees created between dates"""
        return await Employee.find({
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).sort(Employee.created_at, DESCENDING).to_list()
    
    async def get_employees_with_pending_documents(self) -> List[Employee]:
        """Get employees with pending documents"""
        return await Employee.find({
            "documents": {"$size": 0},
            "is_active": True
        }).sort(Employee.created_at, ASCENDING).to_list()
    
    async def get_employees_on_probation(self) -> List[Employee]:
        """Get employees on probation"""
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        return await Employee.find({
            "joining_date": {"$gte": three_months_ago},
            "is_active": True
        }).sort(Employee.joining_date, ASCENDING).to_list()
    
    async def get_upcoming_birthdays(self, days: int = 30) -> List[dict]:
        """Get upcoming birthdays"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        # Get all active employees
        employees = await Employee.find(Employee.is_active == True).to_list()
        
        upcoming_birthdays = []
        for employee in employees:
            if employee.date_of_birth:
                # Create birthday for current year
                current_year_birthday = employee.date_of_birth.replace(year=today.year)
                
                # Check if birthday is within the next N days
                if today <= current_year_birthday <= end_date:
                    days_until = (current_year_birthday - today).days
                    upcoming_birthdays.append({
                        "employee_id": str(employee.id),
                        "employee_code": employee.employee_code,
                        "full_name": employee.full_name,
                        "department": employee.department,
                        "date_of_birth": employee.date_of_birth,
                        "days_until_birthday": days_until
                    })
        
        # Sort by days until birthday
        upcoming_birthdays.sort(key=lambda x: x["days_until_birthday"])
        
        return upcoming_birthdays
    
    async def get_employee_statistics(self) -> dict:
        """Get employee statistics"""
        total_employees = await Employee.count()
        active_employees = await self.get_active_employees_count()
        
        # Department breakdown
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        dept_stats = await Employee.aggregate(dept_pipeline).to_list()
        
        # Status breakdown
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = await Employee.aggregate(status_pipeline).to_list()
        
        # Employment type breakdown
        type_pipeline = [
            {"$group": {"_id": "$employment_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_stats = await Employee.aggregate(type_pipeline).to_list()
        
        # Recent hires (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_hires = await Employee.find({
            "joining_date": {"$gte": thirty_days_ago}
        }).count()
        
        # Employees leaving this month
        current_month_start = datetime.utcnow().replace(day=1)
        leaving_this_month = await Employee.find({
            "last_working_day": {"$gte": current_month_start}
        }).count()
        
        # Gender distribution
        gender_pipeline = [
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        gender_stats = await Employee.aggregate(gender_pipeline).to_list()
        
        # Age distribution
        age_pipeline = [
            {"$group": {"_id": "$age_range", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        age_stats = await Employee.aggregate(age_pipeline).to_list()
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": total_employees - active_employees,
            "department_breakdown": dept_stats,
            "status_breakdown": status_stats,
            "employment_type_breakdown": type_stats,
            "recent_hires": recent_hires,
            "employees_leaving_this_month": leaving_this_month,
            "gender_distribution": gender_stats,
            "age_distribution": age_stats
        }
    
    async def bulk_update_employees(
        self, 
        employee_ids: List[str], 
        update_data: dict, 
        modified_by: str = None
    ) -> int:
        """Bulk update employees"""
        if modified_by:
            update_data["last_modified_by"] = modified_by
        update_data["updated_at"] = datetime.utcnow()
        
        result = await Employee.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in employee_ids]}}
        ).update({"$set": update_data})
        
        return result.modified_count
    
    async def get_employee_ids_by_department(self, department: str) -> List[str]:
        """Get employee IDs by department"""
        employees = await Employee.find(Employee.department == department).to_list()
        return [str(emp.id) for emp in employees]
    
    async def get_all_active_employee_ids(self) -> List[str]:
        """Get all active employee IDs"""
        employees = await Employee.find(Employee.is_active == True).to_list()
        return [str(emp.id) for emp in employees]
