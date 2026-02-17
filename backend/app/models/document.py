# backend/app/models/document.py
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId
from typing import Any, Optional
from datetime import datetime

class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic v2 compatibility"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> Any:
        # Return a core schema that tells Pydantic how to validate and serialize
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(ObjectId),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        # Generate JSON schema
        json_schema = handler(core_schema)
        json_schema.update(type='string', example='507f1f77bcf86cd799439011')
        return json_schema

class DocumentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    document_id: str
    document_type: str
    document_number: str
    revision: str = "unknown"
    issue_date: Optional[datetime] = None
    aircraft_model: Optional[str] = None
    source_pdf_path: Optional[str] = None
    file_hash: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    parsing_status: str = "pending"
    parts_count: int = 0
    
    class Config:
        populate_by_name = True  # Ganti dari allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}