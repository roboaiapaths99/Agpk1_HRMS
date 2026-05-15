from datetime import datetime, date
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field
from enum import Enum


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    AVERAGE = "average"
    SUM = "sum"
    PERCENTAGE = "percentage"


class TimePeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AnalyticsMetric(Document):
    """Analytics metric document"""
    
    # Metric identification
    name: Indexed(str) = Field(..., description="Metric name")
    category: str = Field(..., description="Metric category")
    metric_type: MetricType = Field(..., description="Type of metric")
    time_period: TimePeriod = Field(..., description="Time period for the metric")
    
    # Metric data
    value: float = Field(..., description="Metric value")
    previous_value: Optional[float] = Field(None, description="Previous period value for comparison")
    change_percentage: Optional[float] = Field(None, description="Percentage change from previous period")
    
    # Time information
    period_start: datetime = Field(..., description="Start of the period")
    period_end: datetime = Field(..., description="End of the period")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When metric was recorded")
    
    # Additional data
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Additional dimensions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analytics_metrics"
        indexes = [
            "name",
            "category",
            "time_period",
            "period_start",
            "period_end",
            "recorded_at"
        ]
    
    def calculate_change_percentage(self):
        """Calculate percentage change from previous value"""
        if self.previous_value and self.previous_value != 0:
            self.change_percentage = ((self.value - self.previous_value) / self.previous_value) * 100
        else:
            self.change_percentage = None


class Dashboard(Document):
    """Dashboard configuration document"""
    
    # Dashboard identification
    name: Indexed(str) = Field(..., description="Dashboard name")
    title: str = Field(..., description="Dashboard title")
    description: Optional[str] = Field(None, description="Dashboard description")
    category: str = Field(..., description="Dashboard category")
    
    # Dashboard configuration
    layout: Dict[str, Any] = Field(..., description="Dashboard layout configuration")
    widgets: List[Dict[str, Any]] = Field(..., description="Dashboard widgets")
    filters: List[Dict[str, Any]] = Field(default_factory=list, description="Available filters")
    
    # Access control
    roles: List[str] = Field(default_factory=list, description="Roles that can access this dashboard")
    is_public: bool = Field(default=False, description="Whether dashboard is public")
    is_active: bool = Field(default=True, description="Whether dashboard is active")
    
    # Metadata
    created_by: str = Field(..., description="User who created the dashboard")
    last_modified_by: Optional[str] = Field(None, description="User who last modified the dashboard")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "dashboards"
        indexes = [
            "name",
            "category",
            "roles",
            "is_active",
            "created_at"
        ]


class Report(Document):
    """Report configuration document"""
    
    # Report identification
    name: Indexed(str) = Field(..., description="Report name")
    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(None, description="Report description")
    category: str = Field(..., description="Report category")
    
    # Report configuration
    query: Dict[str, Any] = Field(..., description="Report query configuration")
    template: str = Field(..., description="Report template")
    format: str = Field(default="pdf", description="Report format")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Report schedule")
    
    # Access control
    roles: List[str] = Field(default_factory=list, description="Roles that can access this report")
    is_public: bool = Field(default=False, description="Whether report is public")
    is_active: bool = Field(default=True, description="Whether report is active")
    
    # Metadata
    created_by: str = Field(..., description="User who created the report")
    last_modified_by: Optional[str] = Field(None, description="User who last modified the report")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reports"
        indexes = [
            "name",
            "category",
            "roles",
            "is_active",
            "created_at"
        ]


class Alert(Document):
    """Alert configuration document"""
    
    # Alert identification
    name: Indexed(str) = Field(..., description="Alert name")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    category: str = Field(..., description="Alert category")
    
    # Alert configuration
    metric_name: str = Field(..., description="Metric to monitor")
    condition: Dict[str, Any] = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    comparison: str = Field(..., description="Comparison operator (gt, lt, eq, gte, lte)")
    
    # Notification settings
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    notification_users: List[str] = Field(default_factory=list, description="Users to notify")
    notification_roles: List[str] = Field(default_factory=list, description="Roles to notify")
    
    # Status
    is_active: bool = Field(default=True, description="Whether alert is active")
    last_triggered: Optional[datetime] = Field(None, description="When alert was last triggered")
    trigger_count: int = Field(default=0, description="Number of times alert was triggered")
    
    # Metadata
    created_by: str = Field(..., description="User who created the alert")
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "alerts"
        indexes = [
            "name",
            "category",
            "metric_name",
            "is_active",
            "last_triggered"
        ]


class AlertHistory(Document):
    """Alert history document"""
    
    # Alert identification
    alert_id: str = Field(..., description="Reference to alert")
    alert_name: str = Field(..., description="Alert name")
    
    # Trigger information
    triggered_at: datetime = Field(..., description="When alert was triggered")
    metric_value: float = Field(..., description="Metric value that triggered alert")
    threshold: float = Field(..., description="Alert threshold")
    
    # Resolution
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")
    resolved_by: Optional[str] = Field(None, description="Who resolved the alert")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    
    # Status
    status: str = Field(default="active", description="Alert status (active, resolved, acknowledged)")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged the alert")
    
    # Additional data
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    class Settings:
        name = "alert_history"
        indexes = [
            "alert_id",
            "alert_name",
            "triggered_at",
            "status"
        ]


class UserActivity(Document):
    """User activity tracking document"""
    
    # User identification
    user_id: str = Field(..., description="User ID")
    user_email: str = Field(..., description="User email")
    user_role: str = Field(..., description="User role")
    
    # Activity information
    activity_type: str = Field(..., description="Type of activity")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    action: str = Field(..., description="Action performed")
    
    # Request information
    ip_address: str = Field(..., description="IP address")
    user_agent: str = Field(..., description="User agent string")
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    
    # Status
    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(..., description="Whether request was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When activity occurred")
    duration_ms: Optional[int] = Field(None, description="Request duration in milliseconds")
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Settings:
        name = "user_activity"
        indexes = [
            "user_id",
            "user_email",
            "activity_type",
            "resource_type",
            "action",
            "timestamp",
            "status_code"
        ]


class SystemMetrics(Document):
    """System performance metrics document"""
    
    # Metric identification
    metric_name: str = Field(..., description="Metric name")
    category: str = Field(..., description="Metric category")
    
    # Metric data
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    
    # Time information
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metric was recorded")
    
    # System information
    hostname: str = Field(..., description="Server hostname")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    
    # Additional data
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Settings:
        name = "system_metrics"
        indexes = [
            "metric_name",
            "category",
            "timestamp",
            "hostname",
            "service"
        ]


class DataQualityMetrics(Document):
    """Data quality metrics document"""
    
    # Metric identification
    table_name: str = Field(..., description="Table name")
    metric_type: str = Field(..., description="Type of quality metric")
    
    # Quality metrics
    total_records: int = Field(..., description="Total records processed")
    valid_records: int = Field(..., description="Valid records")
    invalid_records: int = Field(..., description="Invalid records")
    duplicate_records: int = Field(..., description="Duplicate records")
    missing_values: int = Field(..., description="Missing values")
    
    # Quality scores
    completeness_score: float = Field(..., description="Data completeness score")
    accuracy_score: float = Field(..., description="Data accuracy score")
    consistency_score: float = Field(..., description="Data consistency score")
    overall_quality_score: float = Field(..., description="Overall quality score")
    
    # Time information
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metric was recorded")
    
    # Additional data
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Validation rules applied")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="Issues found")
    
    class Settings:
        name = "data_quality_metrics"
        indexes = [
            "table_name",
            "metric_type",
            "timestamp",
            "overall_quality_score"
        ]
