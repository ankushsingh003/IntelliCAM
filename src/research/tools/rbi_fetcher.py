"""
src/research/tools/rbi_fetcher.py

Mock integration to check Reserve Bank of India (RBI) Defaulter Lists 
and CFR (Central Fraud Registry) mentions.
"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class RBIInput(BaseModel):
    company_name: str = Field(description="The legal name of the company to check against RBI lists.")

class RBIFetcherTool(BaseTool):
    name = "rbi_defaulter_check"
    description = "Check if the company or its promoters are listed in the RBI Willful Defaulters list, CIBIL Suit Filed accounts, or specific banking circulars."
    args_schema: Type[BaseModel] = RBIInput

    def _run(self, company_name: str) -> str:
        logger.info(f"Checking RBI lists for: {company_name}")
        
        mock_response = f"""
        RBI & CIBIL Suit Filed Check for: {company_name}
        -------------------------------------------------
        - RBI Central Fraud Registry: NO MATCH FOUND
        - Willful Defaulters List (>Rs 25 Lakhs): NO MATCH FOUND
        - SMA-2 (Special Mention Account) / NPA Warnings: Clear
        
        Result: Clean record in RBI public databases.
        """
        
        return mock_response

    async def _arun(self, company_name: str) -> str:
        return self._run(company_name)
