from typing import Optional, List, Dict, Any
from datetime import datetime, date
from beanie import PydanticObjectId
from pymongo import DESCENDING

from .model import Employee, EmployeeStatus, Department, EmploymentType
from .schema import EmployeeCreate, EmployeeUpdate, EmployeeSearch
from utils.helpers import generate_employee_code, create_pagination_params


class EmployeeRepository:
    """Repository for employee operations"""
    
    async def create_employee(self, employee_data: EmployeeCreate, created_by: str) -> Employee:
        """Create a new employee"""
        # Generate employee code if not provided
        if not employee_data.employee_code:
            sequence_number = await self._get_next_sequence_number(employee_data.department)
            employee_data.employee_code = generate_employee_code(employee_data.department, sequence_number)
        
        # Check if employee code already exists
        existing_employee = await Employee.find_one(Employee.employee_code == employee_data.employee_code)
        if existing_employee:
            raise ValueError(f"Employee code {employee_data.employee_code} already exists")
        
        # Check if email already exists
        existing_email = await Employee.find_one(Employee.email == employee_data.email)
        if existing_email:
            raise ValueError(f"Email {employee_data.email} already exists")
        
        # Create employee document
        employee = Employee(
            **employee_data.dict(),
            created_by=created_by,
            last_modified_by=created_by
        )
        
        await employee.insert()
        return employee
    
    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            return await Employee.get(PydanticObjectId(employee_id))
        except:
            return None
    
    async def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        """Get employee by employee code"""
        return await Employee.find_one(Employee.employee_code == employee_code)
    
    async def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return await Employee.find_one(Employee.email == email)
    
    async def update_employee(self, employee_id: str, update_data: EmployeeUpdate, modified_by: str) -> Optional[Employee]:
        """Update employee details"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return None
        
        # Check if email is being updated and if it already exists
        if update_data.email and update_data.email != employee.email:
            existing_email = await Employee.find_one(Employee.email == update_data.email)
            if existing_email:
                raise ValueError(f"Email {update_data.email} already exists")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(employee, field, value)
        
        employee.updated_at = datetime.utcnow()
        employee.last_modified_by = modified_by
        
        await employee.save()
        return employee
    
    async def delete_employee(self, employee_id: str) -> bool:
        """Delete employee (soft delete by updating status)"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False
        
        employee.status = EmployeeStatus.TERMINATED
        employee.exit_date = date.today()
        employee.updated_at = datetime.utcnow()
        
        await employee.save()
        return True
    
    async def get_employees_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[EmployeeSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Employee], int]:
        """Get list of employees with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            if search.query:
                # Text search across multiple fields
                query["$or"] = [
                    {"first_name": {"$regex": search.query, "$options": "i"}},
                    {"last_name": {"$regex": search.query, "$options": "i"}},
                    {"email": {"$regex": search.query, "$options": "i"}},
                    {"employee_code": {"$regex": search.query, "$options": "i"}},
                    {"designation": {"$regex": search.query, "$options": "i"}}
                ]
            
            if search.department:
                query["department"] = search.department
            
            if search.employment_type:
                query["employment_type"] = search.employment_type
            
            if search.status:
                query["status"] = search.status
            
            if search.min_salary is not None:
                query["base_salary"] = {"$gte": search.min_salary}
            
            if search.max_salary is not None:
                if "base_salary" in query:
                    query["base_salary"]["$lte"] = search.max_salary
                else:
                    query["base_salary"] = {"$lte": search.max_salary}
            
            if search.joining_date_from:
                if "joining_date" in query:
                    query["joining_date"]["$gte"] = search.joining_date_from
                else:
                    query["joining_date"] = {"$gte": search.joining_date_from}
            
            if search.joining_date_to:
                if "joining_date" in query:
                    query["joining_date"]["$lte"] = search.joining_date_to
                else:
                    query["joining_date"] = {"$lte": search.joining_date_to}
        
        # Get total count
        total = await Employee.find(query).count()
        
        # Get employees with pagination and sorting
        employees = await Employee.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return employees, total
    
    async def get_active_employees_count(self) -> int:
        """Get count of active employees"""
        return await Employee.find(Employee.status == EmployeeStatus.ACTIVE).count()
    
    async def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get employees by department"""
        return await Employee.find(
            Employee.department == department
        ).sort(Employee.first_name, Employee.last_name).to_list()
    
    async def get_employees_by_manager(self, manager_code: str) -> List[Employee]:
        """Get employees reporting to a specific manager"""
        return await Employee.find(
            Employee.reporting_manager == manager_code
        ).sort(Employee.first_name, Employee.last_name).to_list()
    
    async def update_employee_status(
        self,
        employee_id: str,
        new_status: EmployeeStatus,
        reason: Optional[str] = None,
        modified_by: str = None
    ) -> Optional[Employee]:
        """Update employee status"""
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return None
        
        await employee.update_status(new_status, reason)
        
        if modified_by:
            employee.last_modified_by = modified_by
            await employee.save()
        
        return employee
    
    async def get_employees_joining_soon(self, days: int = 7) -> List[Employee]:
        """Get employees joining in the next N days"""
        today = date.today()
        future_date = today + datetime.timedelta(days=days)
        
        return await Employee.find({
            "joining_date": {
                "$gte": today,
                "$lte": future_date
            },
            "status": {"$ne": EmployeeStatus.TERMINATED}
        }).sort(Employee.joining_date).to_list()
    
    async def get_employees_on_probation(self) -> List[Employee]:
        """Get employees currently on probation"""
        today = date.today()
        
        return await Employee.find({
            "probation_end_date": {"$gte": today},
            "status": EmployeeStatus.ACTIVE
        }).sort(Employee.probation_end_date).to_list()
    
    async def get_employees_completing_probation_soon(self, days: int = 30) -> List[Employee]:
        """Get employees completing probation soon"""
        today = date.today()
        future_date = today + datetime.timedelta(days=days)
        
        return await Employee.find({
            "probation_end_date": {
                "$gte": today,
                "$lte": future_date
            },
            "status": EmployeeStatus.ACTIVE
        }).sort(Employee.probation_end_date).to_list()
    
    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Get employee statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1},
                    "active": {
                        "$sum": {"$cond": [{"$eq": ["$status", EmployeeStatus.ACTIVE]}, 1, 0]}
                    }
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        dept_stats = await Employee.aggregate(pipeline).to_list()
        
        # Employment type statistics
        emp_type_pipeline = [
            {
                "$group": {
                    "_id": "$employment_type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        emp_type_stats = await Employee.aggregate(emp_type_pipeline).to_list()
        
        # Overall statistics
        total_employees = await Employee.count()
        active_employees = await Employee.find(Employee.status == EmployeeStatus.ACTIVE).count()
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": total_employees - active_employees,
            "department_statistics": dept_stats,
            "employment_type_statistics": emp_type_stats
        }
    
    async def bulk_update_employees(
        self,
        employee_ids: List[str],
        update_data: Dict[str, Any],
        modified_by: str
    ) -> int:
        """Bulk update employees"""
        result = await Employee.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in employee_ids]}}
        ).update(
            {"$set": {**update_data, "updated_at": datetime.utcnow(), "last_modified_by": modified_by}}
        )
        
        return result.modified_count
    
    async def search_employees_full_text(self, query: str, limit: int = 10) -> List[Employee]:
        """Full text search across employee documents"""
        return await Employee.find(
            {"$text": {"$search": query}}
        ).limit(limit).to_list()
    
    async def get_employees_with_upcoming_birthdays(self, days: int = 30) -> List[Employee]:
        """Get employees with upcoming birthdays"""
        today = date.today()
        future_date = today + datetime.timedelta(days=days)
        
        # This is a simplified approach - in production, you might want to store
        # month and day separately for better querying
        employees = await Employee.find(
            {
                "date_of_birth": {"$ne": None},
                "status": EmployeeStatus.ACTIVE
            }
        ).to_list()
        
        upcoming_birthdays = []
        for emp in employees:
            if emp.date_of_birth:
                # Create birthday for current year
                birthday_this_year = date(today.year, emp.date_of_birth.month, emp.date_of_birth.day)
                birthday_next_year = date(today.year + 1, emp.date_of_birth.month, emp.date_of_birth.day)
                
                if today <= birthday_this_year <= future_date:
                    upcoming_birthdays.append(emp)
                elif birthday_this_year < today and today <= birthday_next_year <= future_date:
                    upcoming_birthdays.append(emp)
        
        return upcoming_birthdays
    
    async def _get_next_sequence_number(self, department: str) -> int:
        """Get next sequence number for employee code generation"""
        # Find the highest sequence number for the department
        dept_code = department.lower()[:3].upper()
        
        pipeline = [
            {"$match": {"employee_code": {"$regex": f"^{dept_code}"}}},
            {"$project": {"sequence": {"$toInt": {"$substr": ["$employee_code", 3, 4]}}}},
            {"$sort": {"sequence": -1}},
            {"$limit": 1}
        ]
        
        result = await Employee.aggregate(pipeline).to_list()
        
        if result:
            return result[0]["sequence"] + 1
        else:
            return 1
