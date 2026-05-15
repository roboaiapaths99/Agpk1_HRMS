from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from .model import Payroll, PayrollStatus, PaymentMethod, AllowanceType, DeductionType
from .schema import PayrollCreate, PayrollUpdate, PayrollSearch, PayrollAllowance, PayrollDeduction, PayrollAdjustment
from utils.helpers import create_pagination_params, generate_payroll_month_year, parse_payroll_month


class PayrollRepository:
    """Repository for payroll operations"""
    
    async def create_payroll(self, payroll_data: PayrollCreate, created_by: str) -> Payroll:
        """Create a new payroll record"""
        # Check if payroll already exists for this employee and month
        existing_payroll = await self.get_payroll_by_employee_month(
            payroll_data.employee_id, payroll_data.payroll_month
        )
        if existing_payroll:
            raise ValueError(f"Payroll already exists for employee {payroll_data.employee_code} for month {payroll_data.payroll_month}")
        
        # Create payroll document
        payroll = Payroll(
            **payroll_data.dict(),
            created_by=created_by
        )
        
        # Calculate payroll
        await payroll.calculate_payroll()
        
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
    
    async def update_payroll(
        self, 
        payroll_id: str, 
        update_data: PayrollUpdate, 
        modified_by: str = None
    ) -> Optional[Payroll]:
        """Update payroll details"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(payroll, field, value)
        
        payroll.updated_at = datetime.utcnow()
        if modified_by:
            payroll.last_modified_by = modified_by
        
        # Recalculate payroll if financial data changed
        financial_fields = [
            'base_salary', 'present_days', 'overtime_hours', 'overtime_rate',
            'loan_deductions', 'advance_deductions'
        ]
        
        if any(field in update_dict for field in financial_fields):
            await payroll.calculate_payroll()
        
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
        search: Optional[PayrollSearch] = None,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> tuple[List[Payroll], int]:
        """Get list of payrolls with pagination and filtering"""
        pagination = create_pagination_params(page, page_size)
        
        # Build query
        query = {}
        
        if search:
            if search.query:
                query["$or"] = [
                    {"employee_name": {"$regex": search.query, "$options": "i"}},
                    {"employee_code": {"$regex": search.query, "$options": "i"}},
                    {"department": {"$regex": search.query, "$options": "i"}}
                ]
            
            if search.department:
                query["department"] = search.department
            
            if search.status:
                query["status"] = search.status
            
            if search.payroll_month:
                query["payroll_month"] = search.payroll_month
            
            if search.payment_date_from:
                if "payment_date" in query:
                    query["payment_date"]["$gte"] = search.payment_date_from
                else:
                    query["payment_date"] = {"$gte": search.payment_date_from}
            
            if search.payment_date_to:
                if "payment_date" in query:
                    query["payment_date"]["$lte"] = search.payment_date_to
                else:
                    query["payment_date"] = {"$lte": search.payment_date_to}
            
            if search.min_net_salary is not None:
                if "net_salary" in query:
                    query["net_salary"]["$gte"] = search.min_net_salary
                else:
                    query["net_salary"] = {"$gte": search.min_net_salary}
            
            if search.max_net_salary is not None:
                if "net_salary" in query:
                    query["net_salary"]["$lte"] = search.max_net_salary
                else:
                    query["net_salary"] = {"$lte": search.max_net_salary}
        
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
        
        await payroll.approve(approved_by)
        return payroll
    
    async def process_payroll(
        self, 
        payroll_id: str, 
        processed_by: str, 
        transaction_id: Optional[str] = None
    ) -> Optional[Payroll]:
        """Process payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        await payroll.process(processed_by, transaction_id)
        return payroll
    
    async def mark_paid(
        self, 
        payroll_id: str, 
        payment_date: date, 
        utr_number: Optional[str] = None
    ) -> Optional[Payroll]:
        """Mark payroll as paid"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        await payroll.mark_paid(payment_date, utr_number)
        return payroll
    
    async def get_payrolls_by_employee(self, employee_id: str) -> List[Payroll]:
        """Get all payrolls for an employee"""
        return await Payroll.find(
            Payroll.employee_id == employee_id
        ).sort(Payroll.payroll_month, DESCENDING).to_list()
    
    async def get_payrolls_by_month(self, payroll_month: str) -> List[Payroll]:
        """Get all payrolls for a specific month"""
        return await Payroll.find(
            Payroll.payroll_month == payroll_month
        ).sort(Payroll.employee_code, ASCENDING).to_list()
    
    async def get_payrolls_by_department(self, department: str, payroll_month: Optional[str] = None) -> List[Payroll]:
        """Get payrolls by department"""
        query = {"department": department}
        if payroll_month:
            query["payroll_month"] = payroll_month
        
        return await Payroll.find(query).sort(Payroll.employee_code, ASCENDING).to_list()
    
    async def get_payrolls_by_status(self, status: PayrollStatus) -> List[Payroll]:
        """Get payrolls by status"""
        return await Payroll.find(
            Payroll.status == status
        ).sort(Payroll.created_at, DESCENDING).to_list()
    
    async def get_pending_approval_payrolls(self) -> List[Payroll]:
        """Get payrolls pending approval"""
        return await self.get_payrolls_by_status(PayrollStatus.PENDING_APPROVAL)
    
    async def get_approved_payrolls(self) -> List[Payroll]:
        """Get approved payrolls"""
        return await self.get_payrolls_by_status(PayrollStatus.APPROVED)
    
    async def get_processed_payrolls(self) -> List[Payroll]:
        """Get processed payrolls"""
        return await self.get_payrolls_by_status(PayrollStatus.PROCESSED)
    
    async def get_payroll_statistics(self, payroll_month: Optional[str] = None) -> Dict[str, Any]:
        """Get payroll statistics"""
        # Build query
        query = {}
        if payroll_month:
            query["payroll_month"] = payroll_month
        
        # Overall statistics
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "totalAmount": {"$sum": "$net_salary"},
                    "totalEmployees": {"$sum": 1},
                    "avgSalary": {"$avg": "$net_salary"},
                    "totalOvertime": {"$sum": "$overtime_amount"},
                    "totalDeductions": {"$sum": "$total_deductions"},
                    "totalGross": {"$sum": "$gross_salary"}
                }
            }
        ]
        
        stats = await Payroll.aggregate(pipeline).to_list()
        overall_stats = stats[0] if stats else {}
        
        # Department breakdown
        dept_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$department",
                    "totalAmount": {"$sum": "$net_salary"},
                    "employeeCount": {"$sum": 1},
                    "avgSalary": {"$avg": "$net_salary"}
                }
            },
            {"$sort": {"totalAmount": -1}}
        ]
        
        department_breakdown = await Payroll.aggregate(dept_pipeline).to_list()
        
        # Monthly trend (if no specific month provided)
        monthly_trend = []
        if not payroll_month:
            # Get last 12 months
            today = date.today()
            for i in range(12):
                month_date = today.replace(day=1) - timedelta(days=30 * i)
                month_str = generate_payroll_month_year(month_date.month, month_date.year)
                
                month_pipeline = [
                    {"$match": {"payroll_month": month_str}},
                    {
                        "$group": {
                            "_id": None,
                            "totalAmount": {"$sum": "$net_salary"},
                            "employeeCount": {"$sum": 1}
                        }
                    }
                ]
                
                month_stats = await Payroll.aggregate(month_pipeline).to_list()
                month_data = month_stats[0] if month_stats else {"totalAmount": 0, "employeeCount": 0}
                
                monthly_trend.append({
                    "month": month_str,
                    "total_amount": month_data["totalAmount"],
                    "employee_count": month_data["employeeCount"]
                })
        
        # Allowance breakdown
        allowance_pipeline = [
            {"$match": query},
            {"$unwind": "$allowances"},
            {
                "$group": {
                    "_id": "$allowances.type",
                    "totalAmount": {"$sum": "$allowances.amount"}
                }
            },
            {"$sort": {"totalAmount": -1}}
        ]
        
        allowance_breakdown = await Payroll.aggregate(allowance_pipeline).to_list()
        allowance_dict = {item["_id"]: item["totalAmount"] for item in allowance_breakdown}
        
        # Deduction breakdown
        deduction_pipeline = [
            {"$match": query},
            {"$unwind": "$deductions"},
            {
                "$group": {
                    "_id": "$deductions.type",
                    "totalAmount": {"$sum": "$deductions.amount"}
                }
            },
            {"$sort": {"totalAmount": -1}}
        ]
        
        deduction_breakdown = await Payroll.aggregate(deduction_pipeline).to_list()
        deduction_dict = {item["_id"]: item["totalAmount"] for item in deduction_breakdown}
        
        return {
            "total_payroll_amount": overall_stats.get("totalAmount", 0),
            "total_employees": overall_stats.get("totalEmployees", 0),
            "average_salary": overall_stats.get("avgSalary", 0),
            "total_overtime_amount": overall_stats.get("totalOvertime", 0),
            "total_deductions": overall_stats.get("totalDeductions", 0),
            "department_breakdown": department_breakdown,
            "monthly_trend": monthly_trend,
            "allowance_breakdown": allowance_dict,
            "deduction_breakdown": deduction_dict
        }
    
    async def bulk_update_payrolls(
        self,
        payroll_ids: List[str],
        update_data: Dict[str, Any],
        modified_by: str = None
    ) -> int:
        """Bulk update payrolls"""
        result = await Payroll.find(
            {"_id": {"$in": [PydanticObjectId(id) for id in payroll_ids]}}
        ).update(
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def bulk_approve_payrolls(self, payroll_ids: List[str], approved_by: str) -> int:
        """Bulk approve payrolls"""
        approved_count = 0
        for payroll_id in payroll_ids:
            payroll = await self.approve_payroll(payroll_id, approved_by)
            if payroll:
                approved_count += 1
        
        return approved_count
    
    async def bulk_process_payrolls(
        self, 
        payroll_ids: List[str], 
        processed_by: str,
        transaction_ids: Optional[Dict[str, str]] = None
    ) -> int:
        """Bulk process payrolls"""
        processed_count = 0
        for payroll_id in payroll_ids:
            transaction_id = transaction_ids.get(payroll_id) if transaction_ids else None
            payroll = await self.process_payroll(payroll_id, processed_by, transaction_id)
            if payroll:
                processed_count += 1
        
        return processed_count
    
    async def get_yearly_summary(self, employee_id: str, year: int) -> Dict[str, Any]:
        """Get yearly payroll summary for an employee"""
        # Get all payrolls for the year
        months = []
        for month in range(1, 13):
            months.append(generate_payroll_month_year(month, year))
        
        payrolls = await Payroll.find({
            "employee_id": employee_id,
            "payroll_month": {"$in": months}
        }).sort(Payroll.payroll_month, ASCENDING).to_list()
        
        if not payrolls:
            return {}
        
        # Calculate yearly totals
        total_ctc = sum(p.gross_salary for p in payrolls)
        total_gross = sum(p.gross_salary for p in payrolls)
        total_net = sum(p.net_salary for p in payrolls)
        total_overtime = sum(p.overtime_amount for p in payrolls)
        total_deductions = sum(p.total_deductions for p in payrolls)
        
        # Monthly breakdown
        monthly_breakdown = []
        for payroll in payrolls:
            monthly_breakdown.append({
                "month": payroll.payroll_month,
                "gross_salary": payroll.gross_salary,
                "net_salary": payroll.net_salary,
                "overtime_amount": payroll.overtime_amount,
                "deductions": payroll.total_deductions
            })
        
        return {
            "year": year,
            "employee_id": employee_id,
            "employee_code": payrolls[0].employee_code,
            "employee_name": payrolls[0].employee_name,
            "department": payrolls[0].department,
            "total_ctc": total_ctc,
            "total_gross_salary": total_gross,
            "total_net_salary": total_net,
            "total_overtime_amount": total_overtime,
            "total_deductions": total_deductions,
            "average_monthly_salary": total_net / len(payrolls),
            "monthly_breakdown": monthly_breakdown
        }
    
    async def get_compliance_report(self, payroll_month: str) -> Dict[str, Any]:
        """Generate compliance report for a month"""
        payrolls = await self.get_payrolls_by_month(payroll_month)
        
        total_employees = len(payrolls)
        
        # PF compliance
        pf_compliant = len([p for p in payrolls if p.pf_employee > 0])
        pf_non_compliant = total_employees - pf_compliant
        total_pf = sum(p.pf_employee + p.pf_employer for p in payrolls)
        
        # ESI compliance
        esi_compliant = len([p for p in payrolls if p.esi_employee > 0])
        esi_non_compliant = total_employees - esi_compliant
        total_esi = sum(p.esi_employee + p.esi_employer for p in payrolls)
        
        # PT compliance
        pt_compliant = len([p for p in payrolls if p.professional_tax > 0])
        pt_non_compliant = total_employees - pt_compliant
        total_pt = sum(p.professional_tax for p in payrolls)
        
        # Tax compliance
        tax_compliant = len([p for p in payrolls if p.income_tax > 0])
        tax_non_compliant = total_employees - tax_compliant
        total_tax = sum(p.income_tax for p in payrolls)
        
        # Issues
        compliance_issues = []
        
        # Check for missing statutory deductions
        for payroll in payrolls:
            issues = []
            
            if payroll.gross_salary > 15000 and payroll.pf_employee == 0:
                issues.append("PF deduction missing")
            
            if payroll.gross_salary <= 21000 and payroll.esi_employee == 0:
                issues.append("ESI deduction missing")
            
            if payroll.gross_salary > 10000 and payroll.professional_tax == 0:
                issues.append("Professional tax deduction missing")
            
            if payroll.taxable_income > 250000 and payroll.income_tax == 0:
                issues.append("Income tax deduction missing")
            
            if issues:
                compliance_issues.append({
                    "employee_code": payroll.employee_code,
                    "employee_name": payroll.employee_name,
                    "issues": issues
                })
        
        return {
            "period": payroll_month,
            "total_employees": total_employees,
            "compliant_employees": total_employees - len(compliance_issues),
            "non_compliant_employees": len(compliance_issues),
            "pf_compliant": pf_compliant,
            "pf_non_compliant": pf_non_compliant,
            "total_pf_contribution": total_pf,
            "esi_compliant": esi_compliant,
            "esi_non_compliant": esi_non_compliant,
            "total_esi_contribution": total_esi,
            "pt_compliant": pt_compliant,
            "pt_non_compliant": pt_non_compliant,
            "total_pt_deduction": total_pt,
            "tax_compliant": tax_compliant,
            "tax_non_compliant": tax_non_compliant,
            "total_tax_deduction": total_tax,
            "compliance_issues": compliance_issues
        }
    
    async def add_allowance_to_payroll(
        self, 
        payroll_id: str, 
        allowance_data: PayrollAllowance
    ) -> Optional[Payroll]:
        """Add allowance to payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        payroll.add_allowance(AllowanceType(allowance_data.allowance_type), allowance_data.amount, allowance_data.description)
        await payroll.calculate_payroll()
        
        return payroll
    
    async def add_deduction_to_payroll(
        self, 
        payroll_id: str, 
        deduction_data: PayrollDeduction
    ) -> Optional[Payroll]:
        """Add deduction to payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        payroll.add_deduction(DeductionType(deduction_data.deduction_type), deduction_data.amount, deduction_data.description)
        await payroll.calculate_payroll()
        
        return payroll
    
    async def add_adjustment_to_payroll(
        self, 
        payroll_id: str, 
        adjustment_data: PayrollAdjustment
    ) -> Optional[Payroll]:
        """Add adjustment to payroll"""
        payroll = await self.get_payroll_by_id(payroll_id)
        if not payroll:
            return None
        
        payroll.add_adjustment(adjustment_data.adjustment_type, adjustment_data.amount, adjustment_data.description)
        await payroll.calculate_payroll()
        
        return payroll
