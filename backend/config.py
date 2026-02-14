import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

class Settings:
    MONGO_URI: str = os.getenv('MONGO_URI', '')
    MONGO_DB: str = os.getenv('MONGO_DB', 'aircraft_config')
    
    APP_NAME: str = "Aircraft Configuration Intelligence"
    DEBUG: bool = os.getenv('FLASK_ENV', 'development') == 'development'
    
    def __init__(self):
        if not self.MONGO_URI:
            raise ValueError("MONGO_URI tidak boleh kosong. Cek file .env di root")
        if not self.MONGO_DB:
            raise ValueError("MONGO_DB tidak boleh kosong. Cek file .env di root")

settings = Settings()