"""
src/engine/features/capital.py

Feature engineering for "Capital" (Skin in the game / Net Worth).
Inputs: Net Worth, Debt/Equity ratio.
Output: Capital Score (0-100) and feature vector.
"""
from typing import Dict, Any
from src.research.risk_profile import ReconciledRiskProfile

class CapitalEngineer:
    
    @staticmethod
    def extract_features(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Calculates features related to company's financial leverage."""
        
        score = 50.0
        
        financials = profile.internal_data.financials
        if not financials:
            return {"capital_score": 0.0, "debt_to_equity": 0.0, "net_worth_crs": 0.0}
            
        latest = financials[-1]
        
        debt = latest.total_debt_crs
        equity = latest.net_worth_crs
        
        d_e_ratio = debt / equity if equity > 0 else 10.0 # High penalty if equity is negative/zero
        
        if d_e_ratio < 1.0:
            score += 40
        elif d_e_ratio < 2.5:
            score += 20
        elif d_e_ratio > 4.0:
            score -= 40 # Overleveraged
            
        # Size factor
        if equity > 50.0:
            score += 10
            
        final_score = max(0.0, min(100.0, score))

        return {
            "capital_score": final_score,
            "debt_to_equity_ratio": float(d_e_ratio),
            "net_worth_crs": float(equity)
        }
