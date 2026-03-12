"""
src/research/tools/mca_fetcher.py

Mock integration for MCA21 API (Ministry of Corporate Affairs, India).
Fetches master data and charge register for a given CIN.
"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class MCAInput(BaseModel):
    cin: str = Field(description="The 21-character Corporate Identification Number (CIN)")

class MCAFetcherTool(BaseTool):
    name = "mca_master_data"
    description = "Fetch official Ministry of Corporate Affairs (MCA) data including directors, paid-up capital, and charge register (active loans) using a company's CIN."
    args_schema: Type[BaseModel] = MCAInput

    def _run(self, cin: str) -> str:
        logger.info(f"Fetching MCA data for CIN: {cin}")
        
        # In a real hackathon submission, this would call an API like Razorpay MCA or setu.co
        # We are mocking the response based on typical MCA master data
        if len(cin) < 20:
            return "Error: Invalid CIN format. Ensure it is a 21-character string."
            
        mock_response = f"""
        MCA Master Data for CIN: {cin}
        --------------------------------
        Company Status: Active
        Date of Incorporation: 15-Jun-2010
        Class: Private
        Authorized Capital: Rs 5,000,000
        Paid Up Capital: Rs 1,000,000
        
        Directors:
        1. RAHUL SHARMA (DIN: 01234567)
        2. ANITA DESAI (DIN: 09876543)
        
        Charge Register (Active Loans):
        1. Charge ID: 10010010 | Amount: Rs 15,000,000 | Holder: HDFC Bank | Status: OPEN
        2. Charge ID: 10020020 | Amount: Rs 5,000,000 | Holder: Bajaj Finance | Status: CLOSED
        """
        
        return mock_response

    async def _arun(self, cin: str) -> str:
        return self._run(cin)
