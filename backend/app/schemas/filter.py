from pydantic import BaseModel
from typing import List, Optional

class FilterRequest(BaseModel):
    line_number: int
    revision: Optional[str] = None

class PartResult(BaseModel):
    part_number: str
    nomenclature: Optional[str]
    page_number: Optional[int]
    figure: Optional[str]
    change_type: Optional[str]
    sb_reference: Optional[str]
    is_applicable: bool

class FilterResponse(BaseModel):
    line_number: int
    revision: str
    applicable_parts: List[PartResult]
    non_applicable_parts: List[PartResult]
    total_count: int