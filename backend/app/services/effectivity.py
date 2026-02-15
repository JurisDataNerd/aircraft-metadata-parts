from typing import List, Dict, Any

def check_effectivity(
    effectivity_type: str,
    effectivity_values: List[int],
    effectivity_range: Dict[str, int],
    line_number: int
) -> bool:
    """
    FR-03: Deterministic filtering based on effectivity
    Returns True if part applies to line_number
    """
    if not line_number:
        return False
    
    if effectivity_type == 'LIST':
        return line_number in (effectivity_values or [])
    
    elif effectivity_type == 'RANGE':
        if not effectivity_range:
            return False
        from_val = effectivity_range.get('from', 0)
        to_val = effectivity_range.get('to', 0)
        return from_val <= line_number <= to_val
    
    return False

def get_applicable_lines(part: Dict[str, Any]) -> List[int]:
    """
    Get all line numbers where part is applicable
    For LIST type: return the list
    For RANGE type: generate list (for display only)
    """
    eff_type = part.get('effectivity_type')
    
    if eff_type == 'LIST':
        return part.get('effectivity_values', [])
    elif eff_type == 'RANGE':
        eff_range = part.get('effectivity_range', {})
        from_val = eff_range.get('from', 0)
        to_val = eff_range.get('to', 0)
        # For display, generate sample
        if to_val - from_val > 100:
            return list(range(from_val, from_val + 5)) + ['...'] + list(range(to_val - 4, to_val + 1))
        else:
            return list(range(from_val, to_val + 1))
    return []