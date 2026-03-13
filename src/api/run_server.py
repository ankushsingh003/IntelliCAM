"""
src/api/run_server.py

Bootstraps the master Uvicorn server for the IntelliCAM API.
"""
import uvicorn
import logging

from configs.settings import settings

logger = logging.getLogger(__name__)

def start():
    """Starts the Fast API main server."""
    logger.info("Initializing IntelliCAM Master API Server...")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload for dev
        log_level="info"
    )

if __name__ == "__main__":
    start()
