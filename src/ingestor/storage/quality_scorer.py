"""
src/ingestor/storage/quality_scorer.py

Computes a Data Completeness Score (0-100) based on how much 
required data was successfully extracted vs missing.
"""
import logging
from src.ingestor.storage.schema import UnifiedRiskProfile

logger = logging.getLogger(__name__)

class DataQualityScorer:
    """Calculates completion and quality metrics for the extracted data."""

    @staticmethod
    def calculate_completeness(profile: UnifiedRiskProfile) -> float:
        """
        Scores the profile based on the presence of critical fields.
        """
        total_points = 100
        deductions = 0
        
        # Identity checks
        if not profile.identity.pan:
            deductions += 15
        if not profile.identity.cin and not profile.identity.gstin:
            deductions += 15
            
        # Financial checks
        if not profile.financials:
            deductions += 30  # Critical gap
        else:
            latest_fin = profile.financials[-1]
            if latest_fin.revenue_crs == 0:
                deductions += 10
            if latest_fin.net_worth_crs == 0:
                deductions += 10
                
        # Bank flow checks
        if not profile.bank_flows:
            deductions += 20
            
        final_score = max(0.0, float(total_points - deductions))
        logger.info(f"Data Completeness Score calculated: {final_score}/100")
        
        return final_score
