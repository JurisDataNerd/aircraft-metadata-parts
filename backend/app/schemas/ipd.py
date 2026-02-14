from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import datetime

class IPDPartBase(BaseModel):
    ipd_part_id: str
    part_number: str
    nomenclature: Optional[str] = None
    effectivity_type: Literal['LIST', 'RANGE']
    effectivity_values: List[int] = Field(default_factory=list)
    effectivity_range: Dict[str, int] = Field(default_factory=dict)
    page_number: Optional[int] = None
    revision: str

    @validator('effectivity_values')
    def validate_effectivity_values(cls, v, values):
        if values.get('effectivity_type') == 'LIST' and not v:
            raise ValueError('effectivity_values required for LIST type')
        return v

    @validator('effectivity_range')
    def validate_effectivity_range(cls, v, values):
        if values.get('effectivity_type') == 'RANGE' and not v:
            raise ValueError('effectivity_range required for RANGE type')
        return v

class IPDPartCreate(IPDPartBase):
    document_id: str
    change_type: Optional[Literal['ADD', 'MODIFY', 'DELETE']] = None
    figure: Optional[str] = None
    item: Optional[str] = None
    supplier_code: Optional[str] = None
    upa: Optional[int] = None
    sb_reference: Optional[str] = None
    placard_content: Optional[str] = None
    metadata: Optional[Dict] = None

class IPDPartResponse(IPDPartBase):
    id: str
    document_id: str
    created_at: datetime
    change_type: Optional[str] = None
    figure: Optional[str] = None
    item: Optional[str] = None
    supplier_code: Optional[str] = None
    upa: Optional[int] = None
    sb_reference: Optional[str] = None
    placard_content: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }