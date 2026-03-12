"""
src/ingestor/structured/gst_parser.py

Parses GST returns (GSTR-1, 2A, 2B, 3B) and handles basic reconciliation.
"""
import pandas as pd
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class GSTParser:
    """Parses and reconciles GST data."""

    @staticmethod
    def parse_gstr3b(text_or_tables: Any) -> Dict[str, Any]:
        """
        Mock parser for GSTR-3B.
        In a real scenario, this would extract specific fields like 
        Outward Supplies, Eligible ITC, etc. from OCR text or pdf tables.
        """
        logger.info("Parsing GSTR-3B...")
        return {
            "document_type": "GSTR-3B",
            "total_outward_taxable_value": 15000000.0,
            "total_itc_eligible": 1200000.0,
            "tax_paid_cash": 300000.0
        }

    @staticmethod
    def reconcile_2b_vs_3b(gstr2b_data: Dict[str, Any], gstr3b_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconciles ITC available in GSTR-2B vs ITC claimed in GSTR-3B.
        Crucial for detecting exaggerated ITC claims (a fraud indicator).
        """
        itc_2b = gstr2b_data.get("total_itc_available", 0.0)
        itc_3b = gstr3b_data.get("total_itc_eligible", 0.0)

        variance = itc_3b - itc_2b
        variance_pct = (variance / itc_2b) * 100 if itc_2b else 0.0

        is_flagged = variance_pct > 5.0 # Flag if 3B claiming > 5% more than 2B

        return {
            "itc_2b": itc_2b,
            "itc_3b": itc_3b,
            "variance": variance,
            "variance_pct": variance_pct,
            "flag_excess_itc": is_flagged
        }
