import asyncio
import logging
from .database import mongodb
from .persistent_authority import persistent_authority

logger = logging.getLogger(__name__)

async def initialize_authority_system():
    """Initialize authority system on startup"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Wait for DB connection
            if mongodb.db is None:
                logger.info(f"⏳ Waiting for DB connection (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(retry_delay)
                continue
            
            # Initialize authority engine
            await persistent_authority.initialize()
            
            # Validate critical documents
            doc_count = await mongodb.db.document.count_documents({})
            rev_count = await mongodb.db.revisions.count_documents({})
            
            logger.info(f"📊 System state: {doc_count} documents, {rev_count} revisions")
            
            # Check consistency for recent documents
            recent_docs = await mongodb.db.document.find().sort("uploaded_at", -1).limit(5).to_list(5)
            for doc in recent_docs:
                issues = await persistent_authority.validate_consistency(doc["document_id"])
                if issues:
                    logger.warning(f"⚠️ Document {doc['document_id']} has consistency issues: {issues}")
            
            logger.info("✅ Authority system initialized successfully")
            return
            
        except Exception as e:
            logger.error(f"❌ Initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.critical("❌ Failed to initialize authority system after all retries")
                raise