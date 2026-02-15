from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status
from datetime import datetime
import logging
from bson import ObjectId

from ..core.database import mongodb, get_db
from ..core.persistent_authority import persistent_authority
from ..utils.file_handler import save_upload_file
from ..services.pdf_parser import IPDPDFParser

router = APIRouter()
logger = logging.getLogger(__name__)

async def insert_document_and_parts(doc_data: dict, parts: list, created_by: str = "system"):
    """Insert document and parts (tanpa transaction dulu)"""
    try:
        db = mongodb.db
        
        if db is None:
            logger.error("❌ Database not connected")
            return
        
        logger.info(f"📦 Received {len(parts)} parts to insert")
        
        # ===== CLEAN DOCUMENT =====
        clean_doc = {
            "document_id": doc_data.get("document_id"),
            "document_type": "IPD",
            "document_number": doc_data.get("document_number", ""),
            "revision": doc_data.get("revision", ""),
            "issue_date": doc_data.get("issue_date"),
            "aircraft_model": doc_data.get("aircraft_model", ""),
            "source_pdf_path": doc_data.get("source_pdf_path", ""),
            "file_hash": doc_data.get("file_hash", ""),
            "uploaded_at": datetime.utcnow(),
            "parsing_results": doc_data.get("parsing_results", {})
        }
        
        if "issue_date" in clean_doc and clean_doc["issue_date"] is None:
            del clean_doc["issue_date"]
        
        # Cek duplicate
        existing = await db.document.find_one({"document_id": clean_doc["document_id"]})
        if existing:
            logger.info(f"📄 Document already exists: {clean_doc['document_id']}")
            return {"status": "skipped", "document_id": existing["_id"]}
        
        # ===== INSERT DOCUMENT =====
        logger.info(f"📄 Inserting document: {clean_doc['document_id']}")
        doc_result = await db.document.insert_one(clean_doc)
        doc_id = doc_result.inserted_id
        logger.info(f"✅ Document inserted: {doc_id}")
        
        # ===== INSERT PARTS =====
        parts_to_insert = []
        for i, part in enumerate(parts):
            part_clean = {
                "ipd_part_id": f"{part['part_number']}_{doc_id}_{i}",
                "part_number": part["part_number"],
                "nomenclature": part.get("nomenclature", part["part_number"]),
                "change_type": part.get("change_type"),
                "figure": part.get("figure"),
                "item": part.get("item"),
                "supplier_code": part.get("supplier_code"),
                "effectivity_type": "LIST",
                "effectivity_values": part.get("effectivity_values", []),
                "effectivity_range": {},
                "upa": part.get("quantity"),
                "sb_reference": None,
                "page_number": part.get("page"),
                "confidence": part.get("confidence", 1.0),
                "document_id": doc_id,
                "created_at": datetime.utcnow()
            }
            parts_to_insert.append(part_clean)
        
        if parts_to_insert:
            result = await db.ipd_parts.insert_many(parts_to_insert)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} parts")
            
            # Update part master
            for part in parts_to_insert:
                await db.part_master.update_one(
                    {"part_number": part["part_number"]},
                    {
                        "$addToSet": {"linked_ipd_parts": doc_id},
                        "$setOnInsert": {"created_at": datetime.utcnow()}
                    },
                    upsert=True
                )
            
            # Register revision
            try:
                await persistent_authority.register_revision(
                    document_id=clean_doc["document_id"],
                    document_number=clean_doc["document_number"],
                    revision=clean_doc["revision"],
                    parts=parts_to_insert,
                    issue_date=clean_doc.get("issue_date"),
                    source_pdf_path=clean_doc["source_pdf_path"],
                    file_hash=clean_doc["file_hash"],
                    created_by=created_by
                )
                logger.info(f"✅ Revision registered")
            except Exception as e:
                logger.error(f"❌ Failed to register revision: {e}")
            
            # Audit log
            await db.audit.insert_one({
                "document_id": clean_doc["document_id"],
                "revision": clean_doc["revision"],
                "action": "UPLOAD",
                "created_by": created_by,
                "timestamp": datetime.utcnow(),
                "parts_count": len(parts_to_insert)
            })
        
        return {"status": "success", "document_id": clean_doc["document_id"], "parts": len(parts_to_insert)}
        
    except Exception as e:
        logger.error(f"❌ Insert failed: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

@router.post("/pdf", status_code=status.HTTP_202_ACCEPTED)
async def upload_ipd_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file"),
    created_by: str = "system"
):
    """Upload PDF dan parse otomatis"""
    logger.info(f"\n📤 Uploading: {file.filename}")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    try:
        # Simpan file
        file_info = await save_upload_file(file)
        
        # Parse PDF
        logger.info("🔍 Starting parser engine...")
        parser = IPDPDFParser(file_info["file_path"])
        parse_result = await parser.parse()
        
        if not parse_result["success"]:
            return {
                "success": True,
                "message": "File uploaded but parsing failed",
                "file_info": file_info,
                "parse_error": parse_result.get("error")
            }
        
        # DEBUG: Lihat struktur parse_result
        logger.info(f"📊 Parse result keys: {list(parse_result.keys())}")
        logger.info(f"📊 Parts found: {parse_result.get('total_parts', 0)}")
        
        # Siapkan document data
        doc_data = {
            "document_id": parse_result["metadata"].get("document_id") or file_info["stored_filename"],
            "document_type": "IPD",
            "document_number": parse_result["metadata"].get("document_number", ""),
            "revision": parse_result["metadata"].get("revision", ""),
            "issue_date": parse_result["metadata"].get("issue_date"),
            "aircraft_model": parse_result["metadata"].get("aircraft_model", "UNKNOWN"),
            "source_pdf_path": file_info["file_path"],
            "file_hash": file_info["file_hash"],
            "parsing_results": {
                "total_pages": parse_result["total_pages"],
                "parts_found": parse_result.get("total_parts", 0),  # ← FIX: pakai get()
                "total_candidates": parse_result.get("total_candidates", 0)
            }
        }
        
        # Background insert
        background_tasks.add_task(
            insert_document_and_parts,
            doc_data,
            parse_result["parts"],  # ← PARTS dari sini
            created_by
        )
        
        return {
            "success": True,
            "message": "File uploaded and queued for processing",
            "file_info": file_info,
            "parse_result": {
                "total_pages": parse_result["total_pages"],
                "parts_found": parse_result.get("total_parts", 0),
                "document_type": parse_result.get("document_type", "UNKNOWN"),
                "metadata": parse_result["metadata"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}", exc_info=True)
        raise HTTPException(500, detail=f"Upload failed: {str(e)}")