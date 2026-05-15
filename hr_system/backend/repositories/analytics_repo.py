from typing import Optional, List
from datetime import datetime, date, timedelta
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

from modules.analytics.model import (
    AnalyticsMetric, Dashboard, Report, Alert, AlertHistory, UserActivity, 
    SystemMetrics, DataQualityMetrics
)


class AnalyticsRepository:
    """Repository for analytics operations"""
    
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
        # Build query
        query = {}
        
        if name:
            query["name"] = name
        if category:
            query["category"] = category
        if metric_type:
            query["metric_type"] = metric_type
        if time_period:
            query["time_period"] = time_period
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["period_start"] = date_query
        
        # Get metrics
        metrics = await AnalyticsMetric.find(query).sort(
            "-period_start"
        ).limit(limit).to_list()
        
        return metrics
    
    async def get_previous_metric(
        self, 
        name: str, 
        category: str, 
        time_period: TimePeriod, 
        current_start: datetime
    ) -> Optional[AnalyticsMetric]:
        """Get previous metric for comparison"""
        return await AnalyticsMetric.find_one({
            "name": name,
            "category": category,
            "time_period": time_period,
            "period_end": {"$lt": current_start}
        }).sort("-period_end")
    
    async def get_user_activity_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> dict:
        """Get user activity summary"""
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
    
    async def get_dashboard_by_id(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        try:
            return await Dashboard.get(PydanticObjectId(dashboard_id))
        except:
            return None
    
    async def get_dashboards_by_category(self, category: str) -> List[Dashboard]:
        """Get dashboards by category"""
        return await Dashboard.find(
            {"category": category, "is_active": True}
        ).sort(Dashboard.title, ASCENDING).to_list()
    
    async def get_report_by_id(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        try:
            return await Report.get(PydanticObjectId(report_id))
        except:
            return None
    
    async def get_reports_by_category(self, category: str) -> List[Report]:
        """Get reports by category"""
        return await Report.find(
            {"category": category, "is_active": True}
        ).sort(Report.title, ASCENDING).to_list()
    
    async def create_alert(self, alert_data) -> Alert:
        """Create a new alert"""
        alert = Alert(**alert_data.dict())
        await alert.insert()
        return alert
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return await Alert.find(
            {"is_active": True}
        ).sort(Alert.created_at, DESCENDING).to_list()
    
    async def get_alerts_by_metric(self, metric_name: str) -> List[Alert]:
        """Get alerts for a specific metric"""
        return await Alert.find(
            {"metric_name": metric_name, "is_active": True}
        ).sort(Alert.created_at, DESCENDING).to_list()
    
    async def trigger_alert(self, alert_id: str, metric_value: float) -> AlertHistory:
        """Trigger an alert"""
        alert = await Alert.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        
        # Create alert history record
        alert_history = AlertHistory(
            alert_id=str(alert.id),
            alert_name=alert.name,
            triggered_at=datetime.utcnow(),
            metric_value=metric_value,
            threshold=alert.threshold,
            status="active"
        )
        
        await alert_history.insert()
        
        # Update alert
        alert.last_triggered = datetime.utcnow()
        alert.trigger_count += 1
        await alert.save()
        
        return alert_history
    
    async def get_alert_history(self, alert_id: str, limit: int = 50) -> List[AlertHistory]:
        """Get alert history"""
        return await AlertHistory.find(
            {"alert_id": alert_id}
        ).sort(AlertHistory.triggered_at, DESCENDING).limit(limit).to_list()
    
    async def record_user_activity(
        self,
        user_id: str,
        user_email: str,
        user_role: str,
        activity_type: str,
        resource_type: str,
        action: str,
        ip_address: str,
        user_agent: str,
        endpoint: str,
        method: str,
        status_code: int,
        success: bool,
        resource_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UserActivity:
        """Record user activity"""
        activity = UserActivity(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            activity_type=activity_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        await activity.insert()
        return activity
    
    async def record_system_metric(
        self,
        metric_name: str,
        category: str,
        value: float,
        unit: str,
        hostname: str,
        service: str,
        version: str,
        tags: Optional[dict] = None,
        metadata: Optional[dict] = None
    ) -> SystemMetrics:
        """Record system metric"""
        metric = SystemMetrics(
            metric_name=metric_name,
            category=category,
            value=value,
            unit=unit,
            hostname=hostname,
            service=service,
            version=version,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        await metric.insert()
        return metric
    
    async def get_system_metrics(
        self,
        metric_name: Optional[str] = None,
        category: Optional[str] = None,
        service: Optional[str] = None,
        hours: int = 24
    ) -> List[SystemMetrics]:
        """Get system metrics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = {
            "timestamp": {"$gte": cutoff_time}
        }
        
        if metric_name:
            query["metric_name"] = metric_name
        if category:
            query["category"] = category
        if service:
            query["service"] = service
        
        return await SystemMetrics.find(query).sort(
            SystemMetrics.timestamp, DESCENDING
        ).to_list()
    
    async def record_data_quality_metrics(
        self,
        table_name: str,
        metric_type: str,
        total_records: int,
        valid_records: int,
        invalid_records: int,
        duplicate_records: int,
        missing_values: int,
        completeness_score: float,
        accuracy_score: float,
        consistency_score: float,
        overall_quality_score: float,
        validation_rules: Optional[list] = None,
        issues_found: Optional[list] = None
    ) -> DataQualityMetrics:
        """Record data quality metrics"""
        metric = DataQualityMetrics(
            table_name=table_name,
            metric_type=metric_type,
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            duplicate_records=duplicate_records,
            missing_values=missing_values,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            overall_quality_score=overall_quality_score,
            validation_rules=validation_rules or [],
            issues_found=issues_found or []
        )
        
        await metric.insert()
        return metric
    
    async def get_data_quality_metrics(
        self,
        table_name: Optional[str] = None,
        metric_type: Optional[str] = None,
        days: int = 7
    ) -> List[DataQualityMetrics]:
        """Get data quality metrics"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        query = {
            "timestamp": {"$gte": cutoff_time}
        }
        
        if table_name:
            query["table_name"] = table_name
        if metric_type:
            query["metric_type"] = metric_type
        
        return await DataQualityMetrics.find(query).sort(
            DataQualityMetrics.timestamp, DESCENDING
        ).to_list()
    
    async def cleanup_old_metrics(self, days: int = 90) -> int:
        """Clean up old metrics"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Clean up old user activities
        user_activities_deleted = await UserActivity.find(
            {"timestamp": {"$lt": cutoff_time}}
        ).delete()
        
        # Clean up old system metrics
        system_metrics_deleted = await SystemMetrics.find(
            {"timestamp": {"$lt": cutoff_time}}
        ).delete()
        
        # Clean up old alert history
        alert_history_deleted = await AlertHistory.find(
            {"triggered_at": {"$lt": cutoff_time}}
        ).delete()
        
        total_deleted = (
            user_activities_deleted.deleted_count +
            system_metrics_deleted.deleted_count +
            alert_history_deleted.deleted_count
        )
        
        return total_deleted
