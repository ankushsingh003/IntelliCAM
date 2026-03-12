"""
src/research/reconciler.py

Reconciles signals from Phase 1 (Ingestor) with Phase 2 (Research).
Example: If Ingestor shows high revenue, but News shows "Factory Shut Down", 
this module flags a severe contradiction.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResearchReconciler:
    """Finds contradictions between internal data and external internet research."""

    @staticmethod
    def reconcile(ingestor_profile: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compares internal profile vs external OSINT."""
        logger.info("Reconciling internal ingestor data with external research...")
        
        flags = []
        
        # 1. Management Quality Mismatch
        primary_quality = research_data.get("primary_insights", {}).get("management_quality", "Average")
        if primary_quality == "Poor":
            flags.append({
                "severity": "HIGH",
                "reason": "Credit Officer reported POOR management quality on-site."
            })
            
        # 2. Revenue vs Sentiment Mismatch
        financials = ingestor_profile.get("financials", [])
        if financials:
            latest = financials[-1]
            rev = latest.get("revenue_crs", 0)
            sentiment = research_data.get("news_sentiment", {}).get("label")
            
            if rev > 100.0 and sentiment == "Negative":
                flags.append({
                    "severity": "MEDIUM",
                    "reason": f"High reported revenue ({rev} Cr) contrasts with Negative media sentiment."
                })
                
        # 3. Regulatory / Legal Checks
        legal = research_data.get("regulatory_status", {})
        if legal.get("has_active_sebi_bans") or legal.get("nclt_petitions_found"):
            flags.append({
                "severity": "CRITICAL",
                "reason": "Active severe regulatory bans or NCLT bankruptcy petitions found."
            })

        return {
            "reconciliation_status": "Completed",
            "total_flags": len(flags),
            "flags": flags
        }
