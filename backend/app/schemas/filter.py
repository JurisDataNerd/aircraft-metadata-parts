from pydantic import BaseModel
from typing import List, Optional

class PartResult(BaseModel):
    part_number: str
    nomenclature: Optional[str] = None
    page_number: Optional[int] = None
    figure: Optional[str] = None
    change_type: Optional[str] = None
    sb_reference: Optional[str] = None
    upa: Optional[int] = None
    supplier_code: Optional[str] = None
    is_applicable: bool
    revision: Optional[str] = None

class FilterResponse(BaseModel):
    success: bool
    data: dict
    metadata: dict