import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(f"logs/hr_system_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("beanie").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for sensitive operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
        
        # Create audit log file
        handler = logging.FileHandler(f"logs/audit_{datetime.now().strftime('%Y%m%d')}.log")
        formatter = logging.Formatter(
            "%(asctime)s - AUDIT - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: str = ""):
        """Log user action"""
        message = f"User {user_id} performed {action} on {resource}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_data_access(self, user_id: str, resource: str, record_id: str):
        """Log data access"""
        message = f"User {user_id} accessed {resource} record {record_id}"
        self.logger.info(message)
    
    def log_data_modification(self, user_id: str, resource: str, record_id: str, changes: str):
        """Log data modification"""
        message = f"User {user_id} modified {resource} record {record_id} - {changes}"
        self.logger.info(message)
    
    def log_payroll_action(self, user_id: str, action: str, resource: str, details: str = ""):
        """Log payroll action"""
        message = f"User {user_id} performed {action} on payroll {resource}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_authentication(self, user_id: str, action: str, ip_address: str = "", success: bool = True):
        """Log authentication events"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Authentication {status} for user {user_id} - {action}"
        if ip_address:
            message += f" from IP {ip_address}"
        self.logger.info(message)
    
    def log_security_event(self, event_type: str, details: str, severity: str = "MEDIUM"):
        """Log security events"""
        message = f"SECURITY [{severity}] {event_type}: {details}"
        self.logger.warning(message)
    
    def log_payroll_action(self, user_id: str, action: str, payroll_id: str, details: str = ""):
        """Log payroll actions"""
        message = f"Payroll {action} by user {user_id} for payroll {payroll_id}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_employee_action(self, user_id: str, action: str, employee_id: str, details: str = ""):
        """Log employee actions"""
        message = f"Employee {action} by user {user_id} for employee {employee_id}"
        if details:
            message += f" - {details}"
        self.logger.info(message)


# Global audit logger instance
audit_logger = AuditLogger()
