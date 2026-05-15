from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from models.employee_model import Employee, EmploymentType, EmployeeStatus, Department
from schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeSearch, EmployeeStatusUpdate, EmployeeBulkAction
from repositories.employee_repo import EmployeeRepository
from utils.logger import audit_logger


class EmployeeService:
    """Service layer for employee operations"""
    
    def __init__(self):
        self.repository = EmployeeRepository()
    
    async def create_employee(self, employee_data: EmployeeCreate, created_by: str) -> Employee:
        """Create a new employee"""
        # Validate input data
        await self._validate_employee_data(employee_data)
        
        try:
            employee = await self.repository.create_employee(employee_data, created_by)
            
            # Log the action
            audit_logger.log_user_action(
                created_by, "employee_created", str(employee.id),
                f"Created employee {employee.employee_code}"
            )
            
            return employee
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create employee"
            )
    
    async def get_employee_by_id(self, employee_id: str) -> Employee:
        """Get employee by ID"""
        employee = await self.repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    
    async def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        """Get employee by code"""
        return await self.repository.get_employee_by_code(employee_code)
    
    async def update_employee(self, employee_id: str, update_data: EmployeeUpdate, modified_by: str = None) -> Employee:
        """Update employee details"""
        # Validate the employee exists
        existing_employee = await self.get_employee_by_id(employee_id)
        
        # Validate update data
        await self._validate_employee_update(update_data, existing_employee)
        
        try:
            updated_employee = await self.repository.update_employee(
                employee_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "employee_updated", employee_id,
                f"Updated employee {updated_employee.employee_code}"
            )
            
            return updated_employee
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update employee"
            )
    
    async def delete_employee(self, employee_id: str, deleted_by: str) -> bool:
        """Delete employee record"""
        employee = await self.get_employee_by_id(employee_id)
        
        try:
            success = await self.repository.delete_employee(employee_id)
            
            if success:
                # Log the action
                audit_logger.log_user_action(
                    deleted_by, "employee_deleted", employee_id,
                    f"Deleted employee {employee.employee_code}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete employee"
            )
    
    async def get_employees_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of employees"""
        try:
            employees, total = await self.repository.get_employees_list(
                page, page_size, search, department, status, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "employees": employees,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employees"
            )
    
    async def update_employee_status(self, employee_id: str, status: str, modified_by: str = None) -> Employee:
        """Update employee status"""
        try:
            new_status = EmployeeStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid employee status"
            )
        
        update_data = EmployeeUpdate(status=new_status)
        return await self.update_employee(employee_id, update_data, modified_by)
    
    async def bulk_action(self, bulk_action: EmployeeBulkAction, modified_by: str) -> Dict[str, Any]:
        """Perform bulk action on employees"""
        try:
            # Validate all employees exist
            for employee_id in bulk_action.employee_ids:
                await self.get_employee_by_id(employee_id)
            
            if bulk_action.action == "update_status":
                update_data = {"status": bulk_action.parameters.get("status")}
                updated_count = await self.repository.bulk_update_employees(
                    bulk_action.employee_ids, update_data, modified_by
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported bulk action: {bulk_action.action}"
                )
            
            # Log the action
            audit_logger.log_user_action(
                modified_by or "system", "bulk_employee_action", "",
                f"Bulk action {bulk_action.action} on {updated_count} employees"
            )
            
            return {
                "total_employees": len(bulk_action.employee_ids),
                "updated_count": updated_count,
                "failed_count": len(bulk_action.employee_ids) - updated_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform bulk action"
            )
    
    async def search_employees(self, query: str, limit: int = 10) -> List[Employee]:
        """Search employees"""
        try:
            return await self.repository.search_employees(query, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search employees"
            )
    
    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Get employee statistics"""
        try:
            return await self.repository.get_employee_statistics()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employee statistics"
            )
    
    async def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get employees by department"""
        try:
            return await self.repository.get_employees_by_department(department)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employees by department"
            )
    
    async def get_upcoming_birthdays(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming birthdays"""
        try:
            return await self.repository.get_upcoming_birthdays(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch upcoming birthdays"
            )
    
    async def _validate_employee_data(self, employee_data: EmployeeCreate):
        """Validate employee creation data"""
        # Date validation
        if employee_data.date_of_birth and employee_data.date_of_birth >= date.today():
            raise ValueError("Date of birth cannot be in the future")
        
        if employee_data.joining_date and employee_data.joining_date > date.today():
            raise ValueError("Joining date cannot be in the future")
        
        # Email validation
        if employee_data.email:
            existing_employee = await self.repository.get_employee_by_email(employee_data.email)
            if existing_employee:
                raise ValueError("Email already exists")
        
        # Phone validation
        if employee_data.phone:
            existing_employee = await self.repository.get_employee_by_phone(employee_data.phone)
            if existing_employee:
                raise ValueError("Phone number already exists")
        
        # Salary validation
        if employee_data.ctc <= 0:
            raise ValueError("CTC must be greater than 0")
    
    async def _validate_employee_update(self, update_data: EmployeeUpdate, existing_employee: Employee):
        """Validate employee update data"""
        # Email validation
        if update_data.email and update_data.email != existing_employee.email:
            existing_employee = await self.repository.get_employee_by_email(update_data.email)
            if existing_employee:
                raise ValueError("Email already exists")
        
        # Phone validation
        if update_data.phone and update_data.phone != existing_employee.phone:
            existing_employee = await self.repository.get_employee_by_phone(update_data.phone)
            if existing_employee:
                raise ValueError("Phone number already exists")
        
        # Status validation
        if update_data.status:
            try:
                EmployeeStatus(update_data.status)
            except ValueError:
                raise ValueError("Invalid employee status")
        
        # Department validation
        if update_data.department:
            try:
                Department(update_data.department)
            except ValueError:
                raise ValueError("Invalid department")
        
        # Employment type validation
        if update_data.employment_type:
            try:
                EmploymentType(update_data.employment_type)
            except ValueError:
                raise ValueError("Invalid employment type")
