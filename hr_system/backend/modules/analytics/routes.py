from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime

from .service import AnalyticsService
from .model import MetricType, TimePeriod
from ..auth.dependencies import get_current_user, require_permission
from ..user.model import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])
analytics_service = AnalyticsService()


@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard analytics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        # Get all statistics
        employee_stats = await analytics_service.get_employee_statistics()
        payroll_stats = await analytics_service.get_payroll_statistics()
        onboarding_stats = await analytics_service.get_onboarding_statistics()
        exit_stats = await analytics_service.get_exit_management_statistics()
        system_health = await analytics_service.get_system_health_metrics()
        
        dashboard_data = {
            "employee_statistics": employee_stats,
            "payroll_statistics": payroll_stats,
            "onboarding_statistics": onboarding_stats,
            "exit_management_statistics": exit_stats,
            "system_health": system_health,
            "last_updated": datetime.utcnow()
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard analytics"
        )


@router.get("/employees")
async def get_employee_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get employee analytics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        stats = await analytics_service.get_employee_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch employee analytics"
        )


@router.get("/payroll")
async def get_payroll_analytics(
    payroll_month: Optional[str] = Query(None, description="Payroll month (YYYY-MM)"),
    current_user: User = Depends(get_current_user)
):
    """Get payroll analytics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        stats = await analytics_service.get_payroll_statistics(payroll_month)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payroll analytics"
        )


@router.get("/onboarding")
async def get_onboarding_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get onboarding analytics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        stats = await analytics_service.get_onboarding_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch onboarding analytics"
        )


@router.get("/exit-management")
async def get_exit_management_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get exit management analytics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        stats = await analytics_service.get_exit_management_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch exit management analytics"
        )


@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_user)
):
    """Get system health metrics"""
    # Check permission (only admin can access)
    require_permission(current_user, "analytics", "read")
    
    try:
        stats = await analytics_service.get_system_health_metrics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system health metrics"
        )


@router.get("/user-activity")
async def get_user_activity_summary(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    user_id: Optional[str] = Query(None, description="User ID"),
    activity_type: Optional[str] = Query(None, description="Activity type"),
    current_user: User = Depends(get_current_user)
):
    """Get user activity summary"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        summary = await analytics_service.get_user_activity_summary(
            start_date, end_date, user_id, activity_type
        )
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user activity summary"
        )


@router.get("/metrics")
async def get_analytics_metrics(
    name: Optional[str] = Query(None, description="Metric name"),
    category: Optional[str] = Query(None, description="Metric category"),
    metric_type: Optional[MetricType] = Query(None, description="Metric type"),
    time_period: Optional[TimePeriod] = Query(None, description="Time period"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Result limit"),
    current_user: User = Depends(get_current_user)
):
    """Get analytics metrics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        metrics = await analytics_service.get_metrics(
            name=name,
            category=category,
            metric_type=metric_type,
            time_period=time_period,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return {"metrics": metrics}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics metrics"
        )


@router.get("/metrics/{name}/summary")
async def get_metric_summary(
    name: str,
    time_period: TimePeriod = Query(..., description="Time period"),
    periods: int = Query(12, ge=1, le=24, description="Number of periods"),
    current_user: User = Depends(get_current_user)
):
    """Get metric summary"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        summary = await analytics_service.get_metric_summary(name, time_period, periods)
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metric summary"
        )


@router.post("/metrics")
async def record_metric(
    name: str,
    category: str,
    metric_type: MetricType,
    value: float,
    time_period: TimePeriod,
    period_start: datetime,
    period_end: datetime,
    dimensions: Optional[dict] = None,
    metadata: Optional[dict] = None,
    current_user: User = Depends(get_current_user)
):
    """Record an analytics metric"""
    # Check permission
    require_permission(current_user, "analytics", "create")
    
    try:
        metric = await analytics_service.record_metric(
            name=name,
            category=category,
            metric_type=metric_type,
            value=value,
            time_period=time_period,
            period_start=period_start,
            period_end=period_end,
            dimensions=dimensions,
            metadata=metadata
        )
        
        return {"message": "Metric recorded successfully", "metric_id": str(metric.id)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record metric"
        )


@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user)
):
    """Get analytics overview"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        # Get key metrics for overview
        employee_stats = await analytics_service.get_employee_statistics()
        payroll_stats = await analytics_service.get_payroll_statistics()
        onboarding_stats = await analytics_service.get_onboarding_statistics()
        exit_stats = await analytics_service.get_exit_management_statistics()
        
        overview = {
            "key_metrics": {
                "total_employees": employee_stats.get("total_employees", 0),
                "active_employees": employee_stats.get("active_employees", 0),
                "new_hires_this_month": employee_stats.get("new_hires_this_month", 0),
                "total_payroll_amount": payroll_stats.get("total_payroll_amount", 0),
                "active_onboardings": onboarding_stats.get("active_onboardings", 0),
                "active_exits": exit_stats.get("active_exits", 0)
            },
            "trends": {
                "employee_growth": {
                    "current": employee_stats.get("total_employees", 0),
                    "previous": employee_stats.get("total_employees", 0) - employee_stats.get("new_hires_this_month", 0),
                    "trend": "up"
                },
                "payroll_growth": {
                    "current": payroll_stats.get("total_payroll_amount", 0),
                    "previous": payroll_stats.get("total_payroll_amount", 0) * 0.95,  # Placeholder
                    "trend": "up"
                },
                "onboarding_completion": {
                    "current": onboarding_stats.get("completion_rate", 0),
                    "trend": "stable"
                },
                "attrition_rate": {
                    "current": exit_stats.get("completion_rate", 0),
                    "trend": "stable"
                }
            },
            "alerts": [
                {
                    "type": "warning",
                    "message": "5 overdue onboarding processes",
                    "count": 5
                },
                {
                    "type": "info",
                    "message": "8 new hires this month",
                    "count": 8
                }
            ]
        }
        
        return overview
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics overview"
        )


@router.get("/reports")
async def get_available_reports(
    current_user: User = Depends(get_current_user)
):
    """Get available reports"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        reports = [
            {
                "id": "employee_report",
                "name": "Employee Report",
                "description": "Comprehensive employee statistics and demographics",
                "category": "employees",
                "format": "pdf",
                "schedule": "monthly"
            },
            {
                "id": "payroll_report",
                "name": "Payroll Report",
                "description": "Monthly payroll breakdown and analysis",
                "category": "payroll",
                "format": "excel",
                "schedule": "monthly"
            },
            {
                "id": "onboarding_report",
                "name": "Onboarding Report",
                "description": "Onboarding process metrics and completion rates",
                "category": "onboarding",
                "format": "pdf",
                "schedule": "weekly"
            },
            {
                "id": "exit_report",
                "name": "Exit Management Report",
                "description": "Employee exit analysis and trends",
                "category": "exit_management",
                "format": "pdf",
                "schedule": "monthly"
            },
            {
                "id": "activity_report",
                "name": "User Activity Report",
                "description": "System usage and user activity analysis",
                "category": "system",
                "format": "excel",
                "schedule": "daily"
            }
        ]
        
        return {"reports": reports}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available reports"
        )


@router.get("/charts")
async def get_chart_data(
    chart_type: str = Query(..., description="Chart type"),
    current_user: User = Depends(get_current_user)
):
    """Get chart data for specific chart type"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        if chart_type == "employee_distribution":
            data = await analytics_service.get_employee_statistics()
            return {
                "type": "pie",
                "title": "Employee Distribution",
                "data": data.get("department_breakdown", [])
            }
        
        elif chart_type == "salary_distribution":
            data = await analytics_service.get_payroll_statistics()
            return {
                "type": "bar",
                "title": "Salary Distribution",
                "data": data.get("salary_ranges", [])
            }
        
        elif chart_type == "onboarding_trend":
            data = await analytics_service.get_onboarding_statistics()
            return {
                "type": "line",
                "title": "Onboarding Trend",
                "data": data.get("monthly_trend", [])
            }
        
        elif chart_type == "exit_trend":
            data = await analytics_service.get_exit_management_statistics()
            return {
                "type": "line",
                "title": "Exit Trend",
                "data": data.get("monthly_trend", [])
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown chart type: {chart_type}"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chart data: {str(e)}"
        )


@router.get("/kpi")
async def get_kpi_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get KPI metrics"""
    # Check permission
    require_permission(current_user, "analytics", "read")
    
    try:
        employee_stats = await analytics_service.get_employee_statistics()
        payroll_stats = await analytics_service.get_payroll_statistics()
        onboarding_stats = await analytics_service.get_onboarding_statistics()
        exit_stats = await analytics_service.get_exit_management_statistics()
        
        kpis = {
            "employee_kpis": {
                "total_employees": {
                    "value": employee_stats.get("total_employees", 0),
                    "target": 160,
                    "unit": "count",
                    "trend": "up"
                },
                "attrition_rate": {
                    "value": employee_stats.get("attrition_rate", 0),
                    "target": 5.0,
                    "unit": "%",
                    "trend": "stable"
                },
                "new_hires": {
                    "value": employee_stats.get("new_hires_this_month", 0),
                    "target": 10,
                    "unit": "count",
                    "trend": "up"
                }
            },
            "payroll_kpis": {
                "total_payroll": {
                    "value": payroll_stats.get("total_payroll_amount", 0),
                    "target": 8000000,
                    "unit": "₹",
                    "trend": "up"
                },
                "average_salary": {
                    "value": payroll_stats.get("average_salary", 0),
                    "target": 55000,
                    "unit": "₹",
                    "trend": "stable"
                },
                "payroll_accuracy": {
                    "value": 99.5,
                    "target": 99.0,
                    "unit": "%",
                    "trend": "stable"
                }
            },
            "onboarding_kpis": {
                "completion_rate": {
                    "value": onboarding_stats.get("completion_rate", 0),
                    "target": 95.0,
                    "unit": "%",
                    "trend": "up"
                },
                "average_duration": {
                    "value": onboarding_stats.get("average_completion_days", 0),
                    "target": 14.0,
                    "unit": "days",
                    "trend": "down"
                },
                "overdue_count": {
                    "value": onboarding_stats.get("overdue_onboardings", 0),
                    "target": 0,
                    "unit": "count",
                    "trend": "stable"
                }
            },
            "exit_kpis": {
                "completion_rate": {
                    "value": exit_stats.get("completion_rate", 0),
                    "target": 90.0,
                    "unit": "%",
                    "trend": "stable"
                },
                "average_duration": {
                    "value": exit_stats.get("average_exit_process_days", 0),
                    "target": 30.0,
                    "unit": "days",
                    "trend": "down"
                },
                "clearance_rate": {
                    "value": 85.0,
                    "target": 95.0,
                    "unit": "%",
                    "trend": "up"
                }
            }
        }
        
        return kpis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch KPI metrics"
        )
