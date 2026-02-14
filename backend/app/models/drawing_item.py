from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .document import PyObjectId

class DrawingItemModel(BaseModel):
    """Model untuk collection 'drawing_items' (FR-02)"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    drawing_item_id: str = Field(..., description="Unique item identifier")
    document_id: PyObjectId = Field(...)
    
    # Data dari drawing
    item_number: Optional[str] = None
    part_number: str = Field(...)
    title: Optional[str] = None
    sheet_number: Optional[str] = None
    material_spec: Optional[str] = None
    approval_authority: Optional[str] = None
    font_type: Optional[str] = None
    artwork_reference: Optional[str] = None
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "drawing_item_id": "A511351610-057",
                "part_number": "A511351610-057",
                "title": "ECB ELECTRONIC CONTROL BOX",
                "sheet_number": "2",
                "approval_authority": "EASA DOA"
            }
        }