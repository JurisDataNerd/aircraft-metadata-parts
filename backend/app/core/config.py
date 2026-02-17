# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Aircraft Config Phase 1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # MongoDB Atlas
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "aircraft_config"
    
    # File Upload
    UPLOAD_DIR: str = "backend/uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = "../../.env"  # Path ke .env di root
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()