# backend/run.py
#!/usr/bin/env python
"""
Simple script to run the FastAPI server
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Aircraft Configuration Platform - Phase 1")
    print("=" * 60)
    print("📁 Upload directory: backend/uploads")
    print("🔗 MongoDB: Atlas")
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )