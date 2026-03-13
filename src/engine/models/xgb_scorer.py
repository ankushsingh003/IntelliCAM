"""
src/engine/models/xgb_scorer.py

XGBoost Inference Module. Loads a pre-trained XGBoost model to score
the Five Cs feature vector and outputs a Probability of Default (PD).
"""
import logging
import pandas as pd
import xgboost as xgb
from typing import Dict, Any

from configs.settings import settings

logger = logging.getLogger(__name__)

class XGBoostScorer:
    """Wrapper for the XGBoost ML model."""

    def __init__(self):
        self.model_path = settings.models_dir / "xgb_credit_model.json"
        self.model = self._load_model()
        
    def _load_model(self) -> xgb.Booster:
        """Loads the XGBoost booster. Mocks if not found."""
        try:
            if self.model_path.exists():
                booster = xgb.Booster()
                booster.load_model(str(self.model_path))
                logger.info(f"Loaded XGBoost model from {self.model_path}")
                return booster
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using mock heuristic scorer.")
                return None
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {e}")
            return None

    def predict_pd(self, feature_vector: Dict[str, float]) -> float:
        """
        Predicts the Probability of Default (PD).
        1.0 = High Default Risk, 0.0 = Low Default Risk.
        """
        if feature_vector.get("is_auto_reject", 0.0) == 1.0:
            logger.info("Hard auto-reject triggered before ML inference.")
            return 0.99  # 99% PD

        if self.model:
            df = pd.DataFrame([feature_vector])
            dmatrix = xgb.DMatrix(df)
            pd_pred = self.model.predict(dmatrix)[0]
            logger.debug(f"XGBoost inferred PD: {pd_pred:.4f}")
            return float(pd_pred)
            
        else:
            avg_c_score = (
                feature_vector.get("character_score", 50) +
                feature_vector.get("capacity_score", 50) +
                feature_vector.get("capital_score", 50) +
                feature_vector.get("collateral_score", 50) +
                feature_vector.get("conditions_score", 50)
            ) / 5.0
            
            pd_pred = 1.0 - (avg_c_score / 100.0)
            
            if feature_vector.get("bounce_count", 0) > 2:
                pd_pred += 0.2
            if feature_vector.get("shell_risk_flag", 0) == 1.0:
                pd_pred += 0.4
                
            pd_pred = max(0.01, min(0.99, pd_pred))
            logger.debug(f"Mock Heuristic inferred PD: {pd_pred:.4f}")
            return pd_pred

    def get_credit_rating(self, pd: float) -> str:
        """Maps continuous PD to an agency-style rating tier."""
        if pd < 0.05: return "AAA"
        if pd < 0.10: return "AA"
        if pd < 0.20: return "A"
        if pd < 0.35: return "BBB"
        if pd < 0.50: return "BB"
        if pd < 0.70: return "B"
        if pd < 0.85: return "CCC"
        return "D"
