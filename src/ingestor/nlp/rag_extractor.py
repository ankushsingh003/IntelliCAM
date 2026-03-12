"""
src/ingestor/nlp/rag_extractor.py

Orchestrates RAG (Retrieval-Augmented Generation) pipeline using the Embedder
and an LLM to answer specific prompts based on retrieved context.
"""
import logging
import json
from typing import Dict, Any, Optional

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from configs.settings import settings
from src.ingestor.nlp.embedder import DocumentEmbedder

logger = logging.getLogger(__name__)

class RAGExtractor:
    """Uses LLM + Vector Store to answer prompts accurately."""

    def __init__(self, embedder: Optional[DocumentEmbedder] = None):
        self.embedder = embedder or DocumentEmbedder()
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            temperature=0.0,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

    def extract(self, query: str, prompt_template_str: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs RAG to fetch context and extract structured JSON using the given prompt.
        """
        # Retrieve context from ChromaDB
        filter_dict = {"file_name": file_name} if file_name else None
        
        docs = self.embedder.similarity_search(query=query, top_k=4, filter_dict=filter_dict)
        if not docs:
            logger.warning(f"No context retrieved for query: '{query}'")
            return {"status": "no_context_found"}

        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        prompt_template = PromptTemplate.from_template(prompt_template_str)
        formatted_prompt = prompt_template.format(context=context)

        logger.info(f"Invoking LLM for RAG extraction (context size: {len(context)} chars).")
        
        # Invoke LLM
        try:
            response = self.llm.invoke(formatted_prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Failed to generate and parse LLM extraction: {e}")
            return {"status": "extraction_error", "error": str(e)}
