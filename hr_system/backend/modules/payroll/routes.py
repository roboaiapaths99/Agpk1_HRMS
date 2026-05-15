from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from fastapi.security import HTTPBearer

from .model import Payroll
from .schema import (
    PayrollCreate, PayrollUpdate, PayrollResponse, PayrollListResponse,
    PayrollSearch, PayrollBulkAction, PayrollAllowance, PayrollDeduction,
    PayrollAdjustment, PayrollApproval, PayrollProcessing, PayrollRun,
    PayrollRunResponse, PayrollStatistics, PayrollYearlySummary, PayrollComplianceReport
)
from .service import PayrollService
from ..auth.dependencies import get_current_user, require_permission
from ..user.model import User

router = APIRouter()
security = HTTPBearer()
payroll_service = PayrollService()


@router.post("/", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    payroll_data: PayrollCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new payroll record"""
    # Check permission
    require_permission(current_user, "payroll", "create")
    
    payroll = await payroll_service.create_payroll(payroll_data, current_user.username)
    return payroll


@router.get("/", response_model=PayrollListResponse)
async def get_payrolls(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    payroll_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    payment_date_from: Optional[str] = Query(None, description="Payment date from (YYYY-MM-DD)"),
    payment_date_to: Optional[str] = Query(None, description="Payment date to (YYYY-MM-DD)"),
    min_net_salary: Optional[float] = Query(None, ge=0, description="Minimum net salary filter"),
    max_net_salary: Optional[float] = Query(None, ge=0, description="Maximum net salary filter"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of payrolls with pagination and filtering"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    # Parse dates
    from datetime import datetime
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        return None
    
    # Build search object
    search_obj = None
    if any([search, department, payroll_status, payroll_month, payment_date_from, payment_date_to,
            min_net_salary, max_net_salary]):
        search_obj = PayrollSearch(
            query=search,
            department=department,
            status=payroll_status,
            payroll_month=payroll_month,
            payment_date_from=parse_date(payment_date_from),
            payment_date_to=parse_date(payment_date_to),
            min_net_salary=min_net_salary,
            max_net_salary=max_net_salary
        )
    
    result = await payroll_service.get_payrolls_list(
        page, page_size, search_obj, sort_by, sort_order
    )
    
    return PayrollListResponse(**result)


@router.get("/{payroll_id}", response_model=PayrollResponse)
async def get_payroll(
    payroll_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payroll by ID"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payroll = await payroll_service.get_payroll(payroll_id)
    return payroll


@router.get("/employee/{employee_id}/month/{payroll_month}", response_model=PayrollResponse)
async def get_payroll_by_employee_month(
    employee_id: str,
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Get payroll by employee and month"""
    # Check permission (users can view their own payroll)
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "payroll", "read")
    
    payroll = await payroll_service.get_payroll_by_employee_month(employee_id, payroll_month)
    return payroll


@router.put("/{payroll_id}", response_model=PayrollResponse)
async def update_payroll(
    payroll_id: str,
    update_data: PayrollUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update payroll details"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.update_payroll(
        payroll_id, update_data, current_user.username
    )
    return payroll


@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll(
    payroll_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete payroll record"""
    # Check permission
    require_permission(current_user, "payroll", "delete")
    
    success = await payroll_service.delete_payroll(payroll_id, current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll not found"
        )


@router.patch("/{payroll_id}/approve", response_model=PayrollResponse)
async def approve_payroll(
    payroll_id: str,
    approval_data: PayrollApproval,
    current_user: User = Depends(get_current_user)
):
    """Approve payroll"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.approve_payroll(payroll_id, approval_data, current_user.username)
    return payroll


@router.patch("/{payroll_id}/process", response_model=PayrollResponse)
async def process_payroll(
    payroll_id: str,
    processing_data: PayrollProcessing,
    current_user: User = Depends(get_current_user)
):
    """Process payroll"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.process_payroll(payroll_id, processing_data, current_user.username)
    return payroll


@router.patch("/{payroll_id}/mark-paid", response_model=PayrollResponse)
async def mark_payroll_as_paid(
    payroll_id: str,
    payment_date: str = Query(..., description="Payment date (YYYY-MM-DD)"),
    utr_number: Optional[str] = Query(None, description="UTR number"),
    current_user: User = Depends(get_current_user)
):
    """Mark payroll as paid"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    from datetime import datetime
    try:
        parsed_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    payroll = await payroll_service.mark_payroll_as_paid(
        payroll_id, parsed_date, utr_number, current_user.username
    )
    return payroll


@router.get("/employee/{employee_id}", response_model=List[PayrollResponse])
async def get_payrolls_by_employee(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all payrolls for an employee"""
    # Check permission (users can view their own payrolls)
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.get_payrolls_by_employee(employee_id)
    return payrolls


@router.get("/month/{payroll_month}", response_model=List[PayrollResponse])
async def get_payrolls_by_month(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Get all payrolls for a specific month"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.get_payrolls_by_month(payroll_month)
    return payrolls


@router.get("/department/{department}", response_model=List[PayrollResponse])
async def get_payrolls_by_department(
    department: str,
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    current_user: User = Depends(get_current_user)
):
    """Get payrolls by department"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.get_payrolls_by_department(department, payroll_month)
    return payrolls


@router.get("/statistics/overview")
async def get_payroll_statistics(
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    current_user: User = Depends(get_current_user)
):
    """Get payroll statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await payroll_service.get_payroll_statistics(payroll_month)
    return stats


@router.post("/bulk-approve")
async def bulk_approve_payrolls(
    payroll_ids: List[str],
    current_user: User = Depends(get_current_user)
):
    """Bulk approve payrolls"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    result = await payroll_service.bulk_approve_payrolls(payroll_ids, current_user.username)
    return result


@router.post("/bulk-process")
async def bulk_process_payrolls(
    payroll_ids: List[str],
    processing_data: PayrollProcessing,
    current_user: User = Depends(get_current_user)
):
    """Bulk process payrolls"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    result = await payroll_service.bulk_process_payrolls(payroll_ids, processing_data, current_user.username)
    return result


@router.post("/run-monthly", response_model=PayrollRunResponse)
async def run_monthly_payroll(
    payroll_run: PayrollRun,
    current_user: User = Depends(get_current_user)
):
    """Run monthly payroll for multiple employees"""
    # Check permission
    require_permission(current_user, "payroll", "create")
    
    result = await payroll_service.run_monthly_payroll(payroll_run, current_user.username)
    return result


@router.get("/employee/{employee_id}/year/{year}", response_model=PayrollYearlySummary)
async def get_yearly_summary(
    employee_id: str,
    year: int,
    current_user: User = Depends(get_current_user)
):
    """Get yearly payroll summary for an employee"""
    # Check permission (users can view their own summary)
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "payroll", "read")
    
    summary = await payroll_service.get_yearly_summary(employee_id, year)
    return PayrollYearlySummary(**summary) if summary else HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No payroll data found for this employee and year"
    )


@router.get("/compliance/month/{payroll_month}", response_model=PayrollComplianceReport)
async def get_compliance_report(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Generate compliance report"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    report = await payroll_service.get_compliance_report(payroll_month)
    return PayrollComplianceReport(**report)


@router.post("/{payroll_id}/allowances", response_model=PayrollResponse)
async def add_allowance_to_payroll(
    payroll_id: str,
    allowance_data: PayrollAllowance,
    current_user: User = Depends(get_current_user)
):
    """Add allowance to payroll"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.add_allowance_to_payroll(
        payroll_id, allowance_data, current_user.username
    )
    return payroll


@router.post("/{payroll_id}/deductions", response_model=PayrollResponse)
async def add_deduction_to_payroll(
    payroll_id: str,
    deduction_data: PayrollDeduction,
    current_user: User = Depends(get_current_user)
):
    """Add deduction to payroll"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.add_deduction_to_payroll(
        payroll_id, deduction_data, current_user.username
    )
    return payroll


@router.post("/{payroll_id}/adjustments", response_model=PayrollResponse)
async def add_adjustment_to_payroll(
    payroll_id: str,
    adjustment_data: PayrollAdjustment,
    current_user: User = Depends(get_current_user)
):
    """Add adjustment to payroll"""
    # Check permission
    require_permission(current_user, "payroll", "update")
    
    payroll = await payroll_service.add_adjustment_to_payroll(
        payroll_id, adjustment_data, current_user.username
    )
    return payroll


@router.get("/{payroll_id}/slip")
async def generate_payroll_slip(
    payroll_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate payroll slip"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payroll = await payroll_service.get_payroll(payroll_id)
    
    # Generate payroll slip data
    slip_data = payroll.get_detailed_breakdown()
    slip_data.update({
        "payroll_id": str(payroll.id),
        "employee_code": payroll.employee_code,
        "employee_name": payroll.employee_name,
        "department": payroll.department,
        "designation": "Employee",  # Would fetch from employee data
        "payroll_month": payroll.payroll_month,
        "payment_date": payroll.payment_date,
        "bank_name": payroll.bank_name,
        "bank_account": payroll.bank_account,
        "payment_method": payroll.payment_method.value
    })
    
    return slip_data


@router.get("/pending-approval", response_model=List[PayrollResponse])
async def get_pending_approval_payrolls(
    current_user: User = Depends(get_current_user)
):
    """Get payrolls pending approval"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.repository.get_pending_approval_payrolls()
    return payrolls


@router.get("/approved", response_model=List[PayrollResponse])
async def get_approved_payrolls(
    current_user: User = Depends(get_current_user)
):
    """Get approved payrolls"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.repository.get_approved_payrolls()
    return payrolls


@router.get("/processed", response_model=List[PayrollResponse])
async def get_processed_payrolls(
    current_user: User = Depends(get_current_user)
):
    """Get processed payrolls"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.repository.get_processed_payrolls()
    return payrolls


@router.get("/me")
async def get_my_payrolls(
    current_user: User = Depends(get_current_user)
):
    """Get current user's payrolls"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile found for this user"
        )
    
    payrolls = await payroll_service.get_payrolls_by_employee(current_user.employee_id)
    return {"payrolls": payrolls}


@router.get("/me/month/{payroll_month}", response_model=PayrollResponse)
async def get_my_payroll_for_month(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Get current user's payroll for a specific month"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile found for this user"
        )
    
    payroll = await payroll_service.get_payroll_by_employee_month(
        current_user.employee_id, payroll_month
    )
    return payroll


@router.get("/me/year/{year}", response_model=PayrollYearlySummary)
async def get_my_yearly_summary(
    year: int,
    current_user: User = Depends(get_current_user)
):
    """Get current user's yearly payroll summary"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile found for this user"
        )
    
    summary = await payroll_service.get_yearly_summary(current_user.employee_id, year)
    return PayrollYearlySummary(**summary) if summary else HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No payroll data found for this year"
    )
