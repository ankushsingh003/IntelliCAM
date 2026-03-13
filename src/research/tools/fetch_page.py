"""
src/research/tools/fetch_page.py

LangChain custom tool to fetch and extract raw text from a specific URL.
Used by the Research Agent to deep-dive into a specific article or report.
"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class FetchPageInput(BaseModel):
    url: str = Field(description="The absolute URL of the webpage to scrape.")

class FetchPageTool(BaseTool):
    name = "fetch_page_content"
    description = "Use this tool to fetch the text content of a specific webpage by URL. Use this after a web search if you need more details from a specific result."
    args_schema: Type[BaseModel] = FetchPageInput

    def _run(self, url: str) -> str:
        """Execute HTTP request and beautiful soup parsing."""
        logger.info(f"Fetching page content from: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text(separator="\n")
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            
            words = text.split()
            if len(words) > 4000:
                text = " ".join(words[:4000]) + "\n\n...[Content Truncated]..."
                
            return text
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return f"Error fetching webpage: {str(e)}"

    async def _arun(self, url: str) -> str:
        return self._run(url)
