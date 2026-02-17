# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import Database
from app.api import documents, filter

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Aircraft Configuration Platform - Phase 1: Upload, Parse, Filter"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(filter.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "phase": "Phase 1 - Upload, Parse, Filter",
        "endpoints": {
            "upload": f"{settings.API_V1_PREFIX}/documents/upload",
            "filter": f"{settings.API_V1_PREFIX}/filter/line/{line_number}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if Database.client else "disconnected"
    }

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB Atlas on startup"""
    logger.info("🚀 Starting up...")
    await Database.connect_db(settings.MONGODB_URL)
    
    # Create upload directory
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    logger.info("✅ Startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down...")
    await Database.close_db()
    logger.info("👋 Shutdown complete")