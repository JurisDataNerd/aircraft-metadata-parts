from .parser_engine import ParserEngine
import logging

logger = logging.getLogger(__name__)

class IPDPDFParser:
    """Wrapper untuk backward compatibility"""
    
    def __init__(self, file_path: str):
        self.engine = ParserEngine(file_path)
    
    async def parse(self) -> Dict:
        """Parse PDF menggunakan parser engine"""
        result = await self.engine.process()
        
        return {
            "success": result["success"],
            "total_pages": result.get("total_pages", 0),
            "metadata": result.get("metadata", {}),
            "parts": result.get("parts", []),
            "parts_found": result.get("total_validated", 0),
            "document_type": result.get("document_type", "UNKNOWN"),
            "error": result.get("error")
        }