from motor.motor_asyncio import AsyncIOMotorClient
from config import settings  # Absolute import, bukan relative

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Koneksi ke MongoDB Atlas"""
    mongodb.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=50,
        minPoolSize=10
    )
    mongodb.db = mongodb.client[settings.MONGO_DB]
    print(f"✅ Connected to MongoDB: {settings.MONGO_DB}")

async def close_mongo_connection():
    """Tutup koneksi MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Disconnected from MongoDB")

def get_db():
    """Dependency injection untuk database"""
    return mongodb.db