# backend/app/api/filter.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import time
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.services.filter_service import FilterService

router = APIRouter(prefix="/filter", tags=["filter"])
filter_service = FilterService()

@router.get("/line/{line_number}")
async def filter_by_line(
    line_number: int,
    document_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Filter parts by line number based on effectivity
    This is the core feature for Phase 1
    """
    start_time = time.time()
    
    # Build query for applicable parts
    query = {
        "$or": [
            # LIST effectivity
            {
                "effectivity_type": "LIST",
                "effectivity_values": line_number
            },
            # RANGE effectivity
            {
                "effectivity_type": "RANGE",
                "effectivity_range.from": {"$lte": line_number},
                "effectivity_range.to": {"$gte": line_number}
            }
        ]
    }
    
    if document_id:
        query["document_id"] = document_id
    
    # Get all matching parts
    cursor = db.ipd_parts.find(query)
    parts = await cursor.to_list(length=1000)
    
    # Format response
    result = {
        "line_number": line_number,
        "applicable_parts": [
            {
                "part_number": p["part_number"],
                "nomenclature": p.get("nomenclature"),
                "figure": p.get("figure"),
                "item": p.get("item"),
                "effectivity": {
                    "type": p["effectivity_type"],
                    "values": p.get("effectivity_values"),
                    "range": p.get("effectivity_range")
                },
                "page": p.get("page_number"),
                "confidence": p.get("confidence", 0.95)
            }
            for p in parts
        ],
        "total_applicable": len(parts),
        "query_time_ms": int((time.time() - start_time) * 1000)
    }
    
    return result

@router.get("/line/{line_number}/check")
async def check_line_applicability(
    line_number: int,
    part_number: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Check if a specific part is applicable for a line number
    """
    # Find the part
    part = await db.ipd_parts.find_one({"part_number": part_number})
    
    if not part:
        raise HTTPException(404, f"Part {part_number} not found")
    
    # Check applicability
    is_applicable = False
    
    if part["effectivity_type"] == "LIST":
        is_applicable = line_number in part.get("effectivity_values", [])
    elif part["effectivity_type"] == "RANGE":
        range_data = part.get("effectivity_range", {})
        if range_data and range_data.get("from") and range_data.get("to"):
            is_applicable = range_data["from"] <= line_number <= range_data["to"]
    
    return {
        "part_number": part_number,
        "line_number": line_number,
        "is_applicable": is_applicable,
        "effectivity": {
            "type": part["effectivity_type"],
            "values": part.get("effectivity_values"),
            "range": part.get("effectivity_range")
        }
    }

@router.get("/statistics")
async def get_filter_statistics(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get statistics about filtered parts
    """
    # Total parts
    total_parts = await db.ipd_parts.count_documents({})
    
    # Parts by effectivity type
    list_count = await db.ipd_parts.count_documents({"effectivity_type": "LIST"})
    range_count = await db.ipd_parts.count_documents({"effectivity_type": "RANGE"})
    
    # Unique part numbers
    distinct_parts = await db.ipd_parts.distinct("part_number")
    
    # Documents count
    docs_count = await db.documents.count_documents({})
    
    return {
        "total_parts": total_parts,
        "parts_by_type": {
            "LIST": list_count,
            "RANGE": range_count
        },
        "unique_part_numbers": len(distinct_parts),
        "documents": docs_count,
        "recent_uploads": await db.documents.count_documents({
            "uploaded_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
        })
    }