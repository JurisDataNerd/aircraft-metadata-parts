from typing import List, Dict, Any

def check_effectivity(
    effectivity_type: str,
    effectivity_values: List[int],
    effectivity_range: Dict[str, int],
    line_number: int
) -> bool:
    """
    FR-03: Deterministic filtering based on effectivity
    """
    if not line_number:
        return False
    
    if effectivity_type == 'LIST':
        return line_number in (effectivity_values or [])
    
    elif effectivity_type == 'RANGE':
        if not effectivity_range:
            return False
        return effectivity_range.get('from', 0) <= line_number <= effectivity_range.get('to', 0)
    
    return False