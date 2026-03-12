"""
src/research/agent.py

The core ReAct (Reasoning + Acting) Agent for the Research Phase.
Provides the agent with web search, scraping, and specialized API tools.
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from configs.settings import settings
from src.research.tools.web_search import WebSearchTool
from src.research.tools.fetch_page import FetchPageTool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert AI Credit Analyst acting as a 'Digital Credit Manager' for an Indian corporate lending bank. 
Your goal is to conduct autonomous web research on a corporate borrower to build an Open-Source Intelligence (OSINT) profile.

You must look for:
1. Adverse news or litigation involving the company or its promoters/directors.
2. Sector outlook, macro-economic headwinds, or industry tailwinds for their specific industry in India.
3. Competitor financial summaries or operational updates.

Follow this thought process (ReAct):
- Thought: What do I need to search for?
- Action: Use the appropriate tool (e.g., web_search).
- Observation: Read the result. If a specific URL looks very important, use fetch_page_content.
- Final Answer: Once you have enough information, compile a detailed summary answering the user's prompt.

Ensure that the final output is highly relevant to Indian corporate credit appraisal and uses appropriate terminology (Crores, Lakhs, RBI, SEBI, etc.).
"""

class ResearchAgent:
    """Orchestrates the LangChain agent and its tools."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0.2
        )
        
        # We will add more tools in Step 2 (MCA, eCourts, etc.)
        self.tools = [
            WebSearchTool(),
            FetchPageTool()
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            max_iterations=8,
            handle_parsing_errors=True
        )
        
        self.chat_history = []

    def conduct_research(self, company_name: str, industry: Optional[str] = None) -> str:
        """
        Kicks off the agent loop to research a specific company.
        """
        logger.info(f"Starting autonomous research for: {company_name}")
        
        industry_context = f" operating in the '{industry}' sector" if industry else ""
        
        query = (
            f"Conduct comprehensive credit risk research on '{company_name}'{industry_context} in India. "
            f"Find any recent news, management changes, ongoing litigations, or significant industry trends "
            f"that could impact their ability to repay a major corporate loan."
        )
        
        response = self.agent_executor.invoke({
            "input": query,
            "chat_history": self.chat_history
        })
        
        # Save to memory context for follow-ups
        self.chat_history.extend([
            HumanMessage(content=query),
            AIMessage(content=response["output"])
        ])
        
        return response["output"]

    def follow_up_query(self, query: str) -> str:
        """Allows interactive querying based on the previous research."""
        response = self.agent_executor.invoke({
            "input": query,
            "chat_history": self.chat_history
        })
        
        self.chat_history.extend([
            HumanMessage(content=query),
            AIMessage(content=response["output"])
        ])
        return response["output"]
