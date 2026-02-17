# backend/app/models/ipd_part.py (update juga)
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

class EffectivityRange(BaseModel):
    from_: Optional[int] = Field(None, alias="from")
    to: Optional[int] = None

class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic v2 compatibility"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> Any:
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(ObjectId),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update(type='string', example='507f1f77bcf86cd799439011')
        return json_schema

class IPDPartModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ipd_part_id: str
    document_id: str
    part_number: str
    
    # Basic fields
    nomenclature: Optional[str] = None
    figure: Optional[str] = None
    item: Optional[str] = None
    supplier_code: Optional[str] = None
    
    # Effectivity
    effectivity_type: str
    effectivity_values: Optional[List[int]] = None
    effectivity_range: Optional[EffectivityRange] = None
    upa: Optional[int] = None
    
    # Metadata
    page_number: int
    confidence: float = 0.95
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}