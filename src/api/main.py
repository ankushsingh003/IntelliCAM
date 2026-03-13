"""
src/api/main.py

Master FastAPI application for IntelliCAM.
Exposes endpoints for the full end-to-end loan analysis.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as analyze_router
from src.portal.backend.routes.insights import router as portal_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliCAM Master API",
    description="End-to-End automated Corporate Appraisals.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api/v1/engine", tags=["Appraisal Engine"])
app.include_router(portal_router, prefix="/api/v1/portal/insights", tags=["Credit Officer Portal"])

@app.get("/health")
async def health_check():
    """System health check."""
    return {"status": "ok", "service": "intellicam-core"}
