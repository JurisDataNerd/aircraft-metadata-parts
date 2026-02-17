# backend/app/api/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
import os
import uuid
import hashlib
import shutil
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database
from app.services.parser import IPDParser
from app.models.document import DocumentModel

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/")
async def list_documents(
    limit: int = 50,
    skip: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all uploaded documents"""
    cursor = db.documents.find().sort("uploaded_at", -1).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Convert ObjectId
    for doc in documents:
        doc["_id"] = str(doc["_id"])
        
    return {
        "total": await db.documents.count_documents({}),
        "items": documents,
        "limit": limit,
        "skip": skip
    }

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = "IPD",
    aircraft_model: str = "787-8",
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Upload IPD PDF document for parsing
    Phase 1: Simple upload and store
    """
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are supported")
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Save file
    pdf_filename = f"{document_id}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    content = await file.read()
    with open(pdf_path, "wb") as f:
        f.write(content)
    
    # Calculate file hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Create document record
    document = {
        "document_id": document_id,
        "document_type": doc_type,
        "document_number": file.filename.replace('.pdf', ''),
        "revision": "unknown",
        "aircraft_model": aircraft_model,
        "source_pdf_path": pdf_path,
        "file_hash": file_hash,
        "uploaded_at": datetime.utcnow(),
        "parsing_status": "pending",
        "parts_count": 0
    }
    
    await db.documents.insert_one(document)
    
    # Trigger parsing in background
    background_tasks.add_task(
        parse_document_background,
        document_id=document_id,
        pdf_path=pdf_path,
        db=db
    )
    
    return {
        "document_id": document_id,
        "status": "queued",
        "filename": file.filename,
        "size_bytes": len(content)
    }

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get document by ID"""
    document = await db.documents.find_one({"document_id": document_id})
    
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Convert ObjectId to string
    document["_id"] = str(document["_id"])
    
    return document

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get parsing status"""
    document = await db.documents.find_one({"document_id": document_id})
    
    if not document:
        raise HTTPException(404, "Document not found")
    
    return {
        "document_id": document_id,
        "status": document.get("parsing_status"),
        "parts_count": document.get("parts_count", 0),
        "uploaded_at": document.get("uploaded_at")
    }

@router.get("/{document_id}/parts")
async def get_document_parts(
    document_id: str,
    limit: int = 100,
    skip: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all parts from a document"""
    cursor = db.ipd_parts.find(
        {"document_id": document_id}
    ).skip(skip).limit(limit)
    
    parts = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for part in parts:
        part["_id"] = str(part["_id"])
    
    return {
        "total": await db.ipd_parts.count_documents({"document_id": document_id}),
        "items": parts,
        "limit": limit,
        "skip": skip
    }

async def parse_document_background(document_id: str, pdf_path: str, db):
    """Background task for parsing"""
    try:
        # Update status
        await db.documents.update_one(
            {"document_id": document_id},
            {"$set": {"parsing_status": "processing"}}
        )
        
        # Parse document
        parser = IPDParser()
        result = await parser.parse(pdf_path)
        
        # Save parts to database
        saved_count = 0
        for part in result.get('parts', []):
            part_id = f"{part['part_number']}_{document_id}_{part['page']}"
            
            ipd_part = {
                "ipd_part_id": part_id,
                "document_id": document_id,  # Ini string, bukan ObjectId
                "part_number": part["part_number"],
                "nomenclature": part.get("nomenclature"),
                "figure": part.get("figure"),
                "item": part.get("item"),
                "is_sticker": False,  # Default
                "effectivity_type": part["effectivity"]["type"],
                "effectivity_values": part["effectivity"].get("values"),
                "effectivity_range": part["effectivity"] if part["effectivity"].get("type") == "RANGE" else None,
                "upa": part.get("upa"),  # Bisa None
                "page_number": part["page"],
                "confidence": part.get("confidence", 0.95),
                "created_at": datetime.utcnow()
            }

            await db.ipd_parts.update_one(
                {"ipd_part_id": part_id},
                {"$set": ipd_part},
                upsert=True
            )
            saved_count += 1
        
        # Update document status
        await db.documents.update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "parsing_status": "completed",
                    "parts_count": saved_count,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Clean up file? Optional - could keep for reference
        # os.remove(pdf_path)
        
    except Exception as e:
        # Update error status
        await db.documents.update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "parsing_status": "failed",
                    "error_message": str(e)
                }
            }
        )
        print(f"Error parsing document {document_id}: {e}")