"""
src/engine/explainability/shap_explainer.py

Uses SHAP (SHapley Additive exPlanations) to explain the XGBoost model's predictions.
Provides both global feature importance and local instance-level explanations.
"""
import logging
import pandas as pd
import shap
import xgboost as xgb
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SHAPExplainer:
    """Computes SHAP values for Model Explainability."""

    def __init__(self, booster: xgb.Booster):
        self.booster = booster
        if self.booster:
            self.explainer = shap.TreeExplainer(self.booster)
        else:
            self.explainer = None
            logger.warning("SHAPExplainer initialized without a valid booster.")

    def explain_prediction(self, feature_vector: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculates SHAP values for a single prediction and returns the top 
        positive (increasing PD) and top negative (decreasing PD) drivers.
        """
        if not self.explainer:
            return {"top_risk_drivers": [], "top_mitigants": []}

        df = pd.DataFrame([feature_vector])
        
        shap_values = self.explainer.shap_values(df)
        
        instance_shap = shap_values[0]
        
        features = list(feature_vector.keys())
        
        contributions = []
        for i, feature_name in enumerate(features):
            contributions.append({
                "feature": feature_name,
                "value": float(feature_vector[feature_name]),
                "shap_value": float(instance_shap[i])
            })
            
        
        contributions.sort(key=lambda x: x["shap_value"], reverse=True)
        
        top_positive = [c for c in contributions if c["shap_value"] > 0][:3]
        top_negative = [c for c in contributions if c["shap_value"] < 0][-3:]
        
        return {
            "top_risk_drivers": top_positive,  # Things that make default more likely
            "top_mitigants": top_negative      # Things that make default less likely
        }
