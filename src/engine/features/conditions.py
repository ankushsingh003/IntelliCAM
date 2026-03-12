"""
src/engine/features/conditions.py

Feature engineering for "Conditions" (Macro context + Primary Insights).
Inputs: Sector outlook, Credit Officer field notes.
Output: Conditions Score (0-100) and feature vector.
"""
from typing import Dict, Any
from src.research.risk_profile import ReconciledRiskProfile

class ConditionsEngineer:
    
    @staticmethod
    def extract_features(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Calculates macro and circumstantial risk features."""
        
        score = 50.0  # Base neutral
        
        # Sector Outlook
        outlook = profile.external_osint.industry_outlook.lower()
        if "positive" in outlook:
            score += 20
        elif "negative" in outlook:
            score -= 20
            
        # Primary OSINT - Management Quality from portal
        mgmt_quality = profile.primary_insights.get("management_quality", "Average")
        if mgmt_quality == "Good":
            score += 20
        elif mgmt_quality == "Poor":
            score -= 30
            
        # Field note: factory utilized
        utilization = profile.primary_insights.get("factory_utilization_pct", 70.0)
        if utilization < 40.0:
             score -= 20
        elif utilization > 80.0:
             score += 10
             
        final_score = max(0.0, min(100.0, score))

        return {
            "conditions_score": final_score,
            "sector_positive_flag": 1.0 if "positive" in outlook else 0.0,
            "poor_mgmt_flag": 1.0 if mgmt_quality == "Poor" else 0.0,
            "factory_utilization": float(utilization)
        }
