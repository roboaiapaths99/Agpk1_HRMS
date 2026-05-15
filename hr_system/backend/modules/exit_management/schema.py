from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class ExitTaskBase(BaseModel):
    """Base exit task schema"""
    title: str = Field(..., min_length=2, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to: Optional[str] = Field(None, description="Person responsible")
    department: Optional[str] = Field(None, description="Department responsible")
    priority: str = Field(default="medium", description="Task priority")
    due_date: Optional[date] = Field(None, description="Task due date")
    notes: Optional[str] = Field(None, description="Task notes")


class ExitTaskCreate(ExitTaskBase):
    """Schema for creating exit task"""
    pass


class ExitTaskUpdate(BaseModel):
    """Schema for updating exit task"""
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    status: Optional[str] = Field(None, description="Task status")
    priority: Optional[str] = Field(None)
    due_date: Optional[date] = Field(None)
    completed_by: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)


class ExitTaskResponse(BaseModel):
    """Schema for exit task response"""
    id: str
    title: str
    description: Optional[str]
    assigned_to: Optional[str]
    department: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    completed_at: Optional[datetime]
    completed_by: Optional[str]
    attachments: List[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExitManagementBase(BaseModel):
    """Base exit management schema"""
    employee_id: str = Field(..., description="Reference to employee")
    employee_code: str = Field(..., description="Employee code")
    employee_name: str = Field(..., description="Employee name")
    department: str = Field(..., description="Employee department")
    designation: str = Field(..., description="Employee designation")
    exit_reason: str = Field(..., description="Reason for exit")
    resignation_date: date = Field(..., description="Date of resignation/initiation")
    last_working_day: date = Field(..., description="Last working day")
    
    # Notice period
    notice_period_days: int = Field(..., ge=0, description="Notice period in days")
    notice_period_waived: bool = Field(default=False, description="Notice period waived")
    notice_period_waiver_reason: Optional[str] = Field(None, description="Reason for waiver")
    
    # Exit interview
    exit_interviewer: Optional[str] = Field(None, description="Exit interviewer")
    exit_interview_notes: Optional[str] = Field(None, description="Exit interview notes")
    exit_interview_feedback: Optional[str] = Field(None, description="Exit interview feedback")
    
    # Handover process
    handover_responsible_person: Optional[str] = Field(None, description="Handover responsible person")
    
    # Asset and access management
    handover_plan_submitted: bool = Field(default=False, description="Handover plan submitted")
    handover_completed: bool = Field(default=False, description="Handover completed")
    company_assets_returned: bool = Field(default=False, description="All company assets returned")
    email_deactivated: bool = Field(default=False, description="Email account deactivated")
    system_access_revoked: bool = Field(default=False, description="System access revoked")
    access_cards_returned: bool = Field(default=False, description="Access cards returned")
    
    # Financial clearance
    final_settlement_calculated: bool = Field(default=False, description="Final settlement calculated")
    final_settlement_paid: bool = Field(default=False, description="Final settlement paid")
    
    # Documents
    exit_form_submitted: bool = Field(default=False, description="Exit form submitted")
    experience_letter_requested: bool = Field(default=False, description="Experience letter requested")
    experience_letter_issued: bool = Field(default=False, description="Experience letter issued")
    relieving_letter_issued: bool = Field(default=False, description="Relieving letter issued")
    
    # Compliance
    nda_signed: bool = Field(default=False, description="NDA signed")
    legal_clearance: bool = Field(default=False, description="Legal clearance completed")
    
    # Feedback
    hr_feedback: Optional[str] = Field(None, description="HR team feedback")
    manager_feedback: Optional[str] = Field(None, description="Manager feedback")
    team_feedback: Optional[str] = Field(None, description="Team feedback")
    
    # Notes
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    employee_notes: Optional[str] = Field(None, description="Employee notes")


class ExitManagementCreate(ExitManagementBase):
    """Schema for creating exit management"""
    assigned_to: Optional[str] = Field(None, description="HR personnel responsible for exit")
    tasks: Optional[List[ExitTaskCreate]] = Field(default_factory=list, description="Initial tasks")


class ExitManagementUpdate(BaseModel):
    """Schema for updating exit management"""
    actual_exit_date: Optional[date] = Field(None)
    status: Optional[str] = Field(None, description="Exit process status")
    
    # Notice period
    notice_period_served: Optional[int] = Field(None, ge=0)
    notice_period_waived: Optional[bool] = Field(None)
    notice_period_waiver_reason: Optional[str] = Field(None)
    
    # Exit interview
    exit_interview_scheduled: bool = Field(default=False)
    exit_interview_date: Optional[date] = Field(None)
    exit_interview_conducted: bool = Field(default=False)
    exit_interviewer: Optional[str] = Field(None)
    exit_interview_notes: Optional[str] = Field(None)
    exit_interview_feedback: Optional[str] = Field(None)
    
    # Handover process
    handover_responsible_person: Optional[str] = Field(None)
    handover_plan_submitted: Optional[bool] = Field(None)
    handover_plan_date: Optional[date] = Field(None)
    handover_completed: Optional[bool] = Field(None)
    handover_completion_date: Optional[date] = Field(None)
    
    # Asset and access management
    company_assets_returned: Optional[bool] = Field(None)
    email_deactivated: Optional[bool] = Field(None)
    system_access_revoked: Optional[bool] = Field(None)
    access_cards_returned: Optional[bool] = Field(None)
    
    # Financial clearance
    final_settlement_calculated: Optional[bool] = Field(None)
    final_settlement_amount: Optional[float] = Field(None, ge=0)
    final_settlement_date: Optional[date] = Field(None)
    final_settlement_paid: Optional[bool] = Field(None)
    
    # Deductions and adjustments
    notice_period_deduction: Optional[float] = Field(None, ge=0)
    other_deductions: Optional[List[Dict[str, Any]]] = Field(None)
    adjustments: Optional[List[Dict[str, Any]]] = Field(None)
    
    # Documents
    exit_form_submitted: Optional[bool] = Field(None)
    experience_letter_requested: Optional[bool] = Field(None)
    experience_letter_issued: Optional[bool] = Field(None)
    relieving_letter_issued: Optional[bool] = Field(None)
    
    # Compliance
    nda_signed: Optional[bool] = Field(None)
    legal_clearance: Optional[bool] = Field(None)
    
    # Feedback
    hr_feedback: Optional[str] = Field(None)
    manager_feedback: Optional[str] = Field(None)
    team_feedback: Optional[str] = Field(None)
    
    # Issues
    escalation_required: Optional[bool] = Field(None)
    
    # Notes
    admin_notes: Optional[str] = Field(None)
    employee_notes: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)


class ExitManagementResponse(BaseModel):
    """Schema for exit management response"""
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    department: str
    designation: str
    exit_reason: str
    resignation_date: date
    last_working_day: date
    actual_exit_date: Optional[date]
    status: str
    
    # Notice period
    notice_period_days: int
    notice_period_served: int
    notice_period_waived: bool
    notice_period_waiver_reason: Optional[str]
    
    # Exit interview
    exit_interview_scheduled: bool
    exit_interview_date: Optional[date]
    exit_interview_conducted: bool
    exit_interviewer: Optional[str]
    exit_interview_notes: Optional[str]
    exit_interview_feedback: Optional[str]
    
    # Handover process
    handover_responsible_person: Optional[str]
    handover_plan_submitted: bool
    handover_plan_date: Optional[date]
    handover_completed: bool
    handover_completion_date: Optional[date]
    
    # Tasks
    tasks: List[ExitTaskResponse]
    
    # Asset and access management
    company_assets_returned: bool
    asset_return_details: List[Dict[str, Any]]
    email_deactivated: bool
    system_access_revoked: bool
    access_cards_returned: bool
    
    # Financial clearance
    final_settlement_calculated: bool
    final_settlement_amount: Optional[float]
    final_settlement_date: Optional[date]
    final_settlement_paid: bool
    
    # Deductions and adjustments
    notice_period_deduction: Optional[float]
    other_deductions: List[Dict[str, Any]]
    adjustments: List[Dict[str, Any]]
    
    # Documents
    exit_form_submitted: bool
    experience_letter_requested: bool
    experience_letter_issued: bool
    relieving_letter_issued: bool
    
    # Compliance
    nda_signed: bool
    legal_clearance: bool
    
    # Feedback
    hr_feedback: Optional[str]
    manager_feedback: Optional[str]
    team_feedback: Optional[str]
    
    # Progress tracking
    completion_percentage: float
    tasks_completed: int
    total_tasks: int
    
    # Issues and blockers
    blockers: List[Dict[str, Any]]
    escalation_required: bool
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    assigned_to: Optional[str]
    
    # Notes
    admin_notes: Optional[str]
    employee_notes: Optional[str]
    
    class Config:
        from_attributes = True


class ExitManagementListResponse(BaseModel):
    """Schema for exit management list response"""
    exits: List[ExitManagementResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExitSearch(BaseModel):
    """Schema for exit search"""
    query: Optional[str] = Field(None, description="Search query")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")
    exit_reason: Optional[str] = Field(None, description="Filter by exit reason")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned person")
    resignation_date_from: Optional[date] = Field(None, description="Resignation date from")
    resignation_date_to: Optional[date] = Field(None, description="Resignation date to")
    last_working_day_from: Optional[date] = Field(None, description="Last working day from")
    last_working_day_to: Optional[date] = Field(None, description="Last working day to")
    overdue_only: bool = Field(default=False, description="Show only overdue exits")


class ExitTaskCreate(BaseModel):
    """Schema for creating a task in existing exit"""
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    assigned_to: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    priority: str = Field(default="medium")
    due_date: Optional[date] = Field(None)
    notes: Optional[str] = Field(None)


class ExitTaskUpdate(BaseModel):
    """Schema for updating exit task status"""
    status: str = Field(..., description="Task status")
    notes: Optional[str] = Field(None, description="Task notes")


class ExitBlocker(BaseModel):
    """Schema for adding a blocker"""
    blocker_description: str = Field(..., description="Blocker description")
    severity: str = Field(default="medium", description="Blocker severity")


class ExitInterview(BaseModel):
    """Schema for exit interview"""
    interview_date: date = Field(..., description="Interview date")
    interviewer: str = Field(..., description="Interviewer name/ID")
    interview_type: str = Field(default="face_to_face", description="Interview type")
    questions: List[Dict[str, Any]] = Field(default_factory=list, description="Interview questions and answers")
    feedback: Optional[str] = Field(None, description="Interview feedback")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Overall rating")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class ExitAsset(BaseModel):
    """Schema for asset return"""
    asset_name: str = Field(..., description="Asset name")
    asset_id: str = Field(..., description="Asset ID")
    asset_type: str = Field(..., description="Asset type")
    return_date: date = Field(..., description="Return date")
    condition: str = Field(..., description="Asset condition")
    received_by: str = Field(..., description="Person who received asset")
    notes: Optional[str] = Field(None, description="Additional notes")


class ExitSettlement(BaseModel):
    """Schema for final settlement"""
    settlement_amount: float = Field(..., gt=0, description="Settlement amount")
    settlement_date: date = Field(..., description="Settlement date")
    payment_method: str = Field(..., description="Payment method")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    breakdown: Dict[str, float] = Field(..., description="Settlement breakdown")
    notes: Optional[str] = Field(None, description="Settlement notes")


class ExitFeedback(BaseModel):
    """Schema for exit feedback"""
    overall_experience: int = Field(..., ge=1, le=5, description="Overall experience rating")
    management_support: int = Field(..., ge=1, le=5, description="Management support rating")
    work_environment: int = Field(..., ge=1, le=5, description="Work environment rating")
    compensation: int = Field(..., ge=1, le=5, description="Compensation rating")
    growth_opportunities: int = Field(..., ge=1, le=5, description="Growth opportunities rating")
    reasons_for_leaving: List[str] = Field(..., description="Reasons for leaving")
    suggestions_for_improvement: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    would_recommend: bool = Field(..., description="Would recommend company")
    would_rehire: Optional[bool] = Field(None, description="Would consider rehiring")
    additional_comments: Optional[str] = Field(None, description="Additional comments")


class ExitStatistics(BaseModel):
    """Schema for exit statistics"""
    total_exits: int
    active_exits: int
    completed_exits: int
    overdue_exits: int
    average_exit_process_days: float
    department_breakdown: List[Dict[str, Any]]
    exit_reason_breakdown: List[Dict[str, Any]]
    monthly_trend: List[Dict[str, Any]]
    completion_rate: float
    tasks_by_status: Dict[str, int]


class ExitDocument(BaseModel):
    """Schema for exit document"""
    document_type: str = Field(..., description="Document type")
    document_name: str = Field(..., description="Document name")
    file_url: str = Field(..., description="File URL")
    issued_date: Optional[date] = Field(None, description="Document issued date")
    notes: Optional[str] = Field(None, description="Document notes")


class ExitClearance(BaseModel):
    """Schema for department clearance"""
    department: str = Field(..., description="Department name")
    cleared_by: str = Field(..., description="Person who cleared")
    clearance_date: date = Field(..., description="Clearance date")
    status: str = Field(..., description="Clearance status")
    notes: Optional[str] = Field(None, description="Clearance notes")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Clearance attachments")
