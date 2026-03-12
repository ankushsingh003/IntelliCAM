"""
src/research/risk_profile.py

Models the final, unified Risk Profile output of Phase 1 + Phase 2.
This is the required input for Phase 3 (Recommendation Engine).
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.ingestor.storage.schema import UnifiedRiskProfile as IngestorProfile

class OSINTData(BaseModel):
    news_sentiment_score: float
    regulatory_flags: int
    shell_company_risk: bool
    industry_outlook: str

class FlagSchema(BaseModel):
    severity: str
    reason: str

class ReconciledRiskProfile(BaseModel):
    """The master profile sent to the Scoring Engine."""
    cin: str
    internal_data: IngestorProfile
    external_osint: OSINTData
    primary_insights: Dict[str, Any]
    reconciliation_flags: List[FlagSchema]
    
    @property
    def is_auto_reject(self) -> bool:
        """Immediate rejection criteria based on fatal flags."""
        for flag in self.reconciliation_flags:
            if flag.severity == "CRITICAL":
                return True
        return False
