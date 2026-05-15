from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from models.payroll_model import Payroll, PayrollStatus, PaymentMethod
from utils.helpers import create_pagination_params


class PayrollRepository:
    """Repository for payroll operations"""
    
    async def create_payroll(self, payroll_data, created_by: str = None) -> Payroll:
        """Create a new payroll record"""
        payroll = Payroll(**payroll_data.dict())
        if created_by:
            payroll.created_by = created_by
        await payroll.insert()
        return payroll
    
    async def get_payroll_by_id(self, payroll_id: str) -> Optional[Payroll]:
        """Get payroll by ID"""
        try:
            return await Payroll.get(PydanticObjectId(payroll_id))
        except:
            return None
    
    async def get_payroll_by_employee_month(self, employee_id: str, payroll_month: str) -> Optional[Payroll]:
        """Get payroll by employee and month"""
        return await Payroll.find_one({
            "employee_id": employee_id,
            "payroll_month": payroll_month
        })
    
    async def update_payroll(self, payroll_id: str, update_data, modified_by: str = None) -> Optional[Payroll]:
        """Update payroll details"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if modified_by:
            update_dict["last_modified_by"] = modified_by
        update_dict["updated_at"] = datetime.utcnow()
        
        # Recalculate payroll if financial data changed
        financial_fields = [
            'base_salary', 'present_days', 'overtime_hours', 'loan_deductions', 
            'advance_deductions', 'bonus', 'other_earnings', 'other_deductions'
        ]
        
        if any(field in update_dict for field in financial_fields):
            await self._recalculate_payroll(payroll, update_dict)
        
        for field, value in update_dict.items():
            if hasattr(payroll, field):
                setattr(payroll, field, value)
        
        await payroll.save()
        return payroll
    
    async def delete_payroll(self, payroll_id: str) -> bool:
        """Delete payroll record"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return False
        
        await payroll.delete()
        return True
    
    async def get_payrolls_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[dict] = None,
        department: Optional[str] = None,
        payroll_status: Optional[str] = None,
        payroll_month: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Payroll], int]:
        """Get list of payrolls with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            if search.get("query"):
                query["$or"] = [
                    {"employee_code": {"$regex": search["query"], "$options": "i"}},
                    {"employee_name": {"$regex": search["query"], "$options": "i"}},
                    {"department": {"$regex": search["query"], "$options": "i"}}
                ]
        
        if department:
            query["department"] = department
        
        if payroll_status:
            try:
                query["status"] = PayrollStatus(payroll_status)
            except ValueError:
                pass
        
        if payroll_month:
            query["payroll_month"] = payroll_month
        
        # Get total count
        total = await Payroll.find(query).count()
        
        # Get payrolls with pagination and sorting
        payrolls = await Payroll.find(query).sort(
            [(sort_by, sort_order)]
        ).skip(pagination["skip"]).limit(pagination["limit"]).to_list()
        
        return payrolls, total
    
    async def approve_payroll(self, payroll_id: str, approved_by: str) -> Optional[Payroll]:
        """Approve payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        payroll.status = PayrollStatus.APPROVED
        payroll.approved_by = approved_by
        payroll.approved_at = datetime.utcnow()
        await payroll.save()
        
        return payroll
    
    async def lock_payroll(self, payroll_id: str, locked_by: str) -> Optional[Payroll]:
        """Lock payroll (finalized)"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        payroll.status = PayrollStatus.LOCKED
        payroll.locked_by = locked_by
        payroll.locked_at = datetime.utcnow()
        await payroll.save()
        
        return payroll
    
    async def bulk_approve_payrolls(self, payroll_ids: List[str], approved_by: str) -> int:
        """Bulk approve payrolls"""
        result = await Payroll.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in payroll_ids]}}
        ).update({
            "$set": {
                "status": PayrollStatus.APPROVED,
                "approved_by": approved_by,
                "approved_at": datetime.utcnow()
            }
        })
        
        return result.modified_count
    
    async def get_payrolls_by_employee(self, employee_id: str) -> List[Payroll]:
        """Get all payrolls for an employee"""
        return await Payroll.find(
            {"employee_id": employee_id}
        ).sort(Payroll.payroll_month, DESCENDING).to_list()
    
    async def get_payrolls_by_month(self, payroll_month: str) -> List[Payroll]:
        """Get all payrolls for a specific month"""
        return await Payroll.find(
            {"payroll_month": payroll_month}
        ).sort(Payroll.created_at, DESCENDING).to_list()
    
    async def get_payroll_statistics(self, payroll_month: Optional[str] = None) -> dict:
        """Get payroll statistics"""
        # Build query
        query = {}
        if payroll_month:
            query["payroll_month"] = payroll_month
        
        # Total payrolls
        total_payrolls = await Payroll.find(query).count()
        
        # Status breakdown
        status_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = await Payroll.aggregate(status_pipeline).to_list()
        
        # Department breakdown
        dept_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$department", "count": {"$sum": 1}, "total_amount": {"$sum": "$net_salary"}}},
            {"$sort": {"total_amount": -1}}
        ]
        dept_stats = await Payroll.aggregate(dept_pipeline).to_list()
        
        # Financial totals
        totals_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_gross_salary": {"$sum": "$gross_salary"},
                "total_net_salary": {"$sum": "$net_salary"},
                "total_deductions": {"$sum": "$total_deductions"},
                "total_overtime": {"$sum": "$overtime_amount"},
                "total_bonus": {"$sum": "$bonus"}
            }}
        ]
        totals_result = await Payroll.aggregate(totals_pipeline).to_list()
        
        totals = totals_result[0] if totals_result else {
            "total_gross_salary": 0,
            "total_net_salary": 0,
            "total_deductions": 0,
            "total_overtime": 0,
            "total_bonus": 0
        }
        
        # Payment method breakdown
        payment_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$payment_method", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        payment_stats = await Payroll.aggregate(payment_pipeline).to_list()
        
        return {
            "total_payrolls": total_payrolls,
            "status_breakdown": status_stats,
            "department_breakdown": dept_stats,
            "financial_totals": totals,
            "payment_method_breakdown": payment_stats
        }
    
    async def get_compliance_report(self, payroll_month: str) -> dict:
        """Generate compliance report"""
        # Get all payrolls for the month
        payrolls = await self.get_payrolls_by_month(payroll_month)
        
        # Calculate compliance metrics
        total_employees = len(payrolls)
        
        # PF compliance
        pf_eligible = len([p for p in payrolls if p.pf_employee > 0])
        pf_compliant = len([p for p in payrolls if p.pf_employee > 0 and p.pf_employer > 0])
        
        # ESI compliance
        esi_eligible = len([p for p in payrolls if p.esi_employee > 0])
        esi_compliant = len([p for p in payrolls if p.esi_employee > 0 and p.esi_employer > 0])
        
        # Tax compliance
        tax_eligible = len([p for p in payrolls if p.income_tax > 0])
        tax_compliant = len([p for p in payrolls if p.income_tax > 0])
        
        # Professional tax compliance
        pt_eligible = len([p for p in payrolls if p.professional_tax > 0])
        pt_compliant = len([p for p in payrolls if p.professional_tax > 0])
        
        return {
            "payroll_month": payroll_month,
            "total_employees": total_employees,
            "pf_compliance": {
                "eligible": pf_eligible,
                "compliant": pf_compliant,
                "compliance_rate": (pf_compliant / pf_eligible * 100) if pf_eligible > 0 else 100
            },
            "esi_compliance": {
                "eligible": esi_eligible,
                "compliant": esi_compliant,
                "compliance_rate": (esi_compliant / esi_eligible * 100) if esi_eligible > 0 else 100
            },
            "tax_compliance": {
                "eligible": tax_eligible,
                "compliant": tax_compliant,
                "compliance_rate": (tax_compliant / tax_eligible * 100) if tax_eligible > 0 else 100
            },
            "pt_compliance": {
                "eligible": pt_eligible,
                "compliant": pt_compliant,
                "compliance_rate": (pt_compliant / pt_eligible * 100) if pt_eligible > 0 else 100
            },
            "overall_compliance_rate": (
                (pf_compliant + esi_compliant + tax_compliant + pt_compliant) /
                (pf_eligible + esi_eligible + tax_eligible + pt_eligible) * 100
            ) if (pf_eligible + esi_eligible + tax_eligible + pt_eligible) > 0 else 100
        }
    
    async def get_employee_ids_by_department(self, department: str) -> List[str]:
        """Get employee IDs by department"""
        # This would integrate with employee repository
        # For now, return empty list
        return []
    
    async def get_all_active_employee_ids(self) -> List[str]:
        """Get all active employee IDs"""
        # This would integrate with employee repository
        # For now, return empty list
        return []
    
    async def _recalculate_payroll(self, payroll: Payroll, update_data: dict):
        """Recalculate payroll components"""
        # Update attendance salary based on present days
        if 'base_salary' in update_data or 'present_days' in update_data:
            base_salary = update_data.get('base_salary', payroll.base_salary)
            present_days = update_data.get('present_days', payroll.present_days)
            working_days = payroll.working_days
            
            if working_days > 0:
                payroll.attendance_salary = (base_salary / working_days) * present_days
            else:
                payroll.attendance_salary = 0
        
        # Calculate overtime
        if 'overtime_hours' in update_data:
            overtime_hours = update_data['overtime_hours']
            base_salary = update_data.get('base_salary', payroll.base_salary)
            
            # Calculate overtime rate (1.5x base hourly rate)
            hourly_rate = base_salary / (30 * 8)  # Assuming 30 days, 8 hours
            payroll.overtime_amount = overtime_hours * hourly_rate * 1.5
        
        # Update gross salary
        payroll.gross_salary = (
            payroll.attendance_salary +
            payroll.overtime_amount +
            update_data.get('bonus', payroll.bonus) +
            update_data.get('other_earnings', payroll.other_earnings)
        )
        
        # Calculate statutory deductions
        if payroll.gross_salary > 0:
            # PF (12% of basic salary)
            payroll.pf_employee = payroll.attendance_salary * 0.12
            payroll.pf_employer = payroll.attendance_salary * 0.12
            
            # ESI (0.75% employee, 3.25% employer)
            payroll.esi_employee = payroll.gross_salary * 0.0075
            payroll.esi_employer = payroll.gross_salary * 0.0325
            
            # Professional tax (fixed amount)
            payroll.professional_tax = 200  # Placeholder
        
        # Calculate total deductions
        payroll.total_deductions = (
            payroll.pf_employee +
            payroll.esi_employee +
            payroll.professional_tax +
            update_data.get('loan_deductions', payroll.loan_deductions) +
            update_data.get('advance_deductions', payroll.advance_deductions) +
            update_data.get('other_deductions', payroll.other_deductions) +
            update_data.get('income_tax', payroll.income_tax)
        )
        
        # Calculate net salary
        payroll.net_salary = payroll.gross_salary - payroll.total_deductions
