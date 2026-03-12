"""
src/ingestor/storage/databricks_writer.py

Mocks writing normalized data to Databricks Delta Tables.
(Uses local JSON/SQLite fallback for local testing without Databricks connection).
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any

from configs.settings import settings
from src.ingestor.storage.schema import UnifiedRiskProfile

logger = logging.getLogger(__name__)

class DatabricksWriter:
    """Handles writing structured risk profiles to the data lake."""

    def __init__(self):
        self.output_dir = settings.data_dir / "processed"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.host = settings.databricks_host

    def write_profile(self, profile: UnifiedRiskProfile) -> bool:
        """
        Writes the Pydantic profile model to storage.
        """
        cin = profile.identity.cin or "UNKNOWN_CIN"
        file_path = self.output_dir / f"profile_{cin}.json"
        
        try:
            # For the local hackathon env, we save as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(profile.model_dump_json(indent=2))
            
            logger.info(f"Successfully wrote risk profile for {cin} to {file_path}")
            
            # Here we would use databricks-sql-connector to UPSERT into Delta tables:
            # e.g., "MERGE INTO credit_lake.financials target USING new_data source ..."
            if self.host:
                logger.debug(f"Mock sync to Databricks {self.host} completed.")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to write profile for {cin}: {e}")
            return False
