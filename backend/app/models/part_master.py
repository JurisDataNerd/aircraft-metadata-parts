from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .document import PyObjectId

class PartMasterModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    part_number: str = Field(..., unique=True)
    
    # Referensi ke IPD parts (bisa banyak karena beda revisi)
    linked_ipd_parts: List[PyObjectId] = Field(default_factory=list)
    
    # Referensi ke drawing items
    linked_drawing_items: List[PyObjectId] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}