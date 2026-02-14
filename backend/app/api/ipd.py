from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..core.database import get_db
from ..schemas.ipd import IPDPartCreate, IPDPartResponse

router = APIRouter()

def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    doc["id"] = str(doc["_id"])
    if "document_id" in doc and isinstance(doc["document_id"], ObjectId):
        doc["document_id"] = str(doc["document_id"])
    return doc

@router.post("/part", response_model=IPDPartResponse)
async def create_ipd_part(
    part: IPDPartCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """FR-01: Input IPD Part"""
    
    # Cek apakah document exists
    document = await db.document.find_one({"document_id": part.document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Buat part dict
    part_dict = part.model_dump()
    part_dict["document_id"] = document["_id"]
    part_dict["created_at"] = datetime.utcnow()
    
    # Insert ke database
    result = await db.ipd_parts.insert_one(part_dict)
    
    # Ambil data yang baru dibuat
    created_part = await db.ipd_parts.find_one({"_id": result.inserted_id})
    created_part = serialize_document(created_part)
    
    return created_part

@router.get("/part/{part_number}")
async def get_ipd_parts(
    part_number: str,
    revision: Optional[str] = Query(None, description="Filter by revision"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get IPD parts by part number (optionally by revision)"""
    query = {"part_number": part_number}
    if revision:
        query["revision"] = revision
    
    cursor = db.ipd_parts.find(query).sort("revision", -1)
    parts = await cursor.to_list(100)
    
    # Serialize each document
    result = []
    for part in parts:
        part = serialize_document(part)
        # Hapus field yang tidak perlu
        if "_id" in part:
            del part["_id"]
        result.append(part)
    
    return {"parts": result}

@router.get("/document/{document_id}")
async def get_parts_by_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all IPD parts for a specific document"""
    # Cari document dulu
    doc = await db.document.find_one({"document_id": document_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    cursor = db.ipd_parts.find({"document_id": doc["_id"]})
    parts = await cursor.to_list(1000)
    
    # Serialize
    result = []
    for part in parts:
        part = serialize_document(part)
        if "_id" in part:
            del part["_id"]
        result.append(part)
    
    return {
        "document_id": document_id,
        "revision": doc.get("revision"),
        "total_parts": len(result),
        "parts": result
    }