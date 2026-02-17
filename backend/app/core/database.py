# backend/app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls, mongodb_url: str):
        """Connect to MongoDB Atlas"""
        try:
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                maxPoolSize=50,
                minPoolSize=10,
                retryWrites=True,
                serverSelectionTimeoutMS=5000
            )
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_db(cls, db_name: str):
        """Get database instance"""
        if cls.client is None:
            raise Exception("Database not initialized")
        return cls.client[db_name]

# Dependency for FastAPI
async def get_database():
    db_name = settings.MONGODB_DB_NAME
    return Database.get_db(db_name)