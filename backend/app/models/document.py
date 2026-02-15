from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
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
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str = Field(..., description="Unique document identifier")
    document_type: Literal['IPD', 'DRAWING'] = Field(...)  # HARUS IPD atau DRAWING
    document_number: str = Field(...)
    revision: str = Field(...)
    issue_date: Optional[datetime] = None  # Boleh None
    aircraft_model: Optional[str] = None
    source_pdf_path: Optional[str] = None
    file_hash: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}