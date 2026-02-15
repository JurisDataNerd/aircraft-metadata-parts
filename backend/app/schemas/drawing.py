from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import datetime

class DrawingItemBase(BaseModel):
    drawing_item_id: str
    item_number: Optional[str] = None
    part_number: str
    title: Optional[str] = None
    sheet_number: Optional[str] = None
    material_spec: Optional[str] = None
    approval_authority: Optional[str] = None
    font_type: Optional[str] = None
    artwork_reference: Optional[str] = None
    notes: Optional[str] = None

class DrawingItemCreate(DrawingItemBase):
    document_id: str
    size: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

class DrawingItemUpdate(BaseModel):
    item_number: Optional[str] = None
    title: Optional[str] = None
    sheet_number: Optional[str] = None
    material_spec: Optional[str] = None
    approval_authority: Optional[str] = None
    font_type: Optional[str] = None
    artwork_reference: Optional[str] = None
    notes: Optional[str] = None
    size: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

class DrawingItemResponse(DrawingItemBase):
    id: str
    document_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    size: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }