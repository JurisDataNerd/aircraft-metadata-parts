from fastapi import APIRouter, HTTPException, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List, Annotated
from datetime import datetime

from ..core.database import get_db

router = APIRouter()

def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    
    # Convert _id to string
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    
    # Convert any ObjectId fields to string
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, list):
            # Handle lists that might contain ObjectId
            doc[key] = [
                str(item) if isinstance(item, ObjectId) else item
                for item in value
            ]
    
    return doc

@router.get("/")
async def list_documents(
    doc_type: Optional[str] = Query(None, description="Filter by type: IPD or DRAWING"),
    aircraft_model: Optional[str] = Query(None, description="Filter by aircraft model"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all documents with optional filters"""
    query = {}
    if doc_type:
        if doc_type not in ["IPD", "DRAWING"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="doc_type must be 'IPD' or 'DRAWING'"
            )
        query["document_type"] = doc_type
    
    if aircraft_model:
        query["aircraft_model"] = aircraft_model
    
    cursor = db.document.find(query).sort("uploaded_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    # Serialize each document
    serialized_docs = [serialize_document(doc) for doc in docs]
    
    return {
        "total": len(serialized_docs),
        "documents": serialized_docs
    }

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get document by document_id"""
    doc = await db.document.find_one({"document_id": document_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}"
        )
    
    return serialize_document(doc)

@router.get("/{document_id}/parts")
async def get_document_parts(
    document_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
):
    """Get all parts (IPD or Drawing) for a specific document"""
    # Cari document
    doc = await db.document.find_one({"document_id": document_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}"
        )
    
    # Ambil parts berdasarkan tipe dokumen
    if doc["document_type"] == "IPD":
        cursor = db.ipd_parts.find({"document_id": doc["_id"]})
        parts = await cursor.to_list(1000)
        # Serialize
        for part in parts:
            part["id"] = str(part["_id"])
            del part["_id"]
            if "document_id" in part and isinstance(part["document_id"], ObjectId):
                part["document_id"] = str(part["document_id"])
    else:  # DRAWING
        cursor = db.drawing_items.find({"document_id": doc["_id"]})
        parts = await cursor.to_list(1000)
        # Serialize
        for part in parts:
            part["id"] = str(part["_id"])
            del part["_id"]
            if "document_id" in part and isinstance(part["document_id"], ObjectId):
                part["document_id"] = str(part["document_id"])
    
    return {
        "document_id": document_id,
        "document_type": doc["document_type"],
        "total_parts": len(parts),
        "parts": parts
    }

@router.get("/stats/summary")
async def get_document_stats(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get summary statistics of all documents"""
    total_docs = await db.document.count_documents({})
    ipd_count = await db.document.count_documents({"document_type": "IPD"})
    drawing_count = await db.document.count_documents({"document_type": "DRAWING"})
    
    # Ambil unique aircraft models
    pipeline = [
        {"$group": {"_id": "$aircraft_model"}},
        {"$match": {"_id": {"$ne": None}}}
    ]
    cursor = db.document.aggregate(pipeline)
    models = await cursor.to_list(100)
    
    return {
        "total_documents": total_docs,
        "ipd_documents": ipd_count,
        "drawing_documents": drawing_count,
        "aircraft_models": [m["_id"] for m in models if m["_id"]],
        "timestamp": datetime.utcnow().isoformat()
    }