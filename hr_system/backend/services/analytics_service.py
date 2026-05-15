from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

from modules.analytics.model import (
    AnalyticsMetric, Dashboard, Report, Alert, AlertHistory, UserActivity, 
    SystemMetrics, DataQualityMetrics
)
from schemas.analytics_schema import MetricRequest, MetricResponse, DashboardData, ReportRequest, ReportResponse
from repositories.analytics_repo import AnalyticsRepository
from utils.logger import audit_logger


class AnalyticsService:
    """Service layer for analytics operations"""
    
    def __init__(self):
        self.repository = AnalyticsRepository()
    
    async def record_metric(
        self,
        name: str,
        category: str,
        metric_type: MetricType,
        value: float,
        time_period: TimePeriod,
        period_start: datetime,
        period_end: datetime,
        dimensions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalyticsMetric:
        """Record an analytics metric"""
        try:
            # Get previous value for comparison
            previous_metric = await self.repository.get_previous_metric(
                name, category, time_period, period_start
            )
            
            previous_value = previous_metric.value if previous_metric else None
            
            # Create metric
            metric = AnalyticsMetric(
                name=name,
                category=category,
                metric_type=metric_type,
                value=value,
                previous_value=previous_value,
                time_period=time_period,
                period_start=period_start,
                period_end=period_end,
                dimensions=dimensions or {},
                metadata=metadata or {}
            )
            
            # Calculate change percentage
            metric.calculate_change_percentage()
            
            await metric.insert()
            
            return metric
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record metric: {str(e)}"
            )
    
    async def get_metrics(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        time_period: Optional[TimePeriod] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AnalyticsMetric]:
        """Get analytics metrics"""
        try:
            return await self.repository.get_metrics(
                name, category, metric_type, time_period, start_date, end_date, limit
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch metrics: {str(e)}"
            )
    
    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Get employee statistics"""
        try:
            # Mock data for now - replace with actual database queries
            return {
                "total_employees": 150,
                "active_employees": 142,
                "new_hires_this_month": 8,
                "departures_this_month": 2,
                "department_distribution": {
                    "Engineering": 45,
                    "Sales": 30,
                    "HR": 15,
                    "Finance": 20,
                    "Operations": 40
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_payroll_statistics(self) -> Dict[str, Any]:
        """Get payroll statistics"""
        try:
            return {
                "total_payroll_this_month": 2500000,
                "average_salary": 16666.67,
                "payroll_growth_rate": 5.2,
                "pending_approvals": 3,
                "processed_today": 12
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_onboarding_statistics(self) -> Dict[str, Any]:
        """Get onboarding statistics"""
        try:
            return {
                "active_onboarding": 8,
                "completed_this_month": 12,
                "average_completion_time": 4.5,
                "pending_tasks": 15,
                "completion_rate": 85.5
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_exit_management_statistics(self) -> Dict[str, Any]:
        """Get exit management statistics"""
        try:
            return {
                "active_exits": 3,
                "completed_this_month": 2,
                "average_exit_time": 7.2,
                "pending_clearances": 5,
                "satisfaction_score": 4.2
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            return {
                "system_uptime": 99.9,
                "api_response_time": 120,
                "database_performance": 95.5,
                "error_rate": 0.1,
                "active_users": 45
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_metric_summary(
        self,
        name: str,
        time_period: TimePeriod,
        periods: int = 12
    ) -> Dict[str, Any]:
        """Get metric summary for multiple periods"""
        try:
            # Get metrics for the specified number of periods
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=periods * 30)  # Approximate
            
            metrics = await self.get_metrics(
                name=name,
                time_period=time_period,
                start_date=start_date,
                end_date=end_date,
                limit=periods
            )
            
            if not metrics:
                return {"name": name, "time_period": time_period, "data": []}
            
            # Calculate summary
            values = [m.value for m in metrics]
            current_value = values[0] if values else 0
            previous_value = values[1] if len(values) > 1 else 0
            
            summary = {
                "name": name,
                "time_period": time_period,
                "current_value": current_value,
                "previous_value": previous_value,
                "change_percentage": ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0,
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "trend": "up" if current_value > previous_value else "down" if current_value < previous_value else "stable",
                "data": [
                    {
                        "period_start": m.period_start,
                        "period_end": m.period_end,
                        "value": m.value,
                        "change_percentage": m.change_percentage
                    }
                    for m in metrics
                ]
            }
            
            return summary
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get metric summary: {str(e)}"
            )
    
    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Get employee statistics"""
        try:
            # This would integrate with employee repository
            # For now, return placeholder data
            
            stats = {
                "total_employees": 150,  # Placeholder
                "active_employees": 142,
                "new_hires_this_month": 8,
                "employees_on_probation": 12,
                "employees_leaving_this_month": 3,
                "attrition_rate": 2.1,
                "department_breakdown": [
                    {"department": "Engineering", "count": 45, "percentage": 30.0},
                    {"department": "Sales", "count": 30, "percentage": 20.0},
                    {"department": "Marketing", "count": 25, "percentage": 16.7},
                    {"department": "HR", "count": 15, "percentage": 10.0},
                    {"department": "Finance", "count": 20, "percentage": 13.3},
                    {"department": "Operations", "count": 15, "percentage": 10.0}
                ],
                "role_breakdown": [
                    {"role": "Software Engineer", "count": 35, "percentage": 23.3},
                    {"role": "Sales Executive", "count": 25, "percentage": 16.7},
                    {"role": "Marketing Manager", "count": 15, "percentage": 10.0},
                    {"role": "HR Executive", "count": 20, "percentage": 13.3},
                    {"role": "Finance Analyst", "count": 18, "percentage": 12.0},
                    {"role": "Operations Manager", "count": 12, "percentage": 8.0},
                    {"role": "Others", "count": 25, "percentage": 16.7}
                ],
                "gender_distribution": [
                    {"gender": "Male", "count": 95, "percentage": 63.3},
                    {"gender": "Female", "count": 52, "percentage": 34.7},
                    {"gender": "Other", "count": 3, "percentage": 2.0}
                ],
                "age_distribution": [
                    {"age_range": "20-25", "count": 25, "percentage": 16.7},
                    {"age_range": "26-30", "count": 45, "percentage": 30.0},
                    {"age_range": "31-35", "count": 40, "percentage": 26.7},
                    {"age_range": "36-40", "count": 25, "percentage": 16.7},
                    {"age_range": "40+", "count": 15, "percentage": 10.0}
                ],
                "experience_distribution": [
                    {"years": "0-2", "count": 35, "percentage": 23.3},
                    {"years": "2-5", "count": 55, "percentage": 36.7},
                    {"years": "5-10", "count": 40, "percentage": 26.7},
                    {"years": "10+", "count": 20, "percentage": 13.3}
                ],
                "location_distribution": [
                    {"location": "Mumbai", "count": 60, "percentage": 40.0},
                    {"location": "Bangalore", "count": 45, "percentage": 30.0},
                    {"location": "Delhi", "count": 30, "percentage": 20.0},
                    {"location": "Remote", "count": 15, "percentage": 10.0}
                ]
            }
            
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get employee statistics: {str(e)}"
            )
    
    async def get_payroll_statistics(self, payroll_month: Optional[str] = None) -> Dict[str, Any]:
        """Get payroll statistics"""
        try:
            # This would integrate with payroll repository
            # For now, return placeholder data
            
            stats = {
                "total_payroll_amount": 7500000.0,  # Placeholder
                "total_employees": 150,
                "average_salary": 50000.0,
                "median_salary": 45000.0,
                "highest_salary": 250000.0,
                "lowest_salary": 15000.0,
                "total_overtime_amount": 125000.0,
                "total_deductions": 1500000.0,
                "department_breakdown": [
                    {"department": "Engineering", "total_amount": 3000000.0, "average": 66666.7},
                    {"department": "Sales", "total_amount": 1500000.0, "average": 50000.0},
                    {"department": "Marketing", "total_amount": 1000000.0, "average": 40000.0},
                    {"department": "HR", "total_amount": 600000.0, "average": 40000.0},
                    {"department": "Finance", "total_amount": 800000.0, "average": 40000.0},
                    {"department": "Operations", "total_amount": 600000.0, "average": 40000.0}
                ],
                "salary_ranges": [
                    {"range": "0-25k", "count": 20, "percentage": 13.3},
                    {"range": "25k-50k", "count": 65, "percentage": 43.3},
                    {"range": "50k-75k", "count": 40, "percentage": 26.7},
                    {"range": "75k-100k", "count": 15, "percentage": 10.0},
                    {"range": "100k+", "count": 10, "percentage": 6.7}
                ],
                "deduction_breakdown": {
                    "pf_employee": 900000.0,
                    "pf_employer": 900000.0,
                    "esi_employee": 150000.0,
                    "esi_employer": 650000.0,
                    "professional_tax": 300000.0,
                    "income_tax": 500000.0
                }
            }
            
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get payroll statistics: {str(e)}"
            )
    
    async def get_onboarding_statistics(self) -> Dict[str, Any]:
        """Get onboarding statistics"""
        try:
            # This would integrate with onboarding repository
            # For now, return placeholder data
            
            stats = {
                "total_onboardings": 142,
                "active_onboardings": 12,
                "completed_onboardings": 125,
                "overdue_onboardings": 5,
                "average_completion_days": 15.5,
                "completion_rate": 88.0,
                "department_breakdown": [
                    {"department": "Engineering", "total": 40, "completed": 35, "active": 5},
                    {"department": "Sales", "total": 28, "completed": 25, "active": 3},
                    {"department": "Marketing", "total": 22, "completed": 20, "active": 2},
                    {"department": "HR", "total": 15, "completed": 14, "active": 1},
                    {"department": "Finance", "total": 18, "completed": 16, "active": 1},
                    {"department": "Operations", "total": 19, "completed": 15, "active": 0}
                ],
                "task_completion_rates": {
                    "documentation": 92.0,
                    "it_setup": 85.0,
                    "hr_briefing": 95.0,
                    "team_introduction": 88.0,
                    "policy_acknowledgment": 90.0,
                    "benefits_enrollment": 87.0
                },
                "monthly_trend": [
                    {"month": "2024-01", "completed": 8, "started": 10},
                    {"month": "2024-02", "completed": 12, "started": 14},
                    {"month": "2024-03", "completed": 10, "started": 12},
                    {"month": "2024-04", "completed": 15, "started": 16},
                    {"month": "2024-05", "completed": 11, "started": 13},
                    {"month": "2024-06", "completed": 9, "started": 11}
                ]
            }
            
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get onboarding statistics: {str(e)}"
            )
    
    async def get_exit_management_statistics(self) -> Dict[str, Any]:
        """Get exit management statistics"""
        try:
            # This would integrate with exit management repository
            # For now, return placeholder data
            
            stats = {
                "total_exits": 25,
                "active_exits": 8,
                "completed_exits": 17,
                "overdue_exits": 2,
                "average_exit_process_days": 45.0,
                "completion_rate": 68.0,
                "exit_reason_breakdown": [
                    {"reason": "resignation", "count": 18, "percentage": 72.0},
                    {"reason": "termination", "count": 4, "percentage": 16.0},
                    {"reason": "retirement", "count": 2, "percentage": 8.0},
                    {"reason": "contract_end", "count": 1, "percentage": 4.0}
                ],
                "department_breakdown": [
                    {"department": "Engineering", "total": 8, "completed": 6, "active": 2},
                    {"department": "Sales", "total": 7, "completed": 5, "active": 2},
                    {"department": "Marketing", "total": 4, "completed": 3, "active": 1},
                    {"department": "HR", "total": 3, "completed": 2, "active": 1},
                    {"department": "Finance", "total": 2, "completed": 1, "active": 1},
                    {"department": "Operations", "total": 1, "completed": 0, "active": 1}
                ],
                "clearance_status": {
                    "hr_clearance": 85.0,
                    "it_clearance": 80.0,
                    "asset_clearance": 90.0,
                    "finance_clearance": 75.0,
                    "admin_clearance": 95.0
                },
                "monthly_trend": [
                    {"month": "2024-01", "exits": 2},
                    {"month": "2024-02", "exits": 3},
                    {"month": "2024-03", "exits": 4},
                    {"month": "2024-04", "exits": 2},
                    {"month": "2024-05", "exits": 5},
                    {"month": "2024-06", "exits": 3}
                ]
            }
            
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get exit management statistics: {str(e)}"
            )
    
    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # This would integrate with system monitoring
            # For now, return placeholder data
            
            stats = {
                "api_response_time": 125.5,  # ms
                "api_success_rate": 99.2,  # %
                "database_response_time": 45.2,  # ms
                "database_connection_pool": 75.0,  # % used
                "memory_usage": 68.5,  # %
                "cpu_usage": 45.2,  # %
                "disk_usage": 32.8,  # %
                "active_users": 45,
                "total_requests_per_minute": 1250,
                "error_rate": 0.8,  # %
                "uptime": 99.95,  # %
                "services": [
                    {"name": "API Server", "status": "healthy", "response_time": 125.5},
                    {"name": "Database", "status": "healthy", "response_time": 45.2},
                    {"name": "Redis Cache", "status": "healthy", "response_time": 2.1},
                    {"name": "File Storage", "status": "healthy", "response_time": 85.3}
                ]
            }
            
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get system health metrics: {str(e)}"
            )
    
    async def get_user_activity_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user activity summary"""
        try:
            # Build query
            query = {}
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["timestamp"] = date_query
            
            if user_id:
                query["user_id"] = user_id
            if activity_type:
                query["activity_type"] = activity_type
            
            # Get total activities
            total_activities = await UserActivity.find(query).count()
            
            # Get successful activities
            successful_activities = await UserActivity.find({
                **query,
                "success": True
            }).count()
            
            # Get failed activities
            failed_activities = await UserActivity.find({
                **query,
                "success": False
            }).count()
            
            # Get activities by type
            pipeline = [
                {"$match": query},
                {"$group": {"_id": "$activity_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            activities_by_type = await UserActivity.aggregate(pipeline).to_list()
            
            # Get activities by user role
            role_pipeline = [
                {"$match": query},
                {"$group": {"_id": "$user_role", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            activities_by_role = await UserActivity.aggregate(role_pipeline).to_list()
            
            # Get average response time
            avg_duration_pipeline = [
                {"$match": {**query, "duration_ms": {"$ne": None}}},
                {"$group": {"_id": None, "avg_duration": {"$avg": "$duration_ms"}}}
            ]
            
            avg_duration_result = await UserActivity.aggregate(avg_duration_pipeline).to_list()
            avg_duration = avg_duration_result[0]["avg_duration"] if avg_duration_result else 0
            
            summary = {
                "total_activities": total_activities,
                "successful_activities": successful_activities,
                "failed_activities": failed_activities,
                "success_rate": (successful_activities / total_activities * 100) if total_activities > 0 else 0,
                "activities_by_type": activities_by_type,
                "activities_by_role": activities_by_role,
                "average_response_time_ms": avg_duration
            }
            
            return summary
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get activity summary: {str(e)}"
            )
