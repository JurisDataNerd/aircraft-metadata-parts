from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom type untuk handling MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class DocumentModel(BaseModel):
    """Model untuk collection 'document' (FR-01, FR-02)"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str = Field(..., description="Unique document identifier")
    document_type: Literal['IPD', 'DRAWING'] = Field(...)
    document_number: str = Field(...)
    revision: str = Field(...)
    issue_date: Optional[datetime] = None
    aircraft_model: Optional[str] = None
    source_pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "document_id": "DMC-B787-A-11-25-03-030-941A-D__030.4",
                "document_type": "IPD",
                "document_number": "DMC-B787-A-11-25-03-030-941A-D",
                "revision": "030.4",
                "issue_date": "2022-06-20T00:00:00",
                "aircraft_model": "787-8",
                "source_pdf_path": "/pdfs/787/IPD-030.4.pdf"
            }
        }