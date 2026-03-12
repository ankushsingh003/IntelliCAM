"""
src/research/tools/web_search.py

LangChain custom tool for executing web searches via Tavily API.
Used by the Research Agent to find open-source intelligence.
"""
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import requests
import logging

from configs.settings import settings

logger = logging.getLogger(__name__)

class WebSearchInput(BaseModel):
    query: str = Field(description="The search query to execute on the web.")
    search_depth: Optional[str] = Field(default="basic", description="Either 'basic' or 'advanced'.")

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Use this tool to search the internet for recent news, sector updates, or general information about an Indian company."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, search_depth: str = "basic") -> str:
        """Execute the Tavily search API."""
        if not settings.tavily_api_key:
            return "Error: TAVILY_API_KEY environment variable not set."

        logger.info(f"Executing web search for: '{query}'")
        
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "include_answer": True,
                    "max_results": 5
                },
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract combined answer and result snippets
            answer = data.get("answer", "")
            results = "\n".join([f"- {r['title']}: {r['content'][:200]} ({r['url']})" for r in data.get("results", [])])
            
            return f"Summary Answer:\n{answer}\n\nTop Results:\n{results}"
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Error executing search: {str(e)}"

    async def _arun(self, query: str, search_depth: str = "basic") -> str:
        """Async implementation (optional, falls back to sync if not defined properly)."""
        return self._run(query, search_depth)
