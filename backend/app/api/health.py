from fastapi import APIRouter
from app.core.database import get_db  # Absolute

router = APIRouter()

@router.get("/health")
async def health_check():
    """Cek status API dan koneksi database"""
    try:
        db = get_db()
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