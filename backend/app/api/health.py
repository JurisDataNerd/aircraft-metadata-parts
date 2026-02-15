from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Cek status API dan koneksi database"""
    try:
        # Cek koneksi dengan ping
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "phase": "1",
        "database": db_status,
        "service": "aircraft-config-intelligence"
    }