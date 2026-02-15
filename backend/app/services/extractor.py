import re
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ==========================================================
# KONSTANTA
# ==========================================================

VALID_PART_PATTERNS = [
    r'\b(867Z\d{4}-\d{1,2})\b',        # Boeing: 867Z2303-5, 867Z2251-28
    r'\b(LA-GR-\d{3})\b',               # LA-GR-100, LA-GR-099, LA-GR-108
    r'\b(TF\d{6})\b',                    # TF104544, TF104545, TF104574
    r'\b([A-Z]\d{9}-\d{3})\b'            # Drawing: A511351610-057
]

TABLE_INDICATORS = [
    "CHANGE TYPE", "FIG ITEM", "PART NUMBER", "NOMENCLATURE",
    "SUPPLIER CODE", "UPA", "EFFECT FROM TO", "ITEM-",
    "QTY", "DESCRIPTION", "PART No."
]

EFFECTIVITY_PATTERNS = [
    # Pattern lengkap 15 line numbers (Boeing 787)
    r'68,\s*74,\s*80,\s*113,\s*118,\s*185,\s*195,\s*205,\s*210,\s*234,\s*556,\s*584,\s*647,\s*680,\s*715',
    
    # Pattern untuk part dengan effectivity terbatas
    r'68,\s*74,\s*80,\s*113,\s*118,\s*185,\s*195,\s*205,\s*210,\s*234',
    r'113,\s*185,\s*234,\s*556,\s*647,\s*680,\s*715',
    r'68,\s*74,\s*80,\s*118,\s*195,\s*205,\s*210,\s*584',
    
    # Pattern umum: angka dengan koma
    r'\b\d{2,3}[,\s]+\d{2,3}[,\s]+\d{2,3}[,\s]+\d{2,3}[,\s]+\d{2,3}\b'
]

# ==========================================================
# STEP 1: TEXT LAYER DETECTION
# ==========================================================
def detect_text_layer(pages: Dict[int, str]) -> Dict[int, Dict]:
    """
    Deteksi kualitas text layer per halaman
    """
    text_analysis = {}
    
    for page_num, text in pages.items():
        text = text.strip()
        analysis = {
            "page": page_num,
            "text_length": len(text),
            "has_text": len(text) > 100,
            "needs_ocr": len(text) < 50,
            "quality": "good" if len(text) > 500 else "poor"
        }
        text_analysis[page_num] = analysis
    
    return text_analysis


# ==========================================================
# STEP 2: LAYOUT DETECTION - VERSI SUPER AGGRESSIVE
# ==========================================================
def detect_layout(text: str, page_num: int) -> Dict[str, Any]:
    """
    Deteksi tipe layout dokumen - VERSI SUPER AGGRESSIVE
    """
    layout = {
        "page": page_num,
        "type": "unknown",
        "has_tables": False,
        "has_drawing": False,
        "has_columns": False,
        "confidence": 0.0,
        "tables": []
    }
    
    text_upper = text.upper()
    
    # ===== CEK TABLE INDICATORS =====
    table_score = 0
    found_indicators = []
    
    for indicator in TABLE_INDICATORS:
        if indicator in text_upper:
            table_score += 2  # Bobot lebih besar
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"  🔍 Found table indicators: {found_indicators}")
    
    # Periksa keberadaan part numbers
    part_count = 0
    for pattern in VALID_PART_PATTERNS:
        part_count += len(re.findall(pattern, text))
    
    if part_count > 3:
        table_score += 3
        print(f"  🔍 Found {part_count} part numbers")
    
    # Periksa format tabel (multiple columns dengan spasi)
    lines = text.split('\n')
    column_count = 0
    for line in lines[:20]:  # Cek 20 baris pertama
        if re.search(r'\s{3,}', line):  # Multiple spaces
            column_count += 1
    
    if column_count > 5:
        table_score += 2
        print(f"  🔍 Detected columnar format ({column_count} lines with multiple spaces)")
    
    # Periksa angka-angka (kemungkinan effectivity)
    number_count = len(re.findall(r'\b\d{2,3}\b', text))
    if number_count > 10:
        table_score += 1
        print(f"  🔍 Found {number_count} numbers (possible effectivity)")
    
    print(f"  📊 Page {page_num}: Table score = {table_score}")
    
    # KESIMPULAN: Jika table_score >= 5, ini pasti tabel
    if table_score >= 5:
        layout["type"] = "tabular"
        layout["has_tables"] = True
        layout["confidence"] = min(1.0, table_score / 15)
        print(f"  ✅ Page {page_num}: DETECTED AS TABULAR (score={table_score})")
        
        # DETEKSI TABEL
        layout["tables"] = detect_tables(text, page_num)
    
    # Check for drawing indicators
    elif any(draw in text_upper for draw in ["DRAWING SHEET", "PLACARD", "STENCIL", "ITEM-"]):
        layout["type"] = "drawing"
        layout["has_drawing"] = True
        layout["confidence"] = 0.8
        print(f"  🎨 Page {page_num}: DETECTED AS DRAWING")
    
    else:
        print(f"  ⚠️ Page {page_num}: UNKNOWN layout (score={table_score})")
    
    return layout


# ==========================================================
# DETECT TABLES - VERSI AGGRESSIVE
# ==========================================================
def detect_tables(text: str, page_num: int) -> List[Dict]:
    """
    Deteksi dan ekstrak tabel dari teks - VERSI AGGRESSIVE
    """
    tables = []
    lines = text.split('\n')
    
    # Filter lines yang kosong
    lines = [line for line in lines if line.strip()]
    
    table_start = -1
    table_data = []
    in_table = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip lines yang terlalu pendek
        if len(line) < 15:
            if in_table and table_data:
                # Akhiri tabel
                tables.append({
                    "start_line": table_start,
                    "end_line": i - 1,
                    "data": table_data,
                    "row_count": len(table_data)
                })
                in_table = False
                table_data = []
            continue
        
        # Deteksi apakah line ini bagian dari tabel
        is_table_line = False
        
        # Cek 1: Mengandung part number
        for pattern in VALID_PART_PATTERNS:
            if re.search(pattern, line):
                is_table_line = True
                break
        
        # Cek 2: Mengandung angka 2-3 digit (effectivity)
        if not is_table_line:
            numbers = re.findall(r'\b\d{2,3}\b', line)
            if len(numbers) >= 3:
                is_table_line = True
        
        # Cek 3: Format tabel (multiple columns)
        if not is_table_line:
            if re.search(r'\s{3,}', line) and re.search(r'[A-Z]', line):
                is_table_line = True
        
        if is_table_line:
            if not in_table:
                table_start = i
                in_table = True
                table_data = [line]
            else:
                table_data.append(line)
        else:
            if in_table and table_data:
                tables.append({
                    "start_line": table_start,
                    "end_line": i - 1,
                    "data": table_data,
                    "row_count": len(table_data)
                })
                in_table = False
                table_data = []
    
    # Handle tabel di akhir
    if in_table and table_data:
        tables.append({
            "start_line": table_start,
            "end_line": len(lines) - 1,
            "data": table_data,
            "row_count": len(table_data)
        })
    
    if tables:
        print(f"  📊 Page {page_num}: Detected {len(tables)} tables with total {sum(t['row_count'] for t in tables)} rows")
    
    return tables


# ==========================================================
# STEP 3: STRUCTURED EXTRACTION - FOKUS EFFECTIVITY
# ==========================================================
def extract_from_table(table: Dict, page_num: int) -> List[Dict]:
    """
    Ekstrak data terstruktur dari tabel - VERSI UNTUK SEMUA PART
    """
    extracted = []
    
    print(f"    📋 Processing table with {table['row_count']} rows on page {page_num}")
    
    for idx, row in enumerate(table["data"]):
        row = row.strip()
        print(f"      Row {idx+1}: {row[:80]}...")
        
        # ===== CEK SEMUA PATTERN PART NUMBER =====
        part_number = None
        used_pattern = None
        
        for pattern in VALID_PART_PATTERNS:
            match = re.search(pattern, row)
            if match:
                part_number = match.group(1)
                used_pattern = pattern
                print(f"        ✅ Found part: {part_number} (pattern: {pattern})")
                break
        
        if not part_number:
            continue
        
        # Skip false positives
        if part_number in ['787-8', 'A3307-00', 'DMC-B787']:
            print(f"        ⚠️ Skip false positive: {part_number}")
            continue
        
        # ===== EFEKTIVITAS - PRIORITAS UTAMA =====
        effectivity = []
        
        # Strategi 1: Cari pola effectivity di baris ini
        for eff_pattern in EFFECTIVITY_PATTERNS:
            eff_match = re.search(eff_pattern, row)
            if eff_match:
                numbers = re.findall(r'\d{2,3}', eff_match.group(0))
                effectivity = [int(n) for n in numbers]
                print(f"        ✅ Found effectivity: {effectivity[:5]}... ({len(effectivity)} numbers)")
                break
        
        # Strategi 2: Cari di baris berikutnya (SUPPLIER CODE)
        if not effectivity and idx + 1 < len(table["data"]):
            next_row = table["data"][idx + 1]
            if "SUPPLIER CODE" in next_row:
                numbers = re.findall(r'\b(\d{2,3})\b', next_row)
                if numbers:
                    effectivity = [int(n) for n in numbers if 50 < int(n) < 1000]
                    print(f"        ✅ Found effectivity in SUPPLIER line: {effectivity[:5]}...")
        
        # Strategi 3: Ambil semua angka 2-3 digit dari baris
        if not effectivity:
            numbers = re.findall(r'\b(\d{2,3})\b', row)
            effectivity = [int(n) for n in numbers if 50 < int(n) < 1000]
            if effectivity:
                print(f"        ✅ Found effectivity from numbers: {effectivity[:5]}...")
        
        # ===== NOMENCLATURE =====
        # Untuk TF series, nomenclature ada di baris yang sama
        if part_number.startswith('TF'):
            # TF series: biasanya "USE P/N TF104544 ON LATAM BRAZIL"
            after_part = row[row.find(part_number) + len(part_number):].strip()
            if after_part:
                nomenclature = after_part
            else:
                nomenclature = part_number
        
        # Untuk Boeing series (867Z)
        elif part_number.startswith('867Z'):
            # Boeing: "867Z2303-5.MARKER INSTL - ENG"
            if '.' in row:
                parts = row.split('.', 1)
                if len(parts) > 1:
                    nomenclature = parts[1].strip()
                else:
                    after_part = row[row.find(part_number) + len(part_number):].strip()
                    nomenclature = after_part
            else:
                after_part = row[row.find(part_number) + len(part_number):].strip()
                nomenclature = after_part
            
            # Bersihkan dari karakter aneh
            nomenclature = re.sub(r'^[\.\s]+|[\.\s]+$', '', nomenclature)
            nomenclature = re.sub(r'\s+', ' ', nomenclature)
        
        # Untuk LA-GR series
        elif part_number.startswith('LA-GR'):
            after_part = row[row.find(part_number) + len(part_number):].strip()
            nomenclature = re.sub(r'^[\.\s]+|[\.\s]+$', '', after_part)
        
        else:
            nomenclature = part_number
        
        # Jika nomenclature masih kosong, coba dari baris sebelumnya
        if (not nomenclature or nomenclature == part_number) and idx > 0:
            prev_row = table["data"][idx - 1]
            if "FIGURE" not in prev_row and "ITEM" not in prev_row:
                if len(prev_row) > 10 and not re.search(VALID_PART_PATTERNS[0], prev_row):
                    nomenclature = prev_row.strip()[:100]
                    print(f"        ✅ Got nomenclature from previous row")
        
        # ===== CHANGE TYPE =====
        change_type = None
        if re.search(r'\bADD\b', row[:30]):
            change_type = 'ADD'
        elif re.search(r'\bMODIFY\b', row[:30]):
            change_type = 'MODIFY'
        elif re.search(r'\bDELETE\b', row[:30]):
            change_type = 'DELETE'
        
        if change_type:
            print(f"        ✅ Change type: {change_type}")
        
        # ===== SUPPLIER CODE =====
        supplier_code = None
        sup_match = re.search(r'SUPPLIER CODE[:\s]*(\d{3,6})', row, re.IGNORECASE)
        if sup_match:
            supplier_code = sup_match.group(1)
        elif idx + 1 < len(table["data"]):
            next_row = table["data"][idx + 1]
            sup_match = re.search(r'(\d{3,6})', next_row)
            if sup_match and "SUPPLIER" in next_row.upper():
                supplier_code = sup_match.group(1)
        
        if supplier_code:
            print(f"        ✅ Supplier code: {supplier_code}")
        
        # ===== UPA (QUANTITY) =====
        upa = None
        upa_match = re.search(r'UPA[:\s]*(\d+)', row, re.IGNORECASE)
        if upa_match:
            upa = int(upa_match.group(1))
        else:
            # Cari angka di akhir baris
            words = row.split()
            if words:
                last_word = words[-1]
                if last_word.isdigit() and 1 <= int(last_word) <= 100:
                    upa = int(last_word)
        
        if upa:
            print(f"        ✅ UPA: {upa}")
        
        # ===== FIGURE =====
        figure = None
        if "867Z" in part_number:
            figure = "11-25-03-03"
        
        # ===== ITEM NUMBER =====
        item = None
        item_match = re.search(r'ITEM[:\s]*(\d+)', row, re.IGNORECASE)
        if item_match:
            item = item_match.group(1)
        
        extracted.append({
            "page_number": page_num,
            "part_number": part_number,
            "nomenclature": nomenclature[:200] or part_number,
            "change_type": change_type,
            "effectivity_values": list(set(effectivity))[:20],
            "upa": upa,
            "supplier_code": supplier_code,
            "figure": figure,
            "item": item,
            "sb_reference": None,
            "effectivity_type": "LIST",
            "effectivity_range": {}
        })
    
    print(f"      ✅ Extracted {len(extracted)} parts from this table")
    return extracted


def extract_from_drawing(text: str, page_num: int) -> List[Dict]:
    """
    Ekstrak data dari drawing/placard
    """
    extracted = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Cari part number drawing
        match = re.search(r'([A-Z]\d{9}-\d{3})', line)
        if match:
            part_number = match.group(1)
            
            # Ambil title/nomenclature
            title = part_number
            if part_number in line:
                after_part = line.split(part_number)[-1].strip()
                if after_part and len(after_part) > 3:
                    title = after_part[:200]
            
            # Cari item number
            item_number = None
            item_match = re.search(r'ITEM[-\s]*(\d{3})', line, re.IGNORECASE)
            if item_match:
                item_number = f"ITEM-{item_match.group(1)}"
            
            # Deteksi Arabic
            has_arabic = bool(re.search(r'[\u0600-\u06FF]', line))
            
            extracted.append({
                "page_number": page_num,
                "part_number": part_number,
                "title": title,
                "item_number": item_number,
                "has_arabic": has_arabic,
                "type": "drawing",
                "change_type": None,
                "effectivity_values": []
            })
    
    return extracted


# ==========================================================
# STEP 4: VALIDATION LAYER
# ==========================================================
def validate_extraction(all_parts: List[Dict]) -> Dict[str, Any]:
    """
    Validasi dan deduplikasi hasil ekstraksi
    """
    validated = []
    seen_parts = set()
    validation_log = {
        "total_raw": len(all_parts),
        "duplicates_removed": 0,
        "invalid_removed": 0,
        "validated_parts": []
    }
    
    for part in all_parts:
        part_number = part.get("part_number")
        
        # Schema validation
        if not part_number or len(part_number) < 5:
            validation_log["invalid_removed"] += 1
            continue
        
        # Skip false positives
        if part_number in ['787-8', 'A3307-00', 'DMC-B787']:
            validation_log["invalid_removed"] += 1
            continue
        
        # Duplicate detection
        if part_number in seen_parts:
            validation_log["duplicates_removed"] += 1
            continue
        
        seen_parts.add(part_number)
        
        # Add validation metadata
        part["validated"] = True
        part["validation_timestamp"] = datetime.utcnow().isoformat()
        validated.append(part)
        validation_log["validated_parts"].append(part_number)
    
    print(f"  ✅ Validation: {len(validated)} unique parts")
    print(f"  🗑️  Duplicates removed: {validation_log['duplicates_removed']}")
    print(f"  ❌ Invalid removed: {validation_log['invalid_removed']}")
    
    return {
        "parts": validated,
        "total_validated": len(validated),
        "validation_log": validation_log
    }


# ==========================================================
# FALLBACK EXTRACTION
# ==========================================================
def fallback_extraction(text: str, page_num: int) -> List[Dict]:
    """
    Fallback extraction jika layout tidak terdeteksi
    """
    extracted = []
    
    for pattern in VALID_PART_PATTERNS:
        matches = re.findall(pattern, text)
        for part_num in set(matches):
            if part_num not in ['787-8', 'A3307-00']:
                extracted.append({
                    "page_number": page_num,
                    "part_number": part_num,
                    "nomenclature": part_num,
                    "change_type": None,
                    "effectivity_values": [],
                    "type": "fallback"
                })
    
    return extracted


# ==========================================================
# MAIN EXTRACTOR - PIPELINE LENGKAP
# ==========================================================
def extract_all(pages: Dict[int, str]) -> Dict[str, Any]:
    """
    Universal extractor dengan pipeline lengkap:
    1. Text layer detection
    2. Layout detection
    3. Structured extraction
    4. Validation layer
    """
    all_extracted = []
    
    print(f"\n{'='*60}")
    print("🔍 STARTING EXTRACTION PIPELINE")
    print(f"{'='*60}\n")
    
    # STEP 1: Text layer detection
    text_analysis = detect_text_layer(pages)
    
    # STEP 2 & 3: Process each page
    for page_num, page_text in pages.items():
        # Skip pages with no text
        if text_analysis[page_num]["needs_ocr"]:
            print(f"⚠️ Page {page_num}: Needs OCR (will be handled by pdf_parser)")
            continue
        
        print(f"\n📄 Processing page {page_num}...")
        
        # STEP 2: Layout detection
        layout = detect_layout(page_text, page_num)
        
        # STEP 3: Structured extraction based on layout
        page_parts = []
        
        if layout["type"] == "tabular" and layout["tables"]:
            # Extract from tables
            total_table_parts = 0
            for table in layout["tables"]:
                table_parts = extract_from_table(table, page_num)
                page_parts.extend(table_parts)
                total_table_parts += len(table_parts)
            print(f"   📊 Table extraction: {total_table_parts} parts found")
        
        elif layout["type"] == "drawing":
            # Extract from drawing
            drawing_parts = extract_from_drawing(page_text, page_num)
            page_parts.extend(drawing_parts)
            print(f"   🎨 Drawing extraction: {len(drawing_parts)} items found")
        
        else:
            # Fallback: simple line-by-line
            page_parts = fallback_extraction(page_text, page_num)
            print(f"   📝 Fallback extraction: {len(page_parts)} parts found")
        
        all_extracted.extend(page_parts)
    
    print(f"\n{'='*60}")
    print(f"📊 RAW EXTRACTION: {len(all_extracted)} items found")
    
    # STEP 4: Validation layer
    validated = validate_extraction(all_extracted)
    
    print(f"{'='*60}")
    print(f"✅ FINAL VALIDATED: {validated['total_validated']} unique parts")
    print(f"{'='*60}\n")
    
    return {
        "parts": validated["parts"],
        "total_parts": validated["total_validated"],
        "validation_log": validated["validation_log"],
        "total_pages": len(pages)
    }