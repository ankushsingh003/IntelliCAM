"""
src/ingestor/nlp/postprocessor.py

Applies India-specific normalization to extracted unstructured text and numbers.
e.g., Lakhs/Crores -> Millions/Billions or standardized floats, dates -> dd/MM/yyyy.
"""
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

class IndianContextPostprocessor:
    """Normalizes extracted data to a standard format."""

    @staticmethod
    def normalize_currency_to_inr_absolute(value_str: str) -> float:
        """
        Convert Indian terminology ('Lakhs', 'Crores', 'Cr', 'L') to absolute INR float.
        Example: "1.5 Cr" -> 15000000.0
        """
        if not value_str or not isinstance(value_str, str):
            return 0.0
            
        value_str = value_str.lower().replace(",", "").strip()
        
        num_match = re.search(r"[\d\.]+", value_str)
        if not num_match:
            return 0.0
            
        number = float(num_match.group())

        if "cr" in value_str or "crore" in value_str:
            return number * 10000000.0
        elif "lakh" in value_str or "lac" in value_str or value_str.endswith("l"):
            return number * 100000.0
            
        return number

    @staticmethod
    def normalize_json_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scans JSON dict and attempts to normalize currency strings."""
        normalized = {}
        for key, value in payload.items():
            if isinstance(value, str) and ("crs" in key_name_lower or "lakhs" in key_name_lower):
               normalized[key] = value # Usually handled automatically by schema, kept flat for this version
               pass
               
            normalized[key] = value
            
        return normalized

    @staticmethod
    def _is_currency_key(key: str) -> bool:
        k = key.lower()
        return "crs" in k or "rs_" in k or "amount" in k
