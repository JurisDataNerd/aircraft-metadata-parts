from fastapi import APIRouter, HTTPException, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..schemas.ipd import IPDPartCreate, IPDPartResponse

router = APIRouter()

def serialize_part(part):
    """Convert MongoDB document to JSON-serializable dict"""
    if part is None:
        return None
    
    part["id"] = str(part["_id"])
    del part["_id"]
    
    if "document_id" in part and isinstance(part["document_id"], ObjectId):
        part["document_id"] = str(part["document_id"])
    
    if "created_at" in part and isinstance(part["created_at"], datetime):
        part["created_at"] = part["created_at"].isoformat()
    
    return part

@router.get("/part/{part_number}")
async def get_ipd_parts(
    part_number: str,
    revision: Optional[str] = Query(None, description="Filter by revision"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get IPD parts by part number"""
    try:
        query = {"part_number": part_number}
        if revision:
            query["revision"] = revision
        
        cursor = db.ipd_parts.find(query).sort("revision", -1)
        parts = await cursor.to_list(100)
        
        if not parts:
            return {
                "success": True,
                "data": [],
                "message": f"No parts found with number: {part_number}"
            }
        
        # Serialize each document
        result = [serialize_part(part) for part in parts]
        
        return {
            "success": True,
            "data": result,
            "count": len(result),
            "available_revisions": list(set(p.get("revision") for p in result if p.get("revision")))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parts: {str(e)}")