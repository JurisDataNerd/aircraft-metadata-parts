from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
from bson import ObjectId
from .document import PyObjectId

class IPDPartModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ipd_part_id: str = Field(..., description="Unique part identifier per revision")
    document_id: PyObjectId = Field(...)
    
    # Data dari tabel IPD
    change_type: Optional[Literal['ADD', 'MODIFY', 'DELETE']] = None
    figure: Optional[str] = None
    item: Optional[str] = None
    part_number: str = Field(...)
    nomenclature: Optional[str] = None
    supplier_code: Optional[str] = None
    
    # Effectivity
    effectivity_type: Literal['LIST', 'RANGE'] = Field(...)
    effectivity_values: List[int] = Field(default_factory=list)
    effectivity_range: Dict[str, int] = Field(default_factory=dict)
    
    # Metadata
    upa: Optional[int] = None
    sb_reference: Optional[str] = None
    page_number: Optional[int] = None
    revision: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('effectivity_values', always=True)
    def validate_effectivity_values(cls, v, values):
        if values.get('effectivity_type') == 'LIST' and not v:
            raise ValueError('effectivity_values required for LIST type')
        return v
    
    @validator('effectivity_range', always=True)
    def validate_effectivity_range(cls, v, values):
        if values.get('effectivity_type') == 'RANGE' and not v:
            raise ValueError('effectivity_range required for RANGE type')
        return v
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}