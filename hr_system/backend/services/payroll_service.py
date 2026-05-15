from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from repositories.payroll_repo import PayrollRepository
from repositories.employee_repo import EmployeeRepository
from repositories.attendance_repo import AttendanceRepository
from models.payroll_model import Payroll, PayrollStatus, PaymentMethod
from utils.logger import audit_logger
from utils.helpers import calculate_ctc_components, generate_payroll_month_year, parse_payroll_month
import logging

logger = logging.getLogger(__name__)


class PayrollService:
    """Service class for payroll operations"""
    
    def __init__(self):
        self.payroll_repo = PayrollRepository()
        self.employee_repo = EmployeeRepository()
        self.attendance_repo = AttendanceRepository()
    
    async def create_payroll(
        self, 
        payroll_data: Dict[str, Any],
        created_by: str
    ) -> Payroll:
        """Create a new payroll record"""
        try:
            # Get employee information
            employee = await self.employee_repo.get_employee_by_id(payroll_data["employee_id"])
            if not employee:
                raise ValueError(f"Employee {payroll_data['employee_id']} not found")
            
            # Get attendance data for the payroll month
            attendance_summary = await self.attendance_repo.get_attendance_summary(
                payroll_data["employee_id"],
                payroll_data["payroll_month"]
            )
            
            # Calculate payroll based on real attendance
            payroll = await self._calculate_payroll_from_attendance(
                employee, attendance_summary, payroll_data, created_by
            )
            
            # Save payroll
            created_payroll = await self.payroll_repo.create_payroll(payroll)
            
            # Log the action
            audit_logger.log_payroll_action(
                created_by,
                "create",
                created_payroll.employee_code,
                f"Created payroll for {payroll_data['payroll_month']}"
            )
            
            logger.info(f"Created payroll for employee {payroll_data['employee_id']}")
            return created_payroll
            
        except Exception as e:
            logger.error(f"Error creating payroll: {e}")
            raise
    
    async def _calculate_payroll_from_attendance(
        self,
        employee: Dict[str, Any],
        attendance_summary: Dict[str, Any],
        payroll_data: Dict[str, Any],
        created_by: str
    ) -> Payroll:
        """Calculate payroll based on real attendance data"""
        
        # Get salary components
        ctc = employee.get("ctc", 0)
        monthly_salary = ctc / 12
        daily_wages = monthly_salary / 30
        
        # Calculate based on actual attendance
        present_days = attendance_summary.get("present_days", 0)
        leave_days = attendance_summary.get("leave_days", 0)
        holidays = attendance_summary.get("holidays", 0)
        total_work_days = attendance_summary.get("total_days", 22)
        
        # Calculate attendance salary
        attendance_salary = daily_wages * present_days
        
        # Add leave encashment if applicable
        leave_encashment = 0
        if leave_days > 0 and employee.get("leave_encashment_allowed", False):
            leave_encashment = daily_wages * leave_days
        
        # Calculate overtime
        overtime_hours = payroll_data.get("overtime_hours", 0)
        overtime_rate = payroll_data.get("overtime_rate", 1.5)
        overtime_amount = overtime_hours * daily_wages * 8 * overtime_rate  # 8 hours per day
        
        # Calculate gross salary
        bonus = payroll_data.get("bonus", 0)
        other_earnings = payroll_data.get("other_earnings", 0)
        gross_salary = attendance_salary + leave_encashment + overtime_amount + bonus + other_earnings
        
        # Calculate statutory deductions
        pf_employee = min(attendance_salary * 0.12, 15000)  # PF capped at 15000
        pf_employer = pf_employee
        esi_employee = min(gross_salary * 0.0075, 7500)  # ESI capped
        esi_employer = gross_salary * 0.0325
        professional_tax = self._calculate_professional_tax(gross_salary)
        
        # Calculate income tax (simplified)
        income_tax = self._calculate_income_tax(gross_salary, pf_employee)
        
        # Other deductions
        loan_deductions = payroll_data.get("loan_deductions", 0)
        advance_deductions = payroll_data.get("advance_deductions", 0)
        other_deductions = payroll_data.get("other_deductions", 0)
        
        total_deductions = (
            pf_employee + esi_employee + professional_tax + income_tax +
            loan_deductions + advance_deductions + other_deductions
        )
        
        net_salary = gross_salary - total_deductions
        
        # Create payroll object
        payroll = Payroll(
            employee_id=employee["employee_code"],
            employee_code=employee["employee_code"],
            employee_name=employee["full_name"],
            department=employee["department"],
            designation=employee["designation"],
            payroll_month=payroll_data["payroll_month"],
            from_date=payroll_data.get("from_date"),
            to_date=payroll_data.get("to_date"),
            working_days=total_work_days,
            present_days=present_days,
            absent_days=attendance_summary.get("absent_days", 0),
            leave_days=leave_days,
            holidays=holidays,
            base_salary=monthly_salary,
            attendance_salary=attendance_salary,
            overtime_hours=overtime_hours,
            overtime_rate=overtime_rate,
            overtime_amount=overtime_amount,
            bonus=bonus,
            other_earnings=other_earnings + leave_encashment,
            gross_salary=gross_salary,
            pf_employee=pf_employee,
            pf_employer=pf_employer,
            esi_employee=esi_employee,
            esi_employer=esi_employer,
            professional_tax=professional_tax,
            income_tax=income_tax,
            loan_deductions=loan_deductions,
            advance_deductions=advance_deductions,
            other_deductions=other_deductions,
            total_deductions=total_deductions,
            net_salary=net_salary,
            payment_method=PaymentMethod(payroll_data.get("payment_method", "bank_transfer")),
            bank_account=employee.get("bank_account", ""),
            created_by=created_by
        )
        
        return payroll
    
    def _calculate_professional_tax(self, gross_salary: float) -> float:
        """Calculate professional tax based on salary slab"""
        if gross_salary <= 10000:
            return 0
        elif gross_salary <= 20000:
            return 200
        elif gross_salary <= 30000:
            return 400
        else:
            return 600
    
    def _calculate_income_tax(self, gross_salary: float, pf_deduction: float) -> float:
        """Calculate income tax (simplified calculation)"""
        # This is a simplified TDS calculation
        taxable_income = gross_salary - pf_deduction - 50000  # Standard deduction
        
        if taxable_income <= 250000:
            return 0
        elif taxable_income <= 500000:
            return (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            return 12500 + (taxable_income - 500000) * 0.2
        else:
            return 112500 + (taxable_income - 1000000) * 0.3
    
    async def get_payroll_by_id(self, payroll_id: str) -> Payroll:
        """Get payroll by ID"""
        payroll = await self.payroll_repo.get_payroll_by_id(payroll_id)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll not found"
            )
        return payroll
    
    async def get_payroll_by_employee_month(self, employee_id: str, payroll_month: str) -> Payroll:
        """Get payroll by employee and month"""
        payroll = await self.payroll_repo.get_payroll_by_employee_month(employee_id, payroll_month)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll not found for this employee and month"
            )
        return payroll
    
    async def update_payroll(
        self, 
        payroll_id: str, 
        update_data: Dict[str, Any], 
        modified_by: str = None
    ) -> Payroll:
        """Update payroll details"""
        # Validate the payroll exists
        existing_payroll = await self.get_payroll_by_id(payroll_id)
        
        try:
            updated_payroll = await self.payroll_repo.update_payroll(
                payroll_id, update_data, modified_by
            )
            
            # Log the action
            audit_logger.log_payroll_action(
                modified_by or "system", "updated", payroll_id,
                f"Updated payroll for {updated_payroll.employee_code} for {updated_payroll.payroll_month}"
            )
            
            return updated_payroll
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update payroll"
            )
    
    async def delete_payroll(self, payroll_id: str, deleted_by: str) -> bool:
        """Delete payroll record"""
        payroll = await self.get_payroll_by_id(payroll_id)
        
        # Check if payroll can be deleted (only draft status)
        if payroll.status != PayrollStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft payrolls can be deleted"
            )
        
        try:
            success = await self.repository.delete_payroll(payroll_id)
            
            if success:
                # Log the action
                audit_logger.log_payroll_action(
                    deleted_by, "deleted", payroll_id,
                    f"Deleted payroll for {payroll.employee_code} for {payroll.payroll_month}"
                )
            
            return success
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete payroll"
            )
    
    async def get_payrolls_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[PayrollSearch] = None,
        department: Optional[str] = None,
        payroll_status: Optional[str] = None,
        payroll_month: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of payrolls"""
        try:
            payrolls, total = await self.repository.get_payrolls_list(
                page, page_size, search, department, payroll_status, payroll_month, sort_by, sort_order
            )
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "payrolls": payrolls,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch payrolls"
            )
    
    async def approve_payroll(self, payroll_id: str, approved_by: str) -> Payroll:
        """Approve payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        
        # Check if payroll can be approved
        if payroll.status != PayrollStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft payrolls can be approved"
            )
        
        try:
            updated_payroll = await self.repository.approve_payroll(payroll_id, approved_by)
            
            # Log the action
            audit_logger.log_payroll_action(
                approved_by, "approved", payroll_id,
                f"Approved payroll for {updated_payroll.employee_code} for {updated_payroll.payroll_month}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve payroll"
            )
    
    async def lock_payroll(self, payroll_id: str, locked_by: str) -> Payroll:
        """Lock payroll (finalized)"""
        payroll = await self.get_payroll_by_id(payroll_id)
        
        # Check if payroll can be locked
        if payroll.status != PayrollStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved payrolls can be locked"
            )
        
        try:
            updated_payroll = await self.repository.lock_payroll(payroll_id, locked_by)
            
            # Log the action
            audit_logger.log_payroll_action(
                locked_by, "locked", payroll_id,
                f"Locked payroll for {updated_payroll.employee_code} for {updated_payroll.payroll_month}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to lock payroll"
            )
    
    async def run_monthly_payroll(self, payroll_run: PayrollRun, processed_by: str) -> PayrollRunResponse:
        """Run monthly payroll for multiple employees"""
        import uuid
        
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        try:
            # Get employees to process
            if payroll_run.employee_ids:
                employee_ids = payroll_run.employee_ids
            elif payroll_run.department:
                # Process department employees
                employee_ids = await self.repository.get_employee_ids_by_department(payroll_run.department)
            else:
                # Process all active employees
                employee_ids = await self.repository.get_all_active_employee_ids()
            
            successful_calculations = 0
            failed_calculations = 0
            total_amount = 0
            errors = []
            
            for employee_id in employee_ids:
                try:
                    # Create payroll for each employee
                    payroll_data = PayrollCreate(
                        employee_id=employee_id,
                        payroll_month=payroll_run.payroll_month,
                        from_date=date.today().replace(day=1),
                        to_date=date.today().replace(day=28),  # Simplified
                        working_days=22,
                        present_days=22,
                        base_salary=50000  # Placeholder - should fetch from employee data
                    )
                    
                    payroll = await self.create_payroll(payroll_data, processed_by)
                    total_amount += payroll.net_salary
                    
                    if payroll_run.auto_approve:
                        await self.approve_payroll(str(payroll.id), processed_by)
                    
                    successful_calculations += 1
                    
                except Exception as e:
                    failed_calculations += 1
                    errors.append({
                        "employee_id": employee_id,
                        "error": str(e)
                    })
            
            completed_at = datetime.utcnow()
            
            return PayrollRunResponse(
                run_id=run_id,
                payroll_month=payroll_run.payroll_month,
                status="completed" if failed_calculations == 0 else "completed_with_errors",
                total_employees=len(employee_ids),
                successful_calculations=successful_calculations,
                failed_calculations=failed_calculations,
                total_amount=total_amount,
                started_at=started_at,
                completed_at=completed_at,
                errors=errors
            )
            
        except Exception as e:
            return PayrollRunResponse(
                run_id=run_id,
                payroll_month=payroll_run.payroll_month,
                status="failed",
                total_employees=0,
                successful_calculations=0,
                failed_calculations=0,
                total_amount=0,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                errors=[{"error": str(e)}]
            )
    
    async def bulk_approve_payrolls(self, payroll_ids: List[str], approved_by: str) -> Dict[str, Any]:
        """Bulk approve payrolls"""
        try:
            approved_count = await self.repository.bulk_approve_payrolls(payroll_ids, approved_by)
            
            # Log the action
            audit_logger.log_payroll_action(
                approved_by, "bulk_approved", "",
                f"Bulk approved {approved_count} payrolls"
            )
            
            return {
                "total_payrolls": len(payroll_ids),
                "approved_count": approved_count,
                "failed_count": len(payroll_ids) - approved_count
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk approve payrolls"
            )
    
    async def get_payrolls_by_employee(self, employee_id: str) -> List[Payroll]:
        """Get all payrolls for an employee"""
        try:
            return await self.repository.get_payrolls_by_employee(employee_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch employee payrolls"
            )
    
    async def get_payrolls_by_month(self, payroll_month: str) -> List[Payroll]:
        """Get all payrolls for a specific month"""
        try:
            return await self.repository.get_payrolls_by_month(payroll_month)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch monthly payrolls"
            )
    
    async def get_payroll_statistics(self, payroll_month: Optional[str] = None) -> Dict[str, Any]:
        """Get payroll statistics"""
        try:
            return await self.repository.get_payroll_statistics(payroll_month)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch payroll statistics"
            )
    
    async def generate_payslip(self, payroll_id: str) -> Dict[str, Any]:
        """Generate payslip data"""
        payroll = await self.get_payroll_by_id(payroll_id)
        
        # Generate payslip data
        payslip_data = {
            "payroll_id": str(payroll.id),
            "employee_code": payroll.employee_code,
            "employee_name": payroll.employee_name,
            "department": payroll.department,
            "payroll_month": payroll.payroll_month,
            "payment_date": payroll.payment_date,
            
            # Earnings
            "basic_salary": payroll.base_salary,
            "attendance_salary": payroll.attendance_salary,
            "overtime_amount": payroll.overtime_amount,
            "bonus": payroll.bonus,
            "total_earnings": payroll.gross_salary,
            
            # Deductions
            "pf_employee": payroll.pf_employee,
            "esi_employee": payroll.esi_employee,
            "professional_tax": payroll.professional_tax,
            "income_tax": payroll.income_tax,
            "other_deductions": payroll.total_deductions,
            "total_deductions": payroll.total_deductions,
            
            # Net salary
            "net_salary": payroll.net_salary,
            
            # Work details
            "working_days": payroll.working_days,
            "present_days": payroll.present_days,
            "overtime_hours": payroll.overtime_hours,
            
            # Bank details
            "bank_account": payroll.bank_account,
            "payment_method": payroll.payment_method.value
        }
        
        return payslip_data
    
    async def get_payslip_by_employee_month(self, employee_id: str, payroll_month: str) -> Dict[str, Any]:
        """Get payslip for employee and month"""
        payroll = await self.get_payroll_by_employee_month(employee_id, payroll_month)
        return await self.generate_payslip(str(payroll.id))
    
    async def get_compliance_report(self, payroll_month: str) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            return await self.repository.get_compliance_report(payroll_month)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate compliance report"
            )
    
    async def export_payroll_data(self, payroll_month: Optional[str] = None, format: str = "excel") -> Dict[str, Any]:
        """Export payroll data"""
        try:
            payrolls = await self.get_payrolls_by_month(payroll_month) if payroll_month else []
            
            # Convert to export format
            export_data = []
            for payroll in payrolls:
                export_data.append({
                    "employee_code": payroll.employee_code,
                    "employee_name": payroll.employee_name,
                    "department": payroll.department,
                    "payroll_month": payroll.payroll_month,
                    "base_salary": payroll.base_salary,
                    "gross_salary": payroll.gross_salary,
                    "net_salary": payroll.net_salary,
                    "status": payroll.status.value,
                    "payment_date": payroll.payment_date
                })
            
            return {
                "data": export_data,
                "format": format,
                "month": payroll_month or "all",
                "total_records": len(export_data)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export payroll data"
            )
    
    async def _validate_payroll_data(self, payroll_data: PayrollCreate):
        """Validate payroll creation data"""
        # Date validation
        if payroll_data.from_date >= payroll_data.to_date:
            raise ValueError("From date must be before to date")
        
        # Payroll month validation
        try:
            year, month = map(int, payroll_data.payroll_month.split('-'))
            if month < 1 or month > 12:
                raise ValueError("Invalid month")
        except (ValueError, IndexError):
            raise ValueError("Invalid payroll month format. Use YYYY-MM")
        
        # Attendance validation
        total_days = payroll_data.present_days + payroll_data.absent_days + payroll_data.leave_days + payroll_data.holidays
        if total_days > payroll_data.working_days:
            raise ValueError("Total attendance days cannot exceed working days")
        
        # Salary validation
        if payroll_data.base_salary <= 0:
            raise ValueError("Base salary must be greater than 0")
    
    async def _validate_payroll_update(self, update_data: PayrollUpdate, existing_payroll: Payroll):
        """Validate payroll update data"""
        # Check if payroll can be updated
        if existing_payroll.status in [PayrollStatus.LOCKED]:
            financial_fields = [
                'base_salary', 'present_days', 'overtime_hours', 'loan_deductions', 'advance_deductions'
            ]
            
            if any(field in update_data.dict() for field in financial_fields):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Financial data cannot be modified for locked payrolls"
                )
        
        # Date validation
        if update_data.to_date and update_data.to_date <= existing_payroll.from_date:
            raise ValueError("To date must be after from date")
        
        # Salary validation
        if update_data.base_salary is not None and update_data.base_salary <= 0:
            raise ValueError("Base salary must be greater than 0")
