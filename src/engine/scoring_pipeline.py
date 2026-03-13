"""
src/engine/scoring_pipeline.py

Master Orchestrator for Phase 3: Recommendation Engine.
Takes the ReconciledRiskProfile, engineers features, scores via XGBoost,
calculates SHAP values (in Step 3), and creates the final Credit Decision.
"""
import logging
from typing import Dict, Any

from src.research.risk_profile import ReconciledRiskProfile
from src.engine.features.feature_builder import FeatureVectorBuilder
from src.engine.models.xgb_scorer import XGBoostScorer
from src.engine.explainability.shap_explainer import SHAPExplainer

logger = logging.getLogger(__name__)

class CreditScoringPipeline:
    """End-to-end inference pipeline for the recommendation engine."""

    def __init__(self):
        self.feature_builder = FeatureVectorBuilder()
        self.scorer = XGBoostScorer()
        self.explainer = SHAPExplainer(self.scorer.model)

    def generate_decision(self, profile: ReconciledRiskProfile) -> Dict[str, Any]:
        """
        Executes the full engine loop and returns the final decision package.
        """
        cin = profile.cin
        logger.info(f"Starting Phase 3 Engine Pipeline for: {cin}")

        feature_vector = self.feature_builder.build_vector(profile)

        pd_score = self.scorer.predict_pd(feature_vector)
        
        rating = self.scorer.get_credit_rating(pd_score)

        recommendation = "REJECT"
        if profile.is_auto_reject:
            recommendation = "AUTO_REJECT"
        elif pd_score < 0.25:
            recommendation = "APPROVE"
        elif pd_score < 0.40:
            recommendation = "MANUAL_REVIEW_REQUIRED"

        shap_explanations = self.explainer.explain_prediction(feature_vector)

        decision_package = {
            "cin": cin,
            "company_name": profile.internal_data.identity.company_name,
            "ml_probability_of_default": round(pd_score, 4),
            "credit_rating_tier": rating,
            "engine_recommendation": recommendation,
            "feature_vector": feature_vector,
            "shap_explanations": shap_explanations,
            "reconciliation_flags": [f.model_dump() for f in profile.reconciliation_flags]
        }
        
        logger.info(f"Engine Decision for {cin}: {recommendation} (PD: {pd_score:.2f})")
        return decision_package
