"""FastAPI application entry point for CET Tracker API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import (
    sessions,
    listening,
    reading,
    vocabulary,
    stats,
    import_export,
    review_tasks,
    reports,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="CET Tracker API",
    description="Local-first CET-4 / CET-6 exam preparation tracking API",
    version="0.3.4",
    lifespan=lifespan,
)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(sessions.router)
app.include_router(listening.router)
app.include_router(reading.router)
app.include_router(vocabulary.router)
app.include_router(stats.router)
app.include_router(import_export.router)
app.include_router(review_tasks.router)
app.include_router(reports.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
