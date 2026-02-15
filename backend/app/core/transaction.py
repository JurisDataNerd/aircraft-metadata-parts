from motor.motor_asyncio import AsyncIOMotorClientSession
from contextlib import asynccontextmanager
import logging
from ..core.database import mongodb

logger = logging.getLogger(__name__)

class TransactionManager:
    """MongoDB transaction manager with automatic retry"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for atomic transactions"""
        # Buat session baru setiap kali
        session = await mongodb.client.start_session()
        retry_count = 0
        
        try:
            while retry_count < self.max_retries:
                try:
                    session.start_transaction()
                    logger.debug(f"✅ Transaction started (attempt {retry_count + 1})")
                    yield session
                    await session.commit_transaction()
                    logger.debug("✅ Transaction committed")
                    return
                    
                except Exception as e:
                    await session.abort_transaction()
                    retry_count += 1
                    
                    if "TransactionTooLarge" in str(e):
                        logger.error(f"❌ Transaction too large: {e}")
                        raise
                    
                    if retry_count == self.max_retries:
                        logger.error(f"❌ Transaction failed after {self.max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"⚠️ Transaction failed, retry {retry_count}/{self.max_retries}")
                    
        finally:
            await session.end_session()
            logger.debug("✅ Session ended")
    
    async def execute_in_transaction(self, operations):
        """Execute multiple operations atomically"""
        async with self.transaction() as session:
            results = []
            for op in operations:
                result = await op(session)
                results.append(result)
            return results

# Singleton
transaction_manager = TransactionManager()