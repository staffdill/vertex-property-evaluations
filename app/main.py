"""FastAPI application with lifespan, health check, and static file serving."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import properties


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(title="Wise Evaluations", lifespan=lifespan)


@app.get("/api/health")
async def health_check():
    """Return application health status."""
    return {"status": "ok", "version": settings.app_version}


app.include_router(properties.router)

# Mount static files LAST so API routes take priority
app.mount("/", StaticFiles(directory="static", html=True), name="static")
