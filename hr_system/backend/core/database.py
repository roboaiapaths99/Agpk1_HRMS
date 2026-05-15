from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import List
import logging

from .config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls):
        """Create database connection"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Test the connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("Database connection closed")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes"""
        try:
            database = cls.client[settings.DATABASE_NAME]
            # Create indexes for collections (handle existing indexes)
            try:
                await database.employees.create_index("employee_code", unique=True)
            except:
                pass  # Index already exists
            try:
                await database.employees.create_index("email", unique=True)
            except:
                pass  # Index already exists
            try:
                await database.users.create_index("email", unique=True)
            except:
                pass  # Index already exists
            try:
                await database.users.create_index("username", unique=True)
            except:
                pass  # Index already exists
            try:
                await database.payrolls.create_index([("employee_id", 1), ("payroll_month", 1)], unique=True)
            except:
                pass  # Index already exists
            logger.info("Database indexes created/verified")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    @classmethod
    async def get_database(cls):
        """Get database instance"""
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    async def init_beanie(cls, database, document_models: List):
        """Initialize Beanie with document models"""
        try:
            await init_beanie(
                database=database,
                document_models=document_models
            )
            logger.info("Beanie initialized with document models")
        except Exception as e:
            if "IndexKeySpecsConflict" in str(e):
                logger.warning("Index conflicts detected, initializing without index creation")
                # Try to initialize without creating indexes
                await init_beanie(
                    database=database,
                    document_models=document_models
                )
                logger.info("Beanie initialized with document models (existing indexes used)")
            else:
                raise
    
    @classmethod
    async def get_database_stats(cls):
        """Get database statistics"""
        try:
            database = cls.client[settings.DATABASE_NAME]
            stats = await database.command("dbstats")
            return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return None
