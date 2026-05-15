from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status
from decimal import Decimal

from .model import Payroll, PayrollStatus, PaymentMethod, AllowanceType, DeductionType
from .schema import (
    PayrollCreate, PayrollUpdate, PayrollSearch, PayrollAllowance, PayrollDeduction,
    PayrollAdjustment, PayrollApproval, PayrollProcessing, PayrollRun, PayrollRunResponse
)
from .repository import PayrollRepository
from utils.logger import audit_logger
from utils.helpers import get_working_days_in_month, generate_payroll_month_year, parse_payroll_month


class PayrollService:
    """Service layer for payroll operations"""
    
    def __init__(self):
        self.repository = PayrollRepository()
    
    async def create_payroll(self, payroll_data: PayrollCreate, created_by: str) -> Payroll:
        """Create a new payroll record"""
        # Validate input data
        await self._validate_payroll_data(payroll_data)
        
        try:
            payroll = await self.repository.create_payroll(payroll_data, created_by)
            
            # Log the action
            audit_logger.log_payroll_action(
                created_by, "created", str(payroll.id),
                f"Created payroll for {payroll.employee_code} for {payroll.payroll_month}"
            )
            
            return payroll
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payroll"
            )
    
    async def get_payroll(self, payroll_id: str) -> Payroll:
        """Get payroll by ID"""
        payroll = await self.repository.get_payroll_by_id(payroll_id)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll not found"
            )
        return payroll
    
    async def get_payroll_by_employee_month(self, employee_id: str, payroll_month: str) -> Payroll:
        """Get payroll by employee and month"""
        payroll = await self.repository.get_payroll_by_employee_month(employee_id, payroll_month)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll not found for this employee and month"
            )
        return payroll
    
    async def update_payroll(
        self, 
        payroll_id: str, 
        update_data: PayrollUpdate, 
        modified_by: str = None
    ) -> Payroll:
        """Update payroll details"""
        # Validate the payroll exists
        existing_payroll = await self.get_payroll(payroll_id)
        
        # Validate update data
        await self._validate_payroll_update(update_data, existing_payroll)
        
        try:
            updated_payroll = await self.repository.update_payroll(
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
        payroll = await self.get_payroll(payroll_id)
        
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
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """Get paginated list of payrolls"""
        try:
            payrolls, total = await self.repository.get_payrolls_list(
                page, page_size, search, sort_by, sort_order
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
    
    async def approve_payroll(self, payroll_id: str, approval_data: PayrollApproval, approved_by: str) -> Payroll:
        """Approve payroll"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be approved
        if payroll.status != PayrollStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft payrolls can be approved"
            )
        
        if not approval_data.approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval rejected"
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
    
    async def process_payroll(self, payroll_id: str, processing_data: PayrollProcessing, processed_by: str) -> Payroll:
        """Process payroll"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be processed
        if payroll.status != PayrollStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved payrolls can be processed"
            )
        
        try:
            updated_payroll = await self.repository.process_payroll(
                payroll_id, processed_by, processing_data.transaction_id
            )
            
            # Update payment method if provided
            if processing_data.payment_method:
                try:
                    updated_payroll.payment_method = PaymentMethod(processing_data.payment_method)
                    await updated_payroll.save()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid payment method"
                    )
            
            # Log the action
            audit_logger.log_payroll_action(
                processed_by, "processed", payroll_id,
                f"Processed payroll for {updated_payroll.employee_code} for {updated_payroll.payroll_month}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payroll"
            )
    
    async def mark_payroll_as_paid(
        self, 
        payroll_id: str, 
        payment_date: date, 
        utr_number: Optional[str] = None,
        processed_by: str = None
    ) -> Payroll:
        """Mark payroll as paid"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be marked as paid
        if payroll.status != PayrollStatus.PROCESSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only processed payrolls can be marked as paid"
            )
        
        try:
            updated_payroll = await self.repository.mark_paid(payroll_id, payment_date, utr_number)
            
            # Log the action
            audit_logger.log_payroll_action(
                processed_by or "system", "paid", payroll_id,
                f"Marked payroll as paid for {updated_payroll.employee_code} for {updated_payroll.payroll_month}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark payroll as paid"
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
    
    async def bulk_process_payrolls(
        self, 
        payroll_ids: List[str], 
        processing_data: PayrollProcessing,
        processed_by: str
    ) -> Dict[str, Any]:
        """Bulk process payrolls"""
        try:
            # Build transaction IDs mapping if provided
            transaction_ids = None
            if processing_data.transaction_id:
                transaction_ids = {pid: processing_data.transaction_id for pid in payroll_ids}
            
            processed_count = await self.repository.bulk_process_payrolls(
                payroll_ids, processed_by, transaction_ids
            )
            
            # Log the action
            audit_logger.log_payroll_action(
                processed_by, "bulk_processed", "",
                f"Bulk processed {processed_count} payrolls"
            )
            
            return {
                "total_payrolls": len(payroll_ids),
                "processed_count": processed_count,
                "failed_count": len(payroll_ids) - processed_count
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk process payrolls"
            )
    
    async def run_monthly_payroll(self, payroll_run: PayrollRun, processed_by: str) -> PayrollRunResponse:
        """Run monthly payroll for multiple employees"""
        import uuid
        
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        try:
            # Get employees to process
            if payroll_run.employee_ids:
                # Process specific employees
                employee_ids = payroll_run.employee_ids
            elif payroll_run.department:
                # Process department employees (would fetch from employee service)
                # This is a placeholder - in production, you'd fetch real employee data
                employee_ids = ["emp1", "emp2", "emp3"]  # Placeholder
            else:
                # Process all active employees (would fetch from employee service)
                employee_ids = ["emp1", "emp2", "emp3"]  # Placeholder
            
            successful_calculations = 0
            failed_calculations = 0
            total_amount = 0
            errors = []
            
            for employee_id in employee_ids:
                try:
                    # This would integrate with employee service to get employee data
                    # and attendance service to get attendance data
                    # For now, this is a placeholder implementation
                    
                    if not payroll_run.dry_run:
                        # Create actual payroll
                        payroll_data = PayrollCreate(
                            employee_id=employee_id,
                            employee_code="EMP001",  # Placeholder
                            employee_name="John Doe",  # Placeholder
                            department="engineering",  # Placeholder
                            payroll_month=payroll_run.payroll_month,
                            from_date=date.today().replace(day=1),
                            to_date=date.today().replace(day=28),  # Simplified
                            working_days=22,
                            present_days=22,
                            base_salary=50000  # Placeholder
                        )
                        
                        payroll = await self.create_payroll(payroll_data, processed_by)
                        total_amount += payroll.net_salary
                        
                        if payroll_run.auto_approve:
                            await self.approve_payroll(
                                str(payroll.id), 
                                PayrollApproval(approved=True), 
                                processed_by
                            )
                    
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
    
    async def get_yearly_summary(self, employee_id: str, year: int) -> Dict[str, Any]:
        """Get yearly payroll summary for an employee"""
        try:
            return await self.repository.get_yearly_summary(employee_id, year)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch yearly summary"
            )
    
    async def get_compliance_report(self, payroll_month: str) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            return await self.repository.get_compliance_report(payroll_month)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate compliance report"
            )
    
    async def add_allowance_to_payroll(
        self, 
        payroll_id: str, 
        allowance_data: PayrollAllowance,
        modified_by: str
    ) -> Payroll:
        """Add allowance to payroll"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be modified
        if payroll.status not in [PayrollStatus.DRAFT, PayrollStatus.PENDING_APPROVAL]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or pending payroll can be modified"
            )
        
        try:
            # Validate allowance type
            try:
                AllowanceType(allowance_data.allowance_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid allowance type"
                )
            
            updated_payroll = await self.repository.add_allowance_to_payroll(payroll_id, allowance_data)
            
            # Log the action
            audit_logger.log_payroll_action(
                modified_by, "allowance_added", payroll_id,
                f"Added allowance {allowance_data.allowance_type} to payroll for {updated_payroll.employee_code}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add allowance"
            )
    
    async def add_deduction_to_payroll(
        self, 
        payroll_id: str, 
        deduction_data: PayrollDeduction,
        modified_by: str
    ) -> Payroll:
        """Add deduction to payroll"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be modified
        if payroll.status not in [PayrollStatus.DRAFT, PayrollStatus.PENDING_APPROVAL]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or pending payroll can be modified"
            )
        
        try:
            # Validate deduction type
            try:
                DeductionType(deduction_data.deduction_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid deduction type"
                )
            
            updated_payroll = await self.repository.add_deduction_to_payroll(payroll_id, deduction_data)
            
            # Log the action
            audit_logger.log_payroll_action(
                modified_by, "deduction_added", payroll_id,
                f"Added deduction {deduction_data.deduction_type} to payroll for {updated_payroll.employee_code}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add deduction"
            )
    
    async def add_adjustment_to_payroll(
        self, 
        payroll_id: str, 
        adjustment_data: PayrollAdjustment,
        modified_by: str
    ) -> Payroll:
        """Add adjustment to payroll"""
        payroll = await self.get_payroll(payroll_id)
        
        # Check if payroll can be modified
        if payroll.status not in [PayrollStatus.DRAFT, PayrollStatus.PENDING_APPROVAL]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or pending payroll can be modified"
            )
        
        try:
            updated_payroll = await self.repository.add_adjustment_to_payroll(payroll_id, adjustment_data)
            
            # Log the action
            audit_logger.log_payroll_action(
                modified_by, "adjustment_added", payroll_id,
                f"Added adjustment {adjustment_data.adjustment_type} to payroll for {updated_payroll.employee_code}"
            )
            
            return updated_payroll
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add adjustment"
            )
    
    async def _validate_payroll_data(self, payroll_data: PayrollCreate):
        """Validate payroll creation data"""
        # Date validation
        if payroll_data.from_date >= payroll_data.to_date:
            raise ValueError("From date must be before to date")
        
        # Payroll month validation
        try:
            parse_payroll_month(payroll_data.payroll_month)
        except ValueError:
            raise ValueError("Invalid payroll month format. Use YYYY-MM")
        
        # Attendance validation
        total_days = payroll_data.present_days + payroll_data.absent_days + payroll_data.leave_days + payroll_data.holidays
        if total_days > payroll_data.working_days:
            raise ValueError("Total attendance days cannot exceed working days")
        
        if payroll_data.present_days > payroll_data.working_days:
            raise ValueError("Present days cannot exceed working days")
        
        # Salary validation
        if payroll_data.base_salary <= 0:
            raise ValueError("Base salary must be greater than 0")
        
        # Payment method validation
        try:
            PaymentMethod(payroll_data.payment_method)
        except ValueError:
            raise ValueError("Invalid payment method")
    
    async def _validate_payroll_update(self, update_data: PayrollUpdate, existing_payroll: Payroll):
        """Validate payroll update data"""
        # Check if payroll can be updated
        if existing_payroll.status in [PayrollStatus.PROCESSED, PayrollStatus.PAID]:
            financial_fields = [
                'base_salary', 'present_days', 'overtime_hours', 'loan_deductions', 'advance_deductions'
            ]
            
            if any(field in update_data.dict() for field in financial_fields):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Financial data cannot be modified for processed or paid payrolls"
                )
        
        # Date validation
        if update_data.to_date and update_data.to_date <= existing_payroll.from_date:
            raise ValueError("To date must be after from date")
        
        # Attendance validation
        attendance_fields = ['present_days', 'absent_days', 'leave_days', 'holidays']
        attendance_updates = {k: v for k, v in update_data.dict().items() if k in attendance_fields and v is not None}
        
        if attendance_updates:
            # Recalculate total
            total_days = existing_payroll.present_days + existing_payroll.absent_days + existing_payroll.leave_days + existing_payroll.holidays
            
            for field, value in attendance_updates.items():
                if field == 'present_days':
                    total_days = total_days - existing_payroll.present_days + value
                elif field == 'absent_days':
                    total_days = total_days - existing_payroll.absent_days + value
                elif field == 'leave_days':
                    total_days = total_days - existing_payroll.leave_days + value
                elif field == 'holidays':
                    total_days = total_days - existing_payroll.holidays + value
            
            if total_days > existing_payroll.working_days:
                raise ValueError("Total attendance days cannot exceed working days")
        
        # Salary validation
        if update_data.base_salary is not None and update_data.base_salary <= 0:
            raise ValueError("Base salary must be greater than 0")
        
        # Payment method validation
        if update_data.payment_method:
            try:
                PaymentMethod(update_data.payment_method)
            except ValueError:
                raise ValueError("Invalid payment method")
