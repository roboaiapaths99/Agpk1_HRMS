from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from modules.analytics.model import MetricType, TimePeriod


class MetricRequest(BaseModel):
    """Request schema for analytics metrics"""
    metric_type: MetricType
    time_period: TimePeriod
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MetricResponse(BaseModel):
    """Response schema for analytics metrics"""
    metric_type: MetricType
    time_period: TimePeriod
    value: float
    unit: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DashboardData(BaseModel):
    """Dashboard analytics response"""
    total_employees: int
    active_employees: int
    new_hires: int
    departures: int
    payroll_total: float
    attendance_rate: float
    metrics: List[MetricResponse]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: str
    time_period: TimePeriod
    format: str = Field(default="pdf", pattern="^(pdf|excel|csv)$")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    """Report generation response"""
    report_id: str
    download_url: str
    expires_at: datetime
    file_size: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)
