# backend/app/services/filter_service.py
from typing import List, Dict, Optional
import time

class FilterService:
    """
    Simple service for line-based filtering
    Phase 1: No caching yet, just direct database queries
    """
    
    async def filter_by_line(self, line_number: int, parts: List[Dict]) -> Dict:
        """
        Filter parts by line number based on effectivity
        """
        applicable = []
        non_applicable = []
        
        for part in parts:
            effectivity = part.get('effectivity', {})
            eff_type = effectivity.get('type')
            
            is_applicable = False
            
            if eff_type == 'LIST':
                if line_number in effectivity.get('values', []):
                    is_applicable = True
                    
            elif eff_type == 'RANGE':
                from_val = effectivity.get('from')
                to_val = effectivity.get('to')
                if from_val and to_val and from_val <= line_number <= to_val:
                    is_applicable = True
            
            # Build simplified part info
            part_info = {
                'part_number': part['part_number'],
                'nomenclature': part.get('nomenclature'),
                'figure': part.get('figure'),
                'item': part.get('item'),
                'page': part.get('page_number', part.get('page')),
                'confidence': part.get('confidence', 0.95)
            }
            
            if is_applicable:
                applicable.append(part_info)
            else:
                non_applicable.append(part_info)
        
        return {
            'line_number': line_number,
            'applicable_parts': applicable,
            'non_applicable_parts': non_applicable[:50],  # Limit non-applicable
            'total_applicable': len(applicable),
            'total_parts': len(parts)
        }