from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection  # Absolute
from app.api import health, ipd, drawing, filter
from config import settings  # Absolute


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Inisialisasi FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(ipd.router, prefix="/api/ipd", tags=["IPD"])
# app.include_router(drawing.router, prefix="/api/drawing", tags=["Drawing"])
app.include_router(filter.router, prefix="/api/filter", tags=["Filter"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0",
        "status": "running",
        "database": settings.MONGO_DB
    }