from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.startup import initialize_authority_system
from app.api import health, ipd, drawing, filter, upload, document, revision
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await initialize_authority_system()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
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
app.include_router(drawing.router, prefix="/api/drawing", tags=["Drawing"])
app.include_router(filter.router, prefix="/api/filter", tags=["Filter"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(document.router, prefix="/api/document", tags=["Document"])
app.include_router(revision.router, prefix="/api/revision", tags=["Revision"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "database": settings.MONGO_DB,
        "authority_initialized": True
    }