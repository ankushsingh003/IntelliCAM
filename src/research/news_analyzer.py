"""
src/research/news_analyzer.py

Analyzes news articles for positive/negative sentiment using transformers (FinBERT proxy).
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Analyzes financial news sentiment."""

    def __init__(self):
        logger.info("Initializing FinBERT News Analyzer (Mock Mode)")

    def analyze_headlines(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Analyzes a list of news headlines and computes a composite sentiment score.
        Score ranges from -1.0 (very negative) to 1.0 (very positive).
        """
        if not headlines:
            return {"composite_score": 0.0, "label": "Neutral", "risk_flag": False}
            
        score_sum: float = 0.0
        negative_count: int = 0
        
        for h in headlines:
            h_lower = h.lower()
            if "fraud" in h_lower or "default" in h_lower or "plunge" in h_lower or "investigation" in h_lower:
                score_sum -= 0.8
                negative_count = negative_count + 1 
            elif "profit" in h_lower or "growth" in h_lower or "surge" in h_lower or "award" in h_lower:
                score_sum += 0.6
            else:
                score_sum += 0.0
                
        avg_score = score_sum / len(headlines)
        
        label = "Neutral"
        if avg_score > 0.3:
            label = "Positive"
        elif avg_score < -0.3:
            label = "Negative"
            
        return {
            "composite_score": avg_score,
            "label": label,
            "headlines_analyzed": len(headlines),
            "negative_headlines": negative_count,
            "risk_flag": negative_count > 0  # Flag if any negative financial news exists
        }
