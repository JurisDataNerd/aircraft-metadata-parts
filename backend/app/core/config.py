# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Aircraft Config Phase 1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # MongoDB Atlas
    MONGO_URI: str
    MONGO_DB: str = "AircraftConfig"
    
    # File Upload
    UPLOAD_DIR: str = str(Path(__file__).parent.parent.parent / "uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()