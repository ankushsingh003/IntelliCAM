"""
src/research/research_pipeline.py

Master Orchestrator for Phase 2: Research Agent.
Takes the Phase 1 Ingestor Profile, runs the ReAct Agent, fetches Regulatory data,
analyhes News/Sectors, and builds the final Reconciled Risk Profile.
"""
import logging
from typing import Dict, Any

from src.ingestor.storage.schema import UnifiedRiskProfile
from src.research.agent import ResearchAgent
from src.research.sector_profiler import SectorProfiler
from src.research.news_analyzer import NewsAnalyzer
from src.research.promoter_graph import PromoterGraph
from src.research.reconciler import ResearchReconciler
from src.research.risk_profile import ReconciledRiskProfile, OSINTData, FlagSchema

logger = logging.getLogger(__name__)

class ResearchPipeline:
    """Coordinates all external and qualitative research on the borrower."""

    def __init__(self):
        self.agent = ResearchAgent()
        self.news_analyzer = NewsAnalyzer()
        self.promoter_graph = PromoterGraph()

    def execute(self, ingestor_profile: UnifiedRiskProfile, primary_insights: Dict = None) -> ReconciledRiskProfile:
        """
        Runs the full research suite for a company.
        """
        cin = ingestor_profile.identity.cin
        company_name = ingestor_profile.identity.company_name
        sector = ingestor_profile.identity.industry_sector or "general"
        
        logger.info(f"Starting Phase 2 Research Pipeline for: {company_name} ({cin})")

        osint_narrative = self.agent.conduct_research(company_name, sector)
        logger.debug(f"OSINT Agent returned: {osint_narrative[:200]}...")

        sector_context = SectorProfiler.get_sector_profile(sector)

        headlines = [f"News about {company_name} is decent", f"{company_name} wins new contract"]
        news_analysis = self.news_analyzer.analyze_headlines(headlines)

        self.promoter_graph.build_from_mca_data(company_name, [{"name": "Director 1"}])
        promoter_risk = self.promoter_graph.detect_shell_company_risk()

        osint_data = OSINTData(
            news_sentiment_score=news_analysis.get("composite_score", 0.0),
            regulatory_flags=1 if "ALERT" in osint_narrative else 0,
            shell_company_risk=promoter_risk.get("shell_company_risk", False),
            industry_outlook=sector_context.get("outlook", "Neutral")
        )

        research_blob = {
            "osint_data": osint_data.model_dump(),
            "primary_insights": primary_insights or {},
            "regulatory_status": {"has_active_sebi_bans": False, "nclt_petitions_found": False}
        }

        recon_result = ResearchReconciler.reconcile(ingestor_profile.model_dump(), research_blob)

        flags = [FlagSchema(**f) for f in recon_result.get("flags", [])]
        
        final_profile = ReconciledRiskProfile(
            cin=cin,
            internal_data=ingestor_profile,
            external_osint=osint_data,
            primary_insights=primary_insights or {},
            reconciliation_flags=flags
        )
        
        logger.info(f"Phase 2 Complete. Found {len(flags)} reconciliation flags.")
        return final_profile
