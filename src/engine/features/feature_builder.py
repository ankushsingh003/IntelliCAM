"""
src/engine/features/feature_builder.py

Master feature assembler. Plugs the ReconciledRiskProfile through all 
Five Cs engineers and outputs a flat, continuous feature vector 
ready for XGBoost/Scikit-Learn inference.
"""
import logging
from typing import Dict, Any, List

from src.research.risk_profile import ReconciledRiskProfile
from src.engine.features.character import CharacterEngineer
from src.engine.features.capacity import CapacityEngineer
from src.engine.features.capital import CapitalEngineer
from src.engine.features.collateral import CollateralEngineer
from src.engine.features.conditions import ConditionsEngineer

logger = logging.getLogger(__name__)

class FeatureVectorBuilder:
    """Combines all Five C features into a single matrix row."""

    @staticmethod
    def build_vector(profile: ReconciledRiskProfile) -> Dict[str, float]:
        """Runs all engineers and flattens the result."""
        logger.info(f"Building Five Cs feature vector for CIN: {profile.cin}")
        
        vector = {}
        
        vector.update(CharacterEngineer.extract_features(profile))
        vector.update(CapacityEngineer.extract_features(profile))
        vector.update(CapitalEngineer.extract_features(profile))
        vector.update(CollateralEngineer.extract_features(profile))
        vector.update(ConditionsEngineer.extract_features(profile))
        
        vector["data_completeness_penalty"] = 100.0 - profile.internal_data.data_completeness_score
        vector["total_reconciliation_flags"] = float(len(profile.reconciliation_flags))
        
        vector["is_auto_reject"] = 1.0 if profile.is_auto_reject else 0.0

        return vector
