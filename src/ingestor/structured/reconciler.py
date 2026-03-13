"""
src/ingestor/structured/reconciler.py

Cross-source anomaly detection (GST vs Bank vs ITR).
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CrossSourceReconciler:
    """Reconciles data across different financial documents to flag anomalies."""

    @staticmethod
    def reconcile_gst_vs_bank(gst_revenue: float, bank_inward: float) -> Dict[str, Any]:
        """
        Flags if Bank Inward is significantly lower than GST declared revenue.
        (Could indicate cash hoarding or fake billing).
        """
        variance = gst_revenue - bank_inward
        variance_pct = (variance / gst_revenue) * 100 if gst_revenue else 0.0

        is_flagged = variance_pct > 20.0

        return {
            "gst_revenue": gst_revenue,
            "bank_inward": bank_inward,
            "variance": variance,
            "variance_pct": variance_pct,
            "flag_revenue_mismatch": is_flagged
        }

    @staticmethod
    def reconcile_gst_vs_itr(gst_revenue: float, itr_gross_income: float) -> Dict[str, Any]:
        """
        Checks for material discrepancies between Income Tax filings and GST.
        """
        variance = abs(gst_revenue - itr_gross_income)
        variance_pct = (variance / max(gst_revenue, itr_gross_income)) * 100 if max(gst_revenue, itr_gross_income) else 0.0
        
        is_flagged = variance_pct > 10.0

        return {
            "gst_revenue": gst_revenue,
            "itr_gross_income": itr_gross_income,
            "variance": variance,
            "variance_pct": variance_pct,
            "flag_itr_gst_mismatch": is_flagged
        }

    @staticmethod
    def generate_consolidated_report(gst_data: Dict, bank_data: Dict, itr_data: Dict) -> Dict[str, Any]:
        """Runs all reconciliation checks and returns a summary."""
        logger.info("Running Cross-Source Reconciliation...")
        
        gst_rev = gst_data.get("total_outward_taxable_value", 0.0)
        bank_in = bank_data.get("total_inward", 0.0)
        itr_gross = itr_data.get("gross_total_income", 0.0)

        if not gst_rev or not bank_in or not itr_gross:
            return {"status": "incomplete_data"}

        return {
            "status": "success",
            "gst_vs_bank": CrossSourceReconciler.reconcile_gst_vs_bank(gst_rev, bank_in),
            "gst_vs_itr": CrossSourceReconciler.reconcile_gst_vs_itr(gst_rev, itr_gross)
        }
