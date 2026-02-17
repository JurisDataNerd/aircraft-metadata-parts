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