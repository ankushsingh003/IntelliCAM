"""
src/portal/backend/ai_interpreter.py

Uses LLM (GPT-4o) to structure messy field notes from the Credit Officer.
"""
import logging
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from configs.settings import settings

logger = logging.getLogger(__name__)

_INTERPRETER_PROMPT = """
You are assisting an Indian Corporate Credit Officer. They just visited a client's factory and took messy, quick notes.
Your job is to extract structured credit variables from their raw notes.

Look for:
- Quality of Management (Good / Average / Poor)
- Factory Operating Capacity (% utilization)
- Labor unrest or strikes mentioned
- Inventory pileup observed (Yes / No)

Raw Notes:
{notes}

Respond strictly with a JSON object containing these keys:
{{"management_quality": "str", "factory_utilization_pct": float, "labor_issues": bool, "inventory_pileup": bool, "summary": "str"}}
"""

class FieldNoteInterpreter:
    """Interprets unstructured qualitative field notes into structured risk data."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0.0,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        self.prompt = PromptTemplate.from_template(_INTERPRETER_PROMPT)

    def interpret_notes(self, raw_notes: str) -> dict:
        """Parses the qualitative notes to JSON."""
        logger.debug("Prompting LLM to interpret field notes...")
        
        formatted_prompt = self.prompt.format(notes=raw_notes)
        
        try:
            response = self.llm.invoke(formatted_prompt)
            data = json.loads(response.content)
            return data
        except Exception as e:
            logger.error(f"LLM Interpretation failed: {e}")
            # Fallback
            return {
                "management_quality": "Average",
                "factory_utilization_pct": 0.0,
                "labor_issues": False,
                "inventory_pileup": False,
                "summary": "Failed to parse notes."
            }
