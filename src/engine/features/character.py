"""
src/engine/features/character.py

Feature engineering for "Character" (Willingness to Repay).
Inputs: Legal risks, regulatory checks, news sentiment, past bounce history.
Output: Character Score (0-100) and feature vector.
"""
from typing import Dict, Any
from src.research.risk_profile import ReconciledRiskProfile

class CharacterEngineer:
    
    @staticmethod
    def extract_features(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Calculates features related to corporate character."""
        
        score = 80.0
        
        bounce_count = sum(bf.bounce_count for bf in profile.internal_data.bank_flows)
        score -= min(30, bounce_count * 5)
        
        if profile.external_osint.regulatory_flags > 0:
            score -= 20
            
        if profile.external_osint.shell_company_risk:
            score -= 40
            
        sentiment = profile.external_osint.news_sentiment_score
        score += (sentiment * 10)  # ranges from -10 to +10

        final_score = max(0.0, min(100.0, score))

        return {
            "character_score": final_score,
            "bounce_count": float(bounce_count),
            "regulatory_flags": float(profile.external_osint.regulatory_flags),
            "shell_risk_flag": 1.0 if profile.external_osint.shell_company_risk else 0.0
        }
