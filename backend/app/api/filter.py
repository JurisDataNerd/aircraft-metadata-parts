from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime

from ..core.database import get_db
from ..services.effectivity import check_effectivity

router = APIRouter()

def serialize_part(part, line_number=None):
    """Convert part to JSON-serializable dict"""
    # Hitung applicability jika line_number diberikan
    is_applicable = False
    if line_number:
        is_applicable = check_effectivity(
            part.get("effectivity_type", "LIST"),
            part.get("effectivity_values", []),
            part.get("effectivity_range", {}),
            line_number
        )
    
    return {
        "part_number": part.get("part_number", ""),
        "nomenclature": part.get("nomenclature"),
        "page_number": part.get("page_number"),
        "figure": part.get("figure"),
        "change_type": part.get("change_type"),
        "sb_reference": part.get("sb_reference"),
        "upa": part.get("upa"),
        "supplier_code": part.get("supplier_code"),
        "is_applicable": is_applicable,
        "revision": part.get("revision")
    }

@router.get("/line")
async def filter_by_line(
    line: int = Query(..., description="Line number", ge=1),
    revision: Optional[str] = Query(None, description="Specific revision"),
    include_non_applicable: bool = Query(True, description="Include parts that don't apply"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    FR-03: Line-based filtering
    Returns parts that are applicable/non-applicable for given line
    """
    try:
        # Query parts
        query = {}
        if revision:
            query["revision"] = revision
        
        cursor = db.ipd_parts.find(query)
        all_parts = await cursor.to_list(2000)
        
        applicable = []
        non_applicable = []
        
        for part in all_parts:
            part_dict = serialize_part(part, line)
            
            if part_dict["is_applicable"]:
                applicable.append(part_dict)
            elif include_non_applicable:
                non_applicable.append(part_dict)
        
        # Get unique revisions
        revisions = sorted(set(p.get("revision") for p in all_parts if p.get("revision")), reverse=True)
        
        return {
            "success": True,
            "data": {
                "line_number": line,
                "revision_used": revision or "latest",
                "available_revisions": revisions[:10],
                "applicable_parts": applicable,
                "non_applicable_parts": non_applicable if include_non_applicable else [],
                "counts": {
                    "total": len(applicable) + len(non_applicable),
                    "applicable": len(applicable),
                    "non_applicable": len(non_applicable) if include_non_applicable else 0
                }
            },
            "metadata": {
                "query_time": datetime.utcnow().isoformat(),
                "api_version": "1.0"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter error: {str(e)}")