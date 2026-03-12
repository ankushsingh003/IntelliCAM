"""
src/engine/features/collateral.py

Feature engineering for "Collateral" (Security offered).
Inputs: MCA Charge Register for existing pledged assets vs net worth.
Output: Collateral Score (0-100) and feature vector.
"""
from typing import Dict, Any
from src.research.risk_profile import ReconciledRiskProfile

class CollateralEngineer:
    
    @staticmethod
    def extract_features(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Calculates available collateral buffer."""
        
        score = 60.0
        
        # In a real app, we parse exact assets from MCA Charge Register
        # Here we mock a generic calculation: how much net worth is unencumbered?
        
        financials = profile.internal_data.financials
        if not financials:
             return {"collateral_score": 0.0, "unencumbered_ratio": 0.0}
             
        latest = financials[-1]
        
        # Assume existing debt is fully backed by collateral
        unencumbered_assets = latest.net_worth_crs * 1.5 - latest.total_debt_crs
        unencumbered_ratio = unencumbered_assets / latest.net_worth_crs if latest.net_worth_crs else 0.0
        
        if unencumbered_ratio > 1.0:
            score += 30
        elif unencumbered_ratio < 0.2:
            score -= 30
            
        final_score = max(0.0, min(100.0, score))

        return {
            "collateral_score": final_score,
            "unencumbered_asset_ratio": float(unencumbered_ratio)
        }
