import fitz
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ==========================================================
# ENUMS & DATA CLASSES
# ==========================================================

class DocumentType(Enum):
    UNKNOWN = "unknown"
    BOEING_IPD = "boeing_ipd"
    AIRBUS_IPT = "airbus_ipt"
    DRAWING_PLACARD = "drawing_placard"

class PartNumberType(Enum):
    BOEING = "boeing"           # 867Z2303-5
    LA_GR = "la_gr"             # LA-GR-100
    TF = "tf"                   # TF104544
    DRAWING = "drawing"         # A511351610-057
    OEM_REF = "oem_ref"         # V1147010211800
    UNKNOWN = "unknown"

class ValidationStatus(Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    AMBIGUOUS = "ambiguous"

@dataclass
class RawField:
    """Field mentah hasil ekstraksi"""
    value: str
    source_text: str
    page: int
    bbox: Optional[Tuple[float, float, float, float]] = None
    confidence: float = 1.0
    font_size: float = 0.0
    font_name: str = ""

@dataclass
class CandidatePart:
    """Kandidat part sebelum validasi"""
    raw_part_number: RawField
    raw_nomenclature: Optional[RawField] = None
    raw_effectivity: List[RawField] = field(default_factory=list)
    raw_supplier_code: Optional[RawField] = None
    raw_quantity: Optional[RawField] = None
    raw_change_type: Optional[RawField] = None
    raw_figure: Optional[RawField] = None
    raw_item: Optional[RawField] = None
    
    page: int = 0
    column_position: int = 0
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[str] = field(default_factory=list)

@dataclass
class ValidatedPart:
    """Part yang sudah divalidasi"""
    part_number: str
    part_type: PartNumberType
    nomenclature: str
    change_type: Optional[str]
    figure: Optional[str]
    item: Optional[str]
    supplier_code: Optional[str]
    effectivity_values: List[int]
    quantity: Optional[int]
    page: int
    document_id: Optional[str]
    confidence: float
    validation_log: List[str]
    validated_at: datetime


# ==========================================================
# LAYER 1: RAW EXTRACTION (FIXED)
# ==========================================================
class RawExtractor:
    """Layer 1: Ambil semua field mentah dengan posisi"""
    
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)
        self.raw_fields_by_page: Dict[int, List[RawField]] = {}
        
    def extract_all(self) -> Dict[int, List[RawField]]:
        """Ekstrak semua teks dengan bounding box"""
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            fields = []
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text or len(text) < 2:
                            continue
                        
                        # AMAN: Cek keberadaan key
                        bbox = None
                        if "bbox" in span:
                            bbox = tuple(span["bbox"])
                        elif "origin" in span and "width" in span:
                            x0 = span["origin"][0]
                            y0 = span["origin"][1]
                            x1 = x0 + span["width"]
                            y1 = y0 + span.get("size", 10)
                            bbox = (x0, y0, x1, y1)
                        
                        fields.append(RawField(
                            value=text,
                            source_text=text,
                            page=page_num + 1,
                            bbox=bbox,
                            confidence=1.0,
                            font_size=span.get("size", 0),
                            font_name=span.get("font", "")
                        ))
            
            self.raw_fields_by_page[page_num + 1] = fields
            print(f"   Page {page_num + 1}: {len(fields)} fields extracted")
            
        return self.raw_fields_by_page


# ==========================================================
# LAYER 2: STRUCTURAL GROUPING
# ==========================================================
class StructuralGrouper:
    """Layer 2: Kelompokkan field ke dalam baris berdasarkan posisi"""
    
    def __init__(self, raw_fields: Dict[int, List[RawField]], y_tolerance: float = 5.0):
        self.raw_fields = raw_fields
        self.y_tolerance = y_tolerance
        
    def group_by_rows(self) -> Dict[int, List[List[RawField]]]:
        """Kelompokkan field per baris"""
        rows_by_page = {}
        
        for page_num, fields in self.raw_fields.items():
            # Filter fields dengan bbox
            fields_with_bbox = [f for f in fields if f.bbox]
            if not fields_with_bbox:
                rows_by_page[page_num] = []
                continue
                
            # Urutkan berdasarkan Y
            sorted_fields = sorted(fields_with_bbox, key=lambda f: f.bbox[1])
            
            rows = []
            current_row = []
            current_y = None
            
            for field in sorted_fields:
                field_y = field.bbox[1]
                
                if current_y is None:
                    current_y = field_y
                    current_row.append(field)
                elif abs(field_y - current_y) <= self.y_tolerance:
                    current_row.append(field)
                else:
                    if current_row:
                        rows.append(sorted(current_row, key=lambda f: f.bbox[0]))
                    current_row = [field]
                    current_y = field_y
            
            if current_row:
                rows.append(sorted(current_row, key=lambda f: f.bbox[0]))
            
            rows_by_page[page_num] = rows
            print(f"   Page {page_num}: {len(rows)} rows detected")
            
        return rows_by_page
    
    def detect_table_structure(self, rows: List[List[RawField]]) -> Dict:
        """Deteksi struktur tabel"""
        if not rows:
            return {"has_table": False, "column_count": 0}
        
        # Hitung jumlah field per baris
        field_counts = [len(row) for row in rows if row]
        if not field_counts:
            return {"has_table": False, "column_count": 0}
        
        from collections import Counter
        count_mode = Counter(field_counts).most_common(1)[0][0]
        
        # Baris dengan jumlah field konsisten
        consistent_rows = [row for row in rows if len(row) == count_mode]
        
        return {
            "has_table": count_mode >= 2,
            "column_count": count_mode,
            "total_rows": len(rows),
            "consistent_rows": len(consistent_rows),
            "confidence": len(consistent_rows) / len(rows) if rows else 0
        }


# ==========================================================
# LAYER 3: SEMANTIC VALIDATION
# ==========================================================
class SemanticValidator:
    """Layer 3: Validasi tipe data dan format"""
    
    # Pattern part number yang dikenal
    KNOWN_PATTERNS = {
        PartNumberType.BOEING: re.compile(r'^867Z\d{4}-\d{1,2}$'),
        PartNumberType.LA_GR: re.compile(r'^LA-GR-\d{3}$'),
        PartNumberType.TF: re.compile(r'^TF\d{6}$'),
        PartNumberType.DRAWING: re.compile(r'^[A-Z]\d{9}-\d{3}$'),
    }
    
    # Line numbers Boeing yang dikenal
    KNOWN_LINE_NUMBERS = {68,74,80,113,118,185,195,205,210,234,556,584,647,680,715}
    
    def validate_part_number(self, text: str) -> Tuple[bool, PartNumberType, str]:
        """Validasi apakah string ini part number"""
        text = text.strip()
        
        for ptype, pattern in self.KNOWN_PATTERNS.items():
            if pattern.match(text):
                return True, ptype, text
        
        # Cek format umum
        if re.match(r'^[A-Z0-9]{2,8}-\d{1,4}$', text):
            return True, PartNumberType.UNKNOWN, text
        
        return False, PartNumberType.UNKNOWN, text
    
    def validate_effectivity(self, text: str) -> List[int]:
        """Validasi effectivity dari teks"""
        numbers = re.findall(r'\b(\d{2,3})\b', text)
        valid = []
        
        for num in numbers:
            val = int(num)
            if 10 <= val <= 999:
                if val in self.KNOWN_LINE_NUMBERS:
                    valid.append(val)
                elif len(valid) < 5:  # Accept if we already have some
                    valid.append(val)
        
        return list(set(valid))[:15]
    
    def validate_quantity(self, text: str) -> Optional[int]:
        """Validasi quantity"""
        try:
            val = int(text)
            if 1 <= val <= 100:
                return val
        except ValueError:
            pass
        return None
    
    def validate_change_type(self, text: str) -> Optional[str]:
        """Validasi change type"""
        if text.upper() in ["ADD", "MODIFY", "DELETE", "RF"]:
            return text.upper()
        return None


# ==========================================================
# MAIN PARSER ENGINE
# ==========================================================
class ParserEngine:
    """Main parser engine dengan 4-layer architecture"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_extractor = RawExtractor(pdf_path)
        self.validator = SemanticValidator()
        
        self.candidates: List[CandidatePart] = []
        self.validated_parts: List[ValidatedPart] = []
        self.document_type = DocumentType.UNKNOWN
        self.metadata = {}
        
    async def process(self) -> Dict:
        """Jalankan seluruh pipeline"""
        try:
            print(f"\n{'='*60}")
            print("🔍 STARTING PARSER ENGINE")
            print(f"{'='*60}")
            
            # Layer 1: Raw extraction
            print("\n📥 Layer 1: Raw Extraction")
            raw_fields = self.raw_extractor.extract_all()
            total_fields = sum(len(f) for f in raw_fields.values())
            print(f"   Total fields: {total_fields}")
            
            # Layer 2: Structural grouping
            print("\n📐 Layer 2: Structural Grouping")
            grouper = StructuralGrouper(raw_fields)
            rows_by_page = grouper.group_by_rows()
            
            # Deteksi tipe dokumen
            self.document_type = self._detect_document_type(rows_by_page)
            print(f"   Document type: {self.document_type.value}")
            
            # Ekstrak metadata
            self.metadata = self._extract_metadata(raw_fields.get(1, []))
            
            # Layer 3: Create candidates
            print("\n🔧 Layer 3: Creating Candidates")
            self.candidates = self._create_candidates(rows_by_page)
            print(f"   Total candidates: {len(self.candidates)}")
            
            # Layer 4: Validate candidates
            print("\n✅ Layer 4: Validating Candidates")
            self.validated_parts = self._validate_candidates(self.candidates)
            print(f"   Validated parts: {len(self.validated_parts)}")
            
            return {
                "success": True,
                "document_type": self.document_type.value,
                "metadata": self.metadata,
                "parts": [self._part_to_dict(p) for p in self.validated_parts],
                "total_parts": len(self.validated_parts),  # ← INI YANG DIPAKAI
                "total_candidates": len(self.candidates),
                "total_pages": len(raw_fields)
            }
            
        except Exception as e:
            print(f"❌ Parser engine failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "parts": []
            }
    
    def _detect_document_type(self, rows_by_page: Dict[int, List[List[RawField]]]) -> DocumentType:
        """Deteksi tipe dokumen dari struktur"""
        # Cek halaman 1
        page1_rows = rows_by_page.get(1, [])
        
        for row in page1_rows:
            row_text = " ".join(f.value for f in row)
            
            if "CHANGE TYPE" in row_text and "PART NUMBER" in row_text:
                return DocumentType.BOEING_IPD
            if "DRAWING SHEET" in row_text or "PLACARD" in row_text:
                return DocumentType.DRAWING_PLACARD
        
        return DocumentType.UNKNOWN
    
    def _extract_metadata(self, page1_fields: List[RawField]) -> Dict:
        """Ekstrak metadata dari halaman 1"""
        metadata = {
            "document_id": None,
            "document_number": None,
            "revision": None,
            "issue_date": None,
            "aircraft_model": None,
            "operator": None,
            "ata_chapter": None,
            "drawing_number": None
        }
        
        text = " ".join(f.value for f in page1_fields)
        
        # DMC
        dmc_match = re.search(r'(DMC-[A-Z0-9][A-Z0-9\-]*[A-Z0-9])', text)
        if dmc_match:
            metadata["document_number"] = dmc_match.group(1)
            metadata["document_id"] = dmc_match.group(1)
        
        # Revision
        rev_match = re.search(r'Issue\s+([\d.]+)', text, re.IGNORECASE)
        if rev_match:
            metadata["revision"] = rev_match.group(1)
        
        # Aircraft model
        if "787-8" in text:
            metadata["aircraft_model"] = "787-8"
        elif "A350" in text:
            metadata["aircraft_model"] = "A350-1041"
        
        # Operator
        if "LAN" in text:
            metadata["operator"] = "LAN"
        
        # ATA
        ata_match = re.search(r'\b(\d{2}-\d{2}-\d{2})\b', text)
        if ata_match:
            metadata["ata_chapter"] = ata_match.group(1)
        
        # Drawing number
        drawing_match = re.search(r'\b([A-Z]\d{9})\b', text)
        if drawing_match:
            metadata["drawing_number"] = drawing_match.group(1)
        
        return metadata
    
    def _create_candidates(self, rows_by_page: Dict[int, List[List[RawField]]]) -> List[CandidatePart]:
        """Buat kandidat part dari rows"""
        candidates = []
        
        for page_num, rows in rows_by_page.items():
            for row in rows:
                if len(row) < 2:
                    continue
                
                # Cari part number di baris ini
                for field in row:
                    is_valid, ptype, normalized = self.validator.validate_part_number(field.value)
                    
                    if is_valid:
                        # Buat candidate sederhana
                        candidate = CandidatePart(
                            raw_part_number=field,
                            page=page_num
                        )
                        
                        # Ambil seluruh teks baris untuk effectivity
                        row_text = " ".join(f.value for f in row)
                        effectivity = self.validator.validate_effectivity(row_text)
                        
                        for val in effectivity:
                            candidate.raw_effectivity.append(RawField(
                                value=str(val),
                                source_text=row_text,
                                page=page_num
                            ))
                        
                        candidates.append(candidate)
                        break
        
        return candidates
    
    def _validate_candidates(self, candidates: List[CandidatePart]) -> List[ValidatedPart]:
        """Validasi kandidat menjadi part"""
        validated = []
        
        for cand in candidates:
            part_num = cand.raw_part_number.value
            is_valid, ptype, _ = self.validator.validate_part_number(part_num)
            
            if not is_valid:
                continue
            
            # Ambil effectivity
            effectivity = []
            if cand.raw_effectivity:
                text = " ".join(f.value for f in cand.raw_effectivity)
                effectivity = self.validator.validate_effectivity(text)
            
            validated_part = ValidatedPart(
                part_number=part_num,
                part_type=ptype,
                nomenclature=part_num,
                change_type=None,
                figure=None,
                item=None,
                supplier_code=None,
                effectivity_values=effectivity,
                quantity=None,
                page=cand.page,
                document_id=None,
                confidence=0.8 if effectivity else 0.5,
                validation_log=[],
                validated_at=datetime.utcnow()
            )
            
            validated.append(validated_part)
        
        return validated
    
    def _part_to_dict(self, part: ValidatedPart) -> Dict:
        """Konversi ke dict untuk response"""
        return {
            "part_number": part.part_number,
            "part_type": part.part_type.value,
            "nomenclature": part.nomenclature,
            "change_type": part.change_type,
            "effectivity_values": part.effectivity_values,
            "quantity": part.quantity,
            "page": part.page,
            "confidence": part.confidence,
            "validated": True
        }