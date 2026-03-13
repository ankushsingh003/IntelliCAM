"""
src/portal/backend/main.py

FastAPI entry point for the IntelliCAM portal.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.portal.backend.routes import insights

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliCAM Portal API",
    description="Backend API for the Credit Officer Primary Insights Portal.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "intellicam-portal"}
