"""
src/research/tools/ecourts_fetcher.py

Mock integration for Indian e-Courts/NCLT databases.
Searches for active litigation, bankruptcy (IBC) proceedings, or winding up petitions.
"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class ECourtsInput(BaseModel):
    company_name: str = Field(description="The exact legal name of the company.")

class ECourtsFetcherTool(BaseTool):
    name = "ecourts_litigation_search"
    description = "Search Indian e-Courts, High Courts, and NCLT (National Company Law Tribunal) for active lawsuits, defaults, or bankruptcy proceedings against a company."
    args_schema: Type[BaseModel] = ECourtsInput

    def _run(self, company_name: str) -> str:
        logger.info(f"Searching e-Courts for: {company_name}")
        
        # Mocking the response. A real integration might use a legal API provider.
        if "fraud" in company_name.lower() or "default" in company_name.lower():
             return f"ALERT: Found 3 active cases in NCLT Mumbai against {company_name} under IBC Section 7 for loan default."
             
        mock_response = f"""
        e-Courts & NCLT Search Results for: {company_name}
        -------------------------------------------------
        1. NCLT Delhi: Case No. CP(IB)/123/2023 | Petitioner: Vendor XYZ | Status: Disposed (Settled out of court)
        2. Bombay High Court: Civil Suit 456/2022 | Subject: Commercial Contract Dispute | Status: Pending (Next hearing Oct 2024)
        
        No systemic defaults or bankruptcy proceedings found.
        """
        
        return mock_response

    async def _arun(self, company_name: str) -> str:
        return self._run(company_name)
