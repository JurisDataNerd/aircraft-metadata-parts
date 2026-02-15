from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime
from bson import ObjectId
from enum import Enum

class RevisionStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"

class ChangeType(str, Enum):
    ADD = "ADD"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    RF = "RF"
    NONE = "NONE"

class PartChange(BaseModel):
    part_number: str
    change_type: ChangeType
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    fields_changed: List[str] = []

class RevisionMetadata(BaseModel):
    created_by: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    digital_signature: Optional[str] = None
    status: RevisionStatus = RevisionStatus.DRAFT

class RevisionNodeModel(BaseModel):
    """Persistent revision node - disimpan di MongoDB"""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    
    # Identitas
    document_id: str = Field(..., index=True)
    document_number: str
    revision: str = Field(..., index=True)
    
    # Relasi (jangan pakai None, tapi hapus field kalau null)
    previous_revision_id: Optional[ObjectId] = None
    next_revision_id: Optional[ObjectId] = None
    
    # Data
    parts: List[Dict] = []
    part_count: int = 0
    change_summary: Dict = {}
    changes: List[Dict] = []  # Simpan sebagai dict, bukan PartChange
    
    # Metadata
    issue_date: Optional[datetime] = None
    source_pdf_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Authority
    metadata: RevisionMetadata
    
    # Versioning
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def dict(self, *args, **kwargs):
        """Override dict untuk menghapus field None sebelum insert"""
        d = super().dict(*args, **kwargs)
        # Hapus field yang None
        return {k: v for k, v in d.items() if v is not None}
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}