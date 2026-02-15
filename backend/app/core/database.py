from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Koneksi ke MongoDB Atlas"""
    try:
        mongodb.client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=50,
            minPoolSize=10,
            retryWrites=True
        )
        mongodb.db = mongodb.client[settings.MONGO_DB]
        
        # Test koneksi
        await mongodb.db.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB}")
        
        # Buat indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Tutup koneksi MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("✅ Disconnected from MongoDB")

def get_db():
    """Dependency injection untuk database"""
    return mongodb.db

async def create_indexes():
    """Buat indexes untuk performance"""
    db = mongodb.db
    
    # Document indexes
    await db.document.create_index("document_id", unique=True)
    await db.document.create_index([("document_number", 1), ("revision", 1)])
    
    # IPD Parts indexes
    await db.ipd_parts.create_index("part_number")
    await db.ipd_parts.create_index("document_id")
    await db.ipd_parts.create_index("effectivity_values")
    
    # Drawing items indexes
    await db.drawing_items.create_index("part_number")
    await db.drawing_items.create_index("document_id")
    
    # Part master indexes
    await db.part_master.create_index("part_number", unique=True)
    
    # Revision indexes
    await db.revisions.create_index([("document_id", 1), ("revision", 1)], unique=True)
    await db.revisions.create_index("previous_revision")
    
    # Audit indexes
    await db.audit.create_index([("document_id", 1), ("timestamp", -1)])
    
    logger.info("✅ Database indexes created")