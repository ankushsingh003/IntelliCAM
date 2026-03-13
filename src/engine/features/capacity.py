"""
src/engine/features/capacity.py

Feature engineering for "Capacity" (Ability to Repay / Cash Flow).
Inputs: DSCR, EBITDA, Revenue Growth, GST vs Bank reconciliation.
Output: Capacity Score (0-100) and feature vector.
"""
from typing import Dict, Any
from src.research.risk_profile import ReconciledRiskProfile

class CapacityEngineer:
    
    @staticmethod
    def extract_features(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Calculates features related to repayment capacity."""
        
        score = 50.0 # Base

        financials = profile.internal_data.financials
        
        if not financials:
            return {"capacity_score": 0.0, "dscre_estimate": 0.0, "ebitda_margin": 0.0}
            
        latest = financials[-1]
        
        estimated_debt_service = latest.total_debt_crs * 0.15
        dscr = latest.ebitda_crs / estimated_debt_service if estimated_debt_service > 0 else 3.0
        
        if dscr > 1.5:
            score += 30
        elif dscr > 1.0:
            score += 15
        else:
            score -= 30  # Danger! Cannot service existing debt
            
        ebitda_margin = (latest.ebitda_crs / latest.revenue_crs * 100) if latest.revenue_crs else 0.0
        if ebitda_margin > 15.0:
            score += 20
            
        revenue_mismatch = any(f.reason for f in profile.reconciliation_flags if "revenue" in f.reason.lower())
        if revenue_mismatch:
            score -= 25

        final_score = max(0.0, min(100.0, score))

        return {
            "capacity_score": final_score,
            "dscr_estimate": float(dscr),
            "ebitda_margin_pct": float(ebitda_margin),
            "revenue_mismatch_flag": 1.0 if revenue_mismatch else 0.0
        }
