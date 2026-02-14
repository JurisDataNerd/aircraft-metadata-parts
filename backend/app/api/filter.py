from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..services.effectivity import check_effectivity

router = APIRouter()

def serialize_part(part):
    """Convert part to JSON-serializable dict"""
    return {
        "part_number": part.get("part_number", ""),
        "nomenclature": part.get("nomenclature"),
        "page_number": part.get("page_number"),
        "figure": part.get("figure"),
        "change_type": part.get("change_type"),
        "sb_reference": part.get("sb_reference"),
        "is_applicable": part.get("is_applicable", False)
    }

@router.get("/line")
async def filter_by_line(
    line: int = Query(..., description="Line number", ge=1),
    revision: Optional[str] = Query(None, description="Specific revision"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    FR-03: Line-based filtering
    Returns parts that are applicable/non-applicable for given line
    """
    # Query parts (bisa filter by revision jika ada)
    query = {}
    if revision:
        query["revision"] = revision
    
    cursor = db.ipd_parts.find(query)
    all_parts = await cursor.to_list(1000)
    
    applicable = []
    non_applicable = []
    
    for part in all_parts:
        is_applicable = check_effectivity(
            part.get("effectivity_type", "LIST"),
            part.get("effectivity_values", []),
            part.get("effectivity_range", {}),
            line
        )
        
        part_dict = serialize_part(part)
        part_dict["is_applicable"] = is_applicable
        
        if is_applicable:
            applicable.append(part_dict)
        else:
            non_applicable.append(part_dict)
    
    # Ambil revision terbaru jika tidak dispesifikasi
    current_rev = revision
    if not current_rev and all_parts:
        revs = set(p.get("revision") for p in all_parts if p.get("revision"))
        current_rev = max(revs) if revs else "unknown"
    
    return {
        "line_number": line,
        "revision": current_rev or "unknown",
        "applicable_parts": applicable,
        "non_applicable_parts": non_applicable,
        "total_count": len(applicable) + len(non_applicable),
        "applicable_count": len(applicable),
        "non_applicable_count": len(non_applicable)
    }