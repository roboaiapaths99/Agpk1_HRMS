from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime, date

from services.payroll_service import PayrollService
from schemas.payroll_schema import (
    PayrollCreate, PayrollUpdate, PayrollResponse, PayrollListResponse,
    PayrollSearch, PayrollBulkAction, PayrollRun, PayrollRunResponse
)
from modules.auth.dependencies import get_current_user, require_permission
from modules.user.model import User

router = APIRouter(prefix="/payroll", tags=["Payroll"])
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
    payroll_status: Optional[str] = Query(None, description="Filter by status"),
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: int = Query(-1, ge=-1, le=1, description="Sort order (-1 for desc, 1 for asc)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of payrolls with pagination and filtering"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    result = await payroll_service.get_payrolls_list(
        page, page_size, search, department, payroll_status, payroll_month, sort_by, sort_order
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
    
    payroll = await payroll_service.get_payroll_by_id(payroll_id)
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
    
    payroll = await payroll_service.update_payroll(payroll_id, update_data, current_user.username)
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
    current_user: User = Depends(get_current_user)
):
    """Approve payroll"""
    # Check permission
    require_permission(current_user, "payroll", "approve")
    
    payroll = await payroll_service.approve_payroll(payroll_id, current_user.username)
    return payroll


@router.patch("/{payroll_id}/lock", response_model=PayrollResponse)
async def lock_payroll(
    payroll_id: str,
    current_user: User = Depends(get_current_user)
):
    """Lock payroll (finalized)"""
    # Check permission
    require_permission(current_user, "payroll", "lock")
    
    payroll = await payroll_service.lock_payroll(payroll_id, current_user.username)
    return payroll


@router.post("/run-monthly", response_model=PayrollRunResponse)
async def run_monthly_payroll(
    payroll_run: PayrollRun,
    current_user: User = Depends(get_current_user)
):
    """Run monthly payroll for multiple employees"""
    # Check permission
    require_permission(current_user, "payroll", "run")
    
    result = await payroll_service.run_monthly_payroll(payroll_run, current_user.username)
    return result


@router.post("/bulk-approve")
async def bulk_approve_payrolls(
    payroll_ids: List[str],
    current_user: User = Depends(get_current_user)
):
    """Bulk approve payrolls"""
    # Check permission
    require_permission(current_user, "payroll", "approve")
    
    result = await payroll_service.bulk_approve_payrolls(payroll_ids, current_user.username)
    return result


@router.get("/employee/{employee_id}", response_model=List[PayrollResponse])
async def get_employee_payrolls(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all payrolls for an employee"""
    # Users can view their own payrolls
    if current_user.role.value != "admin" and current_user.employee_id != employee_id:
        require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.get_payrolls_by_employee(employee_id)
    return payrolls


@router.get("/month/{payroll_month}", response_model=List[PayrollResponse])
async def get_monthly_payrolls(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Get all payrolls for a specific month"""
    # Check permission
    require_permission(current_user, "payroll", "read")
    
    payrolls = await payroll_service.get_payrolls_by_month(payroll_month)
    return payrolls


@router.get("/statistics")
async def get_payroll_statistics(
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    current_user: User = Depends(get_current_user)
):
    """Get payroll statistics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    stats = await payroll_service.get_payroll_statistics(payroll_month)
    return stats


@router.get("/{payroll_id}/payslip")
async def generate_payslip(
    payroll_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate payslip PDF"""
    # Users can view their own payslips
    payroll = await payroll_service.get_payroll_by_id(payroll_id)
    if current_user.role.value != "admin" and current_user.employee_id != payroll.employee_id:
        require_permission(current_user, "payroll", "read")
    
    payslip_data = await payroll_service.generate_payslip(payroll_id)
    return payslip_data


@router.get("/me", response_model=List[PayrollResponse])
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
    return payrolls


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
    
    payroll = await payroll_service.get_payroll_by_employee_month(current_user.employee_id, payroll_month)
    return payroll


@router.get("/me/payslip/{payroll_month}")
async def get_my_payslip(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Get current user's payslip for a specific month"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile found for this user"
        )
    
    payslip_data = await payroll_service.get_payslip_by_employee_month(current_user.employee_id, payroll_month)
    return payslip_data


@router.get("/compliance/month/{payroll_month}")
async def get_compliance_report(
    payroll_month: str,
    current_user: User = Depends(get_current_user)
):
    """Generate compliance report"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    report = await payroll_service.get_compliance_report(payroll_month)
    return report


@router.get("/export")
async def export_payroll_data(
    payroll_month: Optional[str] = Query(None, description="Filter by payroll month"),
    format: str = Query("excel", description="Export format (excel, csv, pdf)"),
    current_user: User = Depends(get_current_user)
):
    """Export payroll data"""
    # Check permission
    require_permission(current_user, "payroll", "export")
    
    export_data = await payroll_service.export_payroll_data(payroll_month, format)
    return export_data
