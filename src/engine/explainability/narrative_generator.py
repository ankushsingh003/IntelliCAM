"""
src/engine/explainability/narrative_generator.py

Uses GPT-4o to translate raw SHAP values and the Feature Vector into 
a human-readable Credit Assessment Narrative.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from configs.settings import settings

logger = logging.getLogger(__name__)

_NARRATIVE_PROMPT = """
You are an expert Chief Risk Officer for an Indian Bank. Write a 2-paragraph 
'Credit Decision Summary' for the relationship manager based on the following model outputs.

Company: {company}
Model Decision: {decision} (PD: {pd})

Top Risk Drivers (Factors pushing towards Default):
{risk_drivers}

Top Mitigants (Factors demonstrating Repayment Ability):
{mitigants}

Be highly professional, concise, and reference Indian specific context if relevant.
"""

class NarrativeGenerator:
    """Translates ML SHAP outputs to plain English."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0.3
        )
        self.prompt = PromptTemplate.from_template(_NARRATIVE_PROMPT)

    def generate_narrative(self, decision_package: dict) -> str:
        """Calls the LLM to generate the final human explanation."""
        logger.info(f"Generating human narrative for {decision_package['company_name']}")
        
        # Format drivers
        shap_exps = decision_package.get("shap_explanations", {})
        
        rd_str = "\n".join([f"- {d['feature']} (value: {d['value']:.2f})" for d in shap_exps.get("top_risk_drivers", [])])
        mit_str = "\n".join([f"- {d['feature']} (value: {d['value']:.2f})" for d in shap_exps.get("top_mitigants", [])])
        
        formatted_prompt = self.prompt.format(
            company=decision_package.get("company_name", "Unknown"),
            decision=decision_package.get("engine_recommendation", "Unknown"),
            pd=decision_package.get("ml_probability_of_default", "Unknown"),
            risk_drivers=rd_str or "None identified.",
            mitigants=mit_str or "None identified."
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            return "Narrative generation failed due to an API error."
