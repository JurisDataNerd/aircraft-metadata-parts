import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari root project
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / '.env'
load_dotenv(ENV_PATH)

class Settings:
    # MongoDB
    MONGO_URI: str = os.getenv('MONGO_URI', '')
    MONGO_DB: str = os.getenv('MONGO_DB', 'aircraft_config')
    
    # FastAPI
    APP_NAME: str = "Aircraft Configuration Intelligence Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv('FLASK_ENV', 'development') == 'development'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-key-2026')
    
    # Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_PATH: Path = Path("uploads")
    
    def __init__(self):
        if not self.MONGO_URI:
            raise ValueError("❌ MONGO_URI tidak ditemukan di .env")
        if not self.MONGO_DB:
            raise ValueError("❌ MONGO_DB tidak ditemukan di .env")
        
        # Buat folder uploads
        self.UPLOAD_PATH.mkdir(exist_ok=True)
        (self.UPLOAD_PATH / "ipd").mkdir(exist_ok=True)
        (self.UPLOAD_PATH / "images").mkdir(exist_ok=True)

settings = Settings()