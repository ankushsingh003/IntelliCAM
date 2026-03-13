"""
src/research/sector_profiler.py

Provides macroeconomic and sector-specific benchmarking based on NIC/SIC codes.
Used to give the Recommendation Engine context on industry tailwinds/headwinds.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SectorProfiler:
    """Provides risk and benchmarking context for specific sectors."""

    _SECTOR_DB = {
        "textiles": {
            "outlook": "Negative",
            "avg_ebitda_margin": 12.0,
            "avg_dscr": 1.2,
            "headwinds": ["High cotton prices", "Reduced export demand Europe"],
            "tailwinds": ["PLI scheme benefits"]
        },
        "pharmaceuticals": {
            "outlook": "Positive",
            "avg_ebitda_margin": 22.0,
            "avg_dscr": 2.5,
            "headwinds": ["USFDA pricing pressure"],
            "tailwinds": ["Strong domestic formulation demand", "API PLI"]
        },
        "real_estate": {
            "outlook": "Neutral",
            "avg_ebitda_margin": 18.0,
            "avg_dscr": 1.4,
            "headwinds": ["High interest rates"],
            "tailwinds": ["Premium housing demand surge"]
        }
    }

    @staticmethod
    def get_sector_profile(sector_name: str) -> Dict[str, Any]:
        """Returns macro-economic benchmarks for the given sector."""
        logger.info(f"Fetching sector profile for: {sector_name}")
        
        sector_key = sector_name.lower().replace(" ", "_").strip()
        
        if sector_key in SectorProfiler._SECTOR_DB:
            return SectorProfiler._SECTOR_DB[sector_key]
            
        return {
            "outlook": "Unknown",
            "avg_ebitda_margin": 15.0,  # Generic default
            "avg_dscr": 1.5,
            "headwinds": [],
            "tailwinds": []
        }

    @staticmethod
    def compare_vs_benchmark(company_ebitda: float, company_dscr: float, sector: str) -> Dict[str, Any]:
        """Compares a company's ratios against industry averages."""
        benchmark = SectorProfiler.get_sector_profile(sector)
        
        return {
            "ebitda_vs_industry": company_ebitda - benchmark["avg_ebitda_margin"],
            "dscr_vs_industry": company_dscr - benchmark["avg_dscr"],
            "industry_outlook": benchmark["outlook"]
        }
