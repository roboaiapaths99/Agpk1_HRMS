from typing import Optional, List, Dict, Any
from datetime import datetime, date
from fastapi import HTTPException, status

from .model import Employee, EmployeeStatus
from .schema import EmployeeCreate, EmployeeUpdate, EmployeeSearch, EmployeeStatusUpdate
from .repository import EmployeeRepository
from utils.helpers import validate_email, validate_phone, validate_pan, validate_aadhaar
from utils.logger import audit_logger


class EmployeeService:
    """Service layer for employee operations"""
    
    def __init__(self):
        self.repository = EmployeeRepository()
    
    async def create_employee(self, employee_data: EmployeeCreate, created_by: str) -> Employee:
        """Create a new employee with validation"""
        # Validate input data
        await self._validate_employee_data(employee_data)
        
        try:
            employee = await self.repository.create_employee(employee_data, created_by)
            
            # Log the action
            audit_logger.log_employee_action(
                created_by, "created", str(employee.id), 
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
    
    async def get_employee(self, employee_id: str) -> Employee:
        """Get employee by ID"""
        employee = await self.repository.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    
    async def get_employee_by_code(self, employee_code: str) -> Employee:
        """Get employee by code"""
        employee = await self.repository.get_employee_by_code(employee_code)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    
    async def update_employee(
        self, 
        employee_id: str, 
        update_data: EmployeeUpdate, 
        modified_by: str
    ) -> Employee:
        """Update employee with validation"""
        # Validate the employee exists
        existing_employee = await self.get_employee(employee_id)
        
        # Validate update data
        await self._validate_employee_update(update_data, existing_employee)
        
        try:
            updated_employee = await self.repository.update_employee(
                employee_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                modified_by, "updated", employee_id,
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
        """Delete employee (soft delete)"""
        employee = await self.get_employee(employee_id)
        
        try:
            success = await self.repository.delete_employee(employee_id)
            
            if success:
                # Log the action
                audit_logger.log_employee_action(
                    deleted_by, "deleted", employee_id,
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
        search: Optional[EmployeeSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of employees"""
        try:
            employees, total = await self.repository.get_employees_list(
                page, page_size, search, sort_by, sort_order
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
    
    async def update_employee_status(
        self,
        employee_id: str,
        status_update: EmployeeStatusUpdate,
        modified_by: str
    ) -> Employee:
        """Update employee status"""
        employee = await self.get_employee(employee_id)
        
        try:
            # Validate status
            try:
                new_status = EmployeeStatus(status_update.status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status value"
                )
            
            updated_employee = await self.repository.update_employee_status(
                employee_id, new_status, status_update.reason, modified_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                modified_by, "status_updated", employee_id,
                f"Status changed to {status_update.status} for employee {employee.employee_code}"
            )
            
            return updated_employee
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update employee status"
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
    
    async def get_employees_by_manager(self, manager_code: str) -> List[Employee]:
        """Get employees reporting to a manager"""
        try:
            return await self.repository.get_employees_by_manager(manager_code)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employees by manager"
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
    
    async def get_active_employees_count(self) -> int:
        """Get count of active employees"""
        try:
            return await self.repository.get_active_employees_count()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch active employees count"
            )
    
    async def get_employees_joining_soon(self, days: int = 7) -> List[Employee]:
        """Get employees joining in the next N days"""
        try:
            return await self.repository.get_employees_joining_soon(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch upcoming joiners"
            )
    
    async def get_employees_on_probation(self) -> List[Employee]:
        """Get employees currently on probation"""
        try:
            return await self.repository.get_employees_on_probation()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employees on probation"
            )
    
    async def bulk_update_employees(
        self,
        employee_ids: List[str],
        update_data: Dict[str, Any],
        modified_by: str
    ) -> int:
        """Bulk update employees"""
        try:
            # Validate that all employees exist
            for emp_id in employee_ids:
                await self.get_employee(emp_id)
            
            updated_count = await self.repository.bulk_update_employees(
                employee_ids, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_employee_action(
                modified_by, "bulk_updated", "",
                f"Bulk updated {updated_count} employees"
            )
            
            return updated_count
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk update employees"
            )
    
    async def search_employees(self, query: str, limit: int = 10) -> List[Employee]:
        """Search employees"""
        try:
            return await self.repository.search_employees_full_text(query, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search employees"
            )
    
    async def get_employees_with_upcoming_birthdays(self, days: int = 30) -> List[Employee]:
        """Get employees with upcoming birthdays"""
        try:
            return await self.repository.get_employees_with_upcoming_birthdays(days)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch upcoming birthdays"
            )
    
    async def _validate_employee_data(self, employee_data: EmployeeCreate):
        """Validate employee creation data"""
        # Email validation
        if not validate_email(employee_data.email):
            raise ValueError("Invalid email format")
        
        # Phone validation (if provided)
        if employee_data.phone and not validate_phone(employee_data.phone):
            raise ValueError("Invalid phone number format")
        
        # PAN validation (if provided)
        if employee_data.pan_number and not validate_pan(employee_data.pan_number):
            raise ValueError("Invalid PAN number format")
        
        # Aadhaar validation (if provided)
        if employee_data.aadhaar_number and not validate_aadhaar(employee_data.aadhaar_number):
            raise ValueError("Invalid Aadhaar number format")
        
        # Date validation
        if employee_data.joining_date > date.today():
            raise ValueError("Joining date cannot be in the future")
        
        if employee_data.probation_end_date and employee_data.probation_end_date <= employee_data.joining_date:
            raise ValueError("Probation end date must be after joining date")
        
        if employee_data.confirmation_date and employee_data.confirmation_date < employee_data.joining_date:
            raise ValueError("Confirmation date must be after joining date")
        
        # Salary validation
        if employee_data.variable_pay and employee_data.variable_pay > employee_data.base_salary:
            raise ValueError("Variable pay cannot exceed base salary")
    
    async def _validate_employee_update(self, update_data: EmployeeUpdate, existing_employee: Employee):
        """Validate employee update data"""
        # Email validation (if being updated)
        if update_data.email and not validate_email(update_data.email):
            raise ValueError("Invalid email format")
        
        # Phone validation (if being updated)
        if update_data.phone and not validate_phone(update_data.phone):
            raise ValueError("Invalid phone number format")
        
        # PAN validation (if being updated)
        if update_data.pan_number and not validate_pan(update_data.pan_number):
            raise ValueError("Invalid PAN number format")
        
        # Aadhaar validation (if being updated)
        if update_data.aadhaar_number and not validate_aadhaar(update_data.aadhaar_number):
            raise ValueError("Invalid Aadhaar number format")
        
        # Date validations (if being updated)
        if update_data.probation_end_date and update_data.probation_end_date <= existing_employee.joining_date:
            raise ValueError("Probation end date must be after joining date")
        
        if update_data.confirmation_date and update_data.confirmation_date < existing_employee.joining_date:
            raise ValueError("Confirmation date must be after joining date")
        
        # Salary validation (if being updated)
        if (update_data.variable_pay is not None and 
            update_data.base_salary is not None and 
            update_data.variable_pay > update_data.base_salary):
            raise ValueError("Variable pay cannot exceed base salary")
        
        if (update_data.variable_pay is not None and 
            update_data.base_salary is None and 
            update_data.variable_pay > existing_employee.base_salary):
            raise ValueError("Variable pay cannot exceed base salary")
