"""
src/engine/decision_report.py

Builds the final, structured Credit Memo / Recommendation Report
that is returned to the Frontend Portal or downstream banking APIs.
"""
import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

from src.research.risk_profile import ReconciledRiskProfile
from src.engine.scoring_pipeline import CreditScoringPipeline
from src.engine.explainability.narrative_generator import NarrativeGenerator
from src.engine.explainability.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

class FeatureDump(BaseModel):
    character_score: float
    capacity_score: float
    capital_score: float
    collateral_score: float
    conditions_score: float

class CreditDecisionReport(BaseModel):
    """Final JSON object returned by IntelliCAM."""
    report_id: str
    generation_timestamp: str
    company_name: str
    cin: str
    
    # ML Outputs
    probability_of_default: float
    credit_rating_tier: str
    engine_recommendation: str  # APPROVE, REJECT, MANUAL_REVIEW_REQUIRED
    
    # 5 Cs Summarized
    five_cs_summary: FeatureDump
    
    # Explainability
    ai_credit_narrative: str
    top_risk_drivers: List[Dict[str, Any]]
    top_mitigants: List[Dict[str, Any]]
    
    # Validation & Alerts
    critical_reconciliation_flags: List[Dict[str, str]]
    
    # Chart
    shap_waterfall_base64: str

class ReportBuilder:
    """Orchestrates pulling everything into the final format."""
    
    def __init__(self):
        self.pipeline = CreditScoringPipeline()
        self.narrative_gen = NarrativeGenerator()
        
    def generate_report(self, profile: ReconciledRiskProfile) -> CreditDecisionReport:
        """Executes the pipeline and formats the final output."""
        logger.info(f"Generating Final Credit Decision Report for {profile.cin}")
        
        # 1. Run inference
        decision_pkg = self.pipeline.generate_decision(profile)
        
        # 2. Generate NL Narrative
        narrative = self.narrative_gen.generate_narrative(decision_pkg)
        
        # 3. Get charts
        chart_b64 = ChartGenerator.generate_dummy_waterfall()
        
        # 4. Extract specific parts
        feats = decision_pkg["feature_vector"]
        shap_ex = decision_pkg.get("shap_explanations", {})
        
        flags = [
            {"severity": f.severity, "reason": f.reason} 
            for f in profile.reconciliation_flags 
            if f.severity in ["CRITICAL", "HIGH"]
        ]
        
        # 5. Build Pydantic Response
        report = CreditDecisionReport(
            report_id=f"CR_{profile.cin}_{int(datetime.now().timestamp())}",
            generation_timestamp=datetime.utcnow().isoformat() + "Z",
            company_name=decision_pkg["company_name"],
            cin=profile.cin,
            
            probability_of_default=decision_pkg["ml_probability_of_default"],
            credit_rating_tier=decision_pkg["credit_rating_tier"],
            engine_recommendation=decision_pkg["engine_recommendation"],
            
            five_cs_summary=FeatureDump(
                character_score=feats.get("character_score", 0.0),
                capacity_score=feats.get("capacity_score", 0.0),
                capital_score=feats.get("capital_score", 0.0),
                collateral_score=feats.get("collateral_score", 0.0),
                conditions_score=feats.get("conditions_score", 0.0)
            ),
            
            ai_credit_narrative=narrative,
            top_risk_drivers=shap_ex.get("top_risk_drivers", []),
            top_mitigants=shap_ex.get("top_mitigants", []),
            
            critical_reconciliation_flags=flags,
            shap_waterfall_base64=chart_b64
        )
        
        logger.info(f"Successfully generated Decision Report {report.report_id}")
        return report
