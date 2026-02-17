# backend/app/models/ipd_part.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

class EffectivityRange(BaseModel):
    from_: Optional[int] = Field(None, alias="from")
    to: Optional[int] = None

class ParserMetadata(BaseModel):
    confidence: float = 0.0
    page_number: int
    row_index: Optional[int] = None

class IPDPartModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ipd_part_id: str
    document_id: str  # Store as string for simplicity
    part_number: str
    
    # Basic fields
    nomenclature: Optional[str] = None
    figure: Optional[str] = None
    item: Optional[str] = None
    supplier_code: Optional[str] = None
    
    # Effectivity (core for Phase 1)
    effectivity_type: str  # LIST or RANGE
    effectivity_values: Optional[List[int]] = None
    effectivity_range: Optional[EffectivityRange] = None
    upa: Optional[int] = None
    
    # Metadata
    page_number: int
    confidence: float = 0.95
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}