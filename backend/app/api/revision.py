from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime
from bson import ObjectId

from ..core.database import get_db
from ..core.persistent_authority import persistent_authority

router = APIRouter()

def serialize_revision(rev):
    """Convert revision to JSON-serializable dict"""
    if rev is None:
        return None
    
    rev_dict = dict(rev)
    if "_id" in rev_dict:
        rev_dict["id"] = str(rev_dict["_id"])
        del rev_dict["_id"]
    
    # Convert ObjectId fields
    for key, value in rev_dict.items():
        if isinstance(value, ObjectId):
            rev_dict[key] = str(value)
        elif isinstance(value, datetime):
            rev_dict[key] = value.isoformat()
    
    return rev_dict

@router.get("/{document_id}/graph")
async def get_revision_graph(
    document_id: str,
    force_rebuild: bool = Query(False, description="Force rebuild from DB"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Dapatkan revision graph untuk dokumen"""
    try:
        graph = await persistent_authority.get_revision_graph(document_id, force_rebuild)
        
        # Konversi ke format response
        revisions = []
        for rev in graph.values():
            revisions.append({
                "revision": rev.revision,
                "status": rev.metadata.status.value if hasattr(rev.metadata.status, 'value') else rev.metadata.status,
                "created_at": rev.created_at.isoformat(),
                "created_by": rev.metadata.created_by,
                "approved_at": rev.metadata.approved_at.isoformat() if rev.metadata.approved_at else None,
                "approved_by": rev.metadata.approved_by,
                "part_count": rev.part_count,
                "has_previous": rev.previous_revision_id is not None,
                "has_next": rev.next_revision_id is not None
            })
        
        # Sort by revision
        revisions.sort(key=lambda x: x["revision"])
        
        return {
            "document_id": document_id,
            "total_revisions": len(revisions),
            "revisions": revisions,
            "cached": not force_rebuild
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))