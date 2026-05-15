from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import re
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> dict:
    """
    Get current authenticated user from JWT token
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {
            "id": user_id,
            "email": email,
            "role": role,
            "is_authenticated": True
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common formatting characters
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return cleaned_phone.isdigit() and len(cleaned_phone) >= 10


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0
    }
    
    # Check length
    if len(password) < 8:
        result["errors"].append("Password must be at least 8 characters long")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    # Check uppercase
    if not re.search(r'[A-Z]', password):
        result["errors"].append("Password must contain at least one uppercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    # Check lowercase
    if not re.search(r'[a-z]', password):
        result["errors"].append("Password must contain at least one lowercase letter")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    # Check numbers
    if not re.search(r'\d', password):
        result["errors"].append("Password must contain at least one number")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    # Check special characters
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["errors"].append("Password must contain at least one special character")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    result["strength"] = "Weak" if result["score"] < 3 else "Medium" if result["score"] < 5 else "Strong"
    
    return result


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format currency amount"""
    return f"{currency}{amount:,.2f}"


def format_phone_number(phone: str) -> str:
    """Format phone number"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) > 10:
        return f"+{digits[:-10]} ({digits[-10:-7]}) {digits[-7:-4]}-{digits[-4:]}"
    else:
        return phone


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def calculate_experience(joining_date: date, exit_date: Optional[date] = None) -> float:
    """Calculate total experience in years"""
    end_date = exit_date or date.today()
    delta = end_date - joining_date
    return round(delta.days / 365.25, 2)


def get_notice_period_end_date(resignation_date: date, notice_days: int) -> date:
    """Calculate notice period end date excluding weekends"""
    current = resignation_date
    days_counted = 0
    
    while days_counted < notice_days:
        current += timedelta(days=1)
        # Skip weekends (Saturday and Sunday)
        if current.weekday() < 5:  # Monday to Friday
            days_counted += 1
    
    return current


def validate_file_size(file_size_bytes: int, max_size_mb: int = 5) -> bool:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.lower().split('.')[-1] if '.' in filename else ""


def is_allowed_file_type(filename: str, allowed_types: list) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in [t.lower() for t in allowed_types]


def create_pagination_params(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Create pagination parameters"""
    return {
        "skip": (page - 1) * page_size,
        "limit": page_size,
        "page": page,
        "page_size": page_size
    }


def create_response(
    data: Any = None,
    message: str = "Success",
    status: str = "success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        "status": status,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.utcnow()
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return response


def format_address(address_dict: Dict[str, Any]) -> str:
    """Format address dictionary into string"""
    parts = []
    
    if address_dict.get("line1"):
        parts.append(address_dict["line1"])
    if address_dict.get("line2"):
        parts.append(address_dict["line2"])
    if address_dict.get("city"):
        parts.append(address_dict["city"])
    if address_dict.get("state"):
        parts.append(address_dict["state"])
    if address_dict.get("pincode"):
        parts.append(address_dict["pincode"])
    if address_dict.get("country"):
        parts.append(address_dict["country"])
    
    return ", ".join(parts)


def generate_payroll_month_year(month: int, year: int) -> str:
    """Generate payroll month string in YYYY-MM format"""
    return f"{year:04d}-{month:02d}"


def parse_payroll_month(payroll_month: str) -> tuple[int, int]:
    """Parse payroll month string and return year, month tuple"""
    try:
        parts = payroll_month.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid format")
        year = int(parts[0])
        month = int(parts[1])
        if month < 1 or month > 12:
            raise ValueError("Invalid month")
        return year, month
    except (ValueError, IndexError):
        raise ValueError("Invalid payroll month format. Use YYYY-MM")


def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def generate_employee_code(department: str, sequence: int) -> str:
    """Generate employee code"""
    dept_code = department.upper()[:3]
    return f"{dept_code}{sequence:04d}"


def calculate_ctc_components(ctc: float) -> Dict[str, float]:
    """Calculate salary components from CTC"""
    # Basic salary is typically 40-50% of CTC
    basic_salary = ctc * 0.45 / 12  # Monthly
    hra = basic_salary * 0.4  # 40% of basic
    other_allowances = (ctc / 12) - basic_salary - hra
    
    return {
        "ctc": ctc,
        "basic_salary": basic_salary,
        "hra": hra,
        "other_allowances": other_allowances,
        "gross_salary": basic_salary + hra + other_allowances
    }


def validate_pan_number(pan: str) -> bool:
    """Validate PAN number format"""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return re.match(pattern, pan.upper()) is not None


def validate_aadhaar_number(aadhaar: str) -> bool:
    """Validate Aadhaar number format"""
    # Remove spaces and hyphens
    cleaned = re.sub(r'[\s-]', '', aadhaar)
    return len(cleaned) == 12 and cleaned.isdigit()


def generate_unique_id(prefix: str = "HR") -> str:
    """Generate unique ID with timestamp"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{prefix}{timestamp}"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like phone numbers or account numbers"""
    if len(data) <= visible_chars:
        return data
    
    visible = data[:visible_chars]
    masked = mask_char * (len(data) - visible_chars)
    return visible + masked


def calculate_taxable_income(salary: float, deductions: float = 0) -> float:
    """Calculate taxable income (simplified calculation)"""
    return max(0, salary - deductions)


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage"""
    return f"{value:.{decimal_places}f}%"


def is_weekend(date_obj: date) -> bool:
    """Check if date is weekend"""
    return date_obj.weekday() >= 5


def add_business_days(start_date: date, days: int) -> date:
    """Add business days to a date"""
    current = start_date
    business_days_added = 0
    
    while business_days_added < days:
        current += timedelta(days=1)
        if not is_weekend(current):
            business_days_added += 1
    
    return current
