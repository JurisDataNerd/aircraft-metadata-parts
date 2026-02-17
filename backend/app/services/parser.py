# backend/app/services/parser.py
import camelot
import pandas as pd
import re
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class IPDParser:
    """
    Simple parser for Boeing IPD documents using Camelot
    Phase 1: Focus on extracting part numbers and effectivity
    """
    
    def __init__(self):
        self.supported_change_types = ['ADD', 'MODIFY', 'DELETE', 'RF']
    
    async def parse(self, pdf_path: str) -> Dict:
        """
        Parse IPD PDF and extract parts
        """
        logger.info(f"📄 Parsing: {os.path.basename(pdf_path)}")
        
        all_parts = []
        report = {
            'tables_found': 0,
            'parts_extracted': 0,
            'pages_processed': 0
        }
        
        try:
            # Parse with Camelot (lattice for tables with lines)
            tables = camelot.read_pdf(
                pdf_path,
                pages='all',
                flavor='lattice',
                line_scale=40,
                strip_text='\n'
            )
            
            report['tables_found'] = len(tables)
            
            for table in tables:
                df = table.df
                
                # Basic cleaning
                df = df.replace(r'^\s*$', pd.NA, regex=True)
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                # Try to find header
                header_row = self._find_header_row(df)
                if header_row is not None:
                    df = self._apply_header(df, header_row)
                
                # Process rows
                for idx, row in df.iterrows():
                    part = self._extract_part(row, table.page)
                    if part:
                        all_parts.append(part)
                
                report['pages_processed'] += 1
            
            report['parts_extracted'] = len(all_parts)
            logger.info(f"✅ Extracted {len(all_parts)} parts")
            
        except Exception as e:
            logger.error(f"❌ Error parsing PDF: {e}")
            report['error'] = str(e)
        
        return {
            'parts': all_parts,
            'report': report
        }
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """Find which row contains column headers"""
        header_keywords = ['FIG', 'ITEM', 'PART', 'NOMENCLATURE', 'EFFECT']
        
        for idx, row in df.iterrows():
            row_text = ' '.join(str(v) for v in row.values).upper()
            matches = sum(1 for kw in header_keywords if kw in row_text)
            if matches >= 2:  # At least 2 keywords
                return idx
        return None
    
    def _apply_header(self, df: pd.DataFrame, header_row: int) -> pd.DataFrame:
        """Apply header row as column names"""
        new_df = df.copy()
        new_df.columns = new_df.iloc[header_row]
        new_df = new_df.drop(header_row).reset_index(drop=True)
        return new_df
    
    def _extract_part(self, row: pd.Series, page: int) -> Optional[Dict]:
        """Extract part information from a row"""
        try:
            # Convert to dict
            row_dict = {}
            for col, val in row.items():
                if pd.notna(val):
                    row_dict[str(col).upper().strip()] = str(val).strip()
            
            # Find part number
            part_number = self._find_part_number(row_dict)
            if not part_number:
                return None
            
            # Parse effectivity
            effectivity = self._parse_effectivity(row_dict)
            if not effectivity or effectivity.get('type') is None:
                # Skip rows without effectivity
                return None
            
            # Get other fields
            nomenclature = self._get_field(row_dict, ['NOMENCLATURE', 'DESC'])
            figure = self._get_field(row_dict, ['FIG', 'FIGURE'])
            item = self._get_field(row_dict, ['ITEM'])
            upa = self._parse_int(self._get_field(row_dict, ['UPA', 'QTY']))
            
            return {
                'part_number': part_number,
                'nomenclature': nomenclature,
                'figure': figure,
                'item': item,
                'effectivity': effectivity,
                'upa': upa,
                'page': page,
                'confidence': 0.95
            }
            
        except Exception as e:
            logger.debug(f"Error extracting part: {e}")
            return None
    
    def _find_part_number(self, row_dict: Dict) -> Optional[str]:
        """Find part number in row"""
        for key in row_dict:
            if 'PART' in key.upper() and 'NUMBER' in key.upper():
                return row_dict[key]
            # Also check for common part number patterns
            val = row_dict[key]
            if re.match(r'^[A-Z0-9]{5,15}[-]?\d{0,3}$', str(val)):
                return val
        return None
    
    def _parse_effectivity(self, row_dict: Dict) -> Optional[Dict]:
        """Parse effectivity from row"""
        # Find effectivity column
        eff_text = None
        for key in row_dict:
            if 'EFFECT' in key.upper():
                eff_text = row_dict[key]
                break
        
        if not eff_text:
            return None
        
        eff_text = str(eff_text).replace(',', ' ').replace('  ', ' ')
        
        # Check for range (e.g., "100-200")
        range_match = re.search(r'(\d+)\s*[-–]\s*(\d+)', eff_text)
        if range_match:
            return {
                'type': 'RANGE',
                'from': int(range_match.group(1)),
                'to': int(range_match.group(2))
            }
        
        # Extract all numbers for LIST
        numbers = re.findall(r'\d+', eff_text)
        if numbers:
            return {
                'type': 'LIST',
                'values': [int(n) for n in numbers]
            }
        
        return {'type': 'UNKNOWN'}
    
    def _get_field(self, row_dict: Dict, possible_names: List[str]) -> Optional[str]:
        """Get field by trying multiple column names"""
        for name in possible_names:
            for col in row_dict:
                if name.upper() in col.upper():
                    return row_dict[col]
        return None
    
    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Safely parse integer"""
        if value and str(value).strip().isdigit():
            return int(str(value).strip())
        return None
# backend/app/services/parser.py - Update drawing parser

    async def parse_drawing(self, pdf_path: str) -> Dict:
        """
        Parse drawing document with complex layout
        """
        logger.info(f"📐 Parsing drawing: {os.path.basename(pdf_path)}")
        
        all_items = []
        report = {
            'tables_found': 0,
            'items_extracted': 0,
            'pages_processed': 0
        }
        
        try:
            # Strategy 1: Stream with edge_tol for wide tables
            tables = camelot.read_pdf(
                pdf_path,
                pages='all',
                flavor='stream',
                edge_tol=1000,  # Lebih toleran untuk tabel lebar
                row_tol=20,     # Toleransi baris
                strip_text='\n'
            )
            
            report['tables_found'] = len(tables)
            logger.info(f"   Found {len(tables)} tables with stream")
            
            for table in tables:
                df = table.df
                logger.debug(f"   Table shape: {df.shape}")
                
                # Clean dataframe
                df = df.replace(r'^\s*$', pd.NA, regex=True)
                df = df.replace(r'\s+', ' ', regex=True)
                
                # Process each row
                for idx, row in df.iterrows():
                    items = self._extract_drawing_items_from_row(row, table.page)
                    all_items.extend(items)
                
                report['pages_processed'] += 1
            
            # Strategy 2: Jika masih kurang, coba lattice untuk tabel dengan garis
            if len(all_items) < 10:
                tables2 = camelot.read_pdf(
                    pdf_path,
                    pages='all',
                    flavor='lattice',
                    line_scale=40
                )
                logger.info(f"   Found {len(tables2)} tables with lattice")
                
                for table in tables2:
                    df = table.df
                    for idx, row in df.iterrows():
                        items = self._extract_drawing_items_from_row(row, table.page)
                        all_items.extend(items)
            
            report['items_extracted'] = len(all_items)
            logger.info(f"✅ Extracted {len(all_items)} items from drawing")
            
        except Exception as e:
            logger.error(f"❌ Error parsing drawing: {e}")
            import traceback
            traceback.print_exc()
            report['error'] = str(e)
        
        return {
            'items': all_items,
            'report': report
        }
    
    def _extract_drawing_items_from_row(self, row: pd.Series, page: int) -> List[Dict]:
        """Extract multiple items from a single row (for complex tables)"""
        items = []
        
        try:
            # Get all non-empty values
            values = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip()]
            
            if len(values) < 2:
                return items
            
            # Join all text for pattern matching
            full_text = ' '.join(values)
            
            # Pattern untuk part number A511351610-XXX
            part_pattern = r'(A\d{8,10}-\d{3})'
            matches = re.findall(part_pattern, full_text)
            
            if matches:
                for part_number in matches:
                    # Find context around this part number
                    context = self._find_context_for_part(part_number, values, full_text)
                    
                    item = {
                        'part_number': part_number,
                        'nomenclature': context.get('description'),
                        'quantity': context.get('quantity'),
                        'item_number': context.get('item_number'),
                        'page': page,
                        'confidence': 0.9,
                        'has_arabic': self._has_arabic_text(full_text)
                    }
                    
                    # Check if it's a placard/stencil
                    if any(kw in full_text.upper() for kw in ['PLACARD', 'STENCIL', 'DECAL']):
                        item['is_sticker'] = True
                        item['sticker_type'] = self._detect_sticker_type(full_text)
                        item['sticker_text'] = self._extract_sticker_text(full_text)
                    
                    items.append(item)
            
            # Also look for patterns like "ITEM-057" which might contain part numbers
            if not items:
                item_pattern = r'ITEM[-\s](\d{3})'
                item_matches = re.findall(item_pattern, full_text)
                
                for item_num in item_matches:
                    # Try to find part number near this item
                    for i, val in enumerate(values):
                        if f"ITEM-{item_num}" in val or f"ITEM {item_num}" in val:
                            # Check next few values for part number
                            for j in range(1, min(5, len(values)-i)):
                                if re.match(r'^[A-Z]\d+', values[i+j]):
                                    items.append({
                                        'part_number': values[i+j],
                                        'item_number': item_num,
                                        'page': page,
                                        'confidence': 0.7
                                    })
                                    break
                                
        except Exception as e:
            logger.debug(f"Error extracting from row: {e}")
        
        return items
    
    def _find_context_for_part(self, part_number: str, values: List[str], full_text: str) -> Dict:
        """Find context (description, quantity) for a part number"""
        context = {}
        
        try:
            # Find position of part number in values
            part_idx = -1
            for i, val in enumerate(values):
                if part_number in val:
                    part_idx = i
                    break
                
            if part_idx >= 0:
                # Check previous value for quantity
                if part_idx > 0 and values[part_idx-1].isdigit():
                    context['quantity'] = int(values[part_idx-1])
                
                # Check next few values for description
                for j in range(1, min(4, len(values)-part_idx)):
                    if any(kw in values[part_idx+j].upper() for kw in ['PLACARD', 'STENCIL', 'ECB', 'BOX']):
                        context['description'] = values[part_idx+j]
                        break
                    
            # If not found in values, try regex on full text
            if not context.get('description'):
                desc_match = re.search(rf'{part_number}\s+([A-Z\s]+)', full_text)
                if desc_match:
                    context['description'] = desc_match.group(1).strip()
            
        except Exception as e:
            logger.debug(f"Error finding context: {e}")
        
        return context
    
    def _has_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_range = range(0x0600, 0x06FF + 1)
        return any(ord(char) in arabic_range for char in text)
    
    def _detect_sticker_type(self, text: str) -> Optional[str]:
        """Detect sticker type from text"""
        text_upper = text.upper()
        if 'PLACARD' in text_upper:
            return 'PLACARD'
        elif 'STENCIL' in text_upper:
            return 'STENCIL'
        elif 'DECAL' in text_upper:
            return 'DECAL'
        elif 'MARKING' in text_upper:
            return 'MARKING'
        return None
    
    def _extract_sticker_text(self, text: str) -> Optional[str]:
        """Extract the actual text that goes on sticker"""
        # Look for quoted text or specific patterns
        quote_match = re.search(r'"([^"]+)"', text)
        if quote_match:
            return quote_match.group(1)
        
        # Look for common placard content patterns
        content_match = re.search(r'CONTENT:?\s*(.+?)(?:\s*(?:NOTE|SUPPLIER|MANUFACTURED|$))', text, re.IGNORECASE)
        if content_match:
            return content_match.group(1).strip()
        
        return None