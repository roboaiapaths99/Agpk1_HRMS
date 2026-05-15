from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from core.config import settings
from core.database import Database
from core.security import SecurityManager
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Import all models for Beanie initialization
from models.user_model import User
from models.employee_model import Employee
from models.onboarding_model import Onboarding
from models.payroll_model import Payroll
from models.exit_management_model import ExitManagement

# Import simple auth instead of complex auth
from routes.auth import router as auth_router
from routes.employees import router as employee_router
from routes.onboarding import router as onboarding_router
from routes.payroll import router as payroll_router
from routes.exit_management import router as exit_management_router
from routes.users import router as user_router
from routes.employee_portal import router as employee_portal_router
# from test_endpoint import router as test_router

# Import simple routers
# from simple_employees import router as simple_employees_router
# from simple_payroll import router as simple_payroll_router
# from simple_attendance import router as simple_attendance_router
# from simple_onboarding import router as simple_onboarding_router
# from test_analytics import router as test_analytics_router
from api.employee_api import router as employee_api_router
from api.attendance_api import router as attendance_api_router
from api.payroll_api import router as payroll_api_router
from api.analytics_api import router as analytics_api_router
from api.alerts_api import router as alerts_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting HR Management System...")
    
    try:
        # Connect to database
        await Database.connect()
        
        # Get database instance
        database = await Database.get_database()
        
        # Initialize Beanie with all models
        await Database.init_beanie(
            database,
            document_models=[
                User,
                Employee,
                Onboarding,
                Payroll,
                ExitManagement
            ]
        )
        
        # await Database.create_indexes()  # Disabled due to existing index conflicts
        logger.info("Database connection established")
        
        # Initialize default admin user if needed - TEMPORARILY DISABLED
        # await initialize_default_admin()
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down HR Management System...")
    await Database.disconnect()
    logger.info("Application shutdown completed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready HR Management SaaS Platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware - MUST be right after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Exception handlers - FIXED to use JSONResponse and placed AFTER app creation
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status_code": exc.status_code,
                "detail": exc.detail,
                "timestamp": str(datetime.utcnow())
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "status_code": 500,
                "detail": str(exc),  # show real error for debugging
                "timestamp": str(datetime.utcnow())
            }
        }
    )


# Include all module routers (excluding old analytics)
# app.include_router(test_router, prefix="/api/v1")
# Include auth router
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(employee_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(payroll_router, prefix="/api/v1")
app.include_router(exit_management_router, prefix="/api/v1")

# Include new API routers
app.include_router(employee_api_router, prefix="/api/v1")
app.include_router(attendance_api_router, prefix="/api/v1")
app.include_router(payroll_api_router, prefix="/api/v1")
app.include_router(analytics_api_router, prefix="/api/v1")
app.include_router(alerts_api_router, prefix="/api/v1")
# app.include_router(test_analytics_router, prefix="/api/v1")
# app.include_router(simple_employees_router, prefix="/api/v1")
# app.include_router(simple_payroll_router, prefix="/api/v1")
# app.include_router(simple_attendance_router, prefix="/api/v1")
# app.include_router(simple_onboarding_router, prefix="/api/v1")
app.include_router(employee_portal_router, prefix="/api/v1/employee", tags=["Employee Portal"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Management System API",
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_stats = await Database.get_database_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected" if db_stats else "disconnected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/v1/info")
async def get_system_info():
    """Get system information"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "features": {
            "employee_management": True,
            "onboarding": True,
            "payroll": True,
            "exit_management": True,
            "analytics": True,
            "document_management": True
        }
    }


async def initialize_default_admin():
    """Initialize default admin user if not exists"""
    try:
        from models.user_model import User, UserRole
        from core.security import SecurityManager
        
        admin_email = "admin@hrsystem.com"
        existing_admin = await User.find_one(User.email == admin_email)
        
        if not existing_admin:
            # Create default admin
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="System Administrator",
                hashed_password=SecurityManager.get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                created_by="system"
            )
            
            await admin_user.insert()
            logger.info("Default admin user created")
            
    except Exception as e:
        logger.error(f"Failed to initialize default admin: {e}")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow()
        }
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": {
            "status_code": 500,
            "detail": "Internal server error",
            "timestamp": datetime.utcnow()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
