import os
import aiofiles
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile

# Buat folder uploads jika belum ada
UPLOAD_DIR = Path("uploads/ipd")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_upload_file(file: UploadFile) -> dict:
    """
    Simpan file PDF ke disk dan return metadata
    """
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Simpan file
    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Hitung hash untuk verifikasi
    file_hash = hashlib.sha256(content).hexdigest()
    
    return {
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "file_hash": file_hash,
        "uploaded_at": datetime.utcnow().isoformat()
    }

async def file_exists(file_hash: str) -> bool:
    """Cek apakah file dengan hash tertentu sudah ada di database"""
    from core.database import get_db
    db = get_db()
    existing = await db.document.find_one({"file_hash": file_hash})
    return existing is not None 

def compute_file_hash(file_path: str) -> str:
    """Hitung hash file dari path"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
