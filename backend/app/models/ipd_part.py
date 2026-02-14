from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
from bson import ObjectId
from .document import PyObjectId

class IPDPartModel(BaseModel):
    """Model untuk collection 'ipd_parts' (FR-01)"""
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
    
    # Effectivity — inti filtering
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
    def validate_effectivity(cls, v, values):
        """Validasi depend on effectivity_type"""
        if values.get('effectivity_type') == 'LIST' and not v:
            raise ValueError('effectivity_values required for LIST type')
        return v
    
    @validator('effectivity_range', always=True)
    def validate_range(cls, v, values):
        """Validasi depend on effectivity_type"""
        if values.get('effectivity_type') == 'RANGE' and not v:
            raise ValueError('effectivity_range required for RANGE type')
        return v
    
    def is_applicable(self, line_number: int) -> bool:
        """
        FR-03: Deterministic filtering based on effectivity
        Returns True/False
        """
        if not line_number:
            return False
        
        if self.effectivity_type == 'LIST':
            return line_number in self.effectivity_values
        else:  # RANGE
            from_val = self.effectivity_range.get('from', 0)
            to_val = self.effectivity_range.get('to', 0)
            return from_val <= line_number <= to_val
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "ipd_part_id": "867Z2251-28-030.4",
                "part_number": "867Z2251-28",
                "nomenclature": "STENCIL",
                "effectivity_type": "LIST",
                "effectivity_values": [68, 74, 80, 113, 118, 185, 195],
                "page_number": 5,
                "revision": "030.4"
            }
        }