"""
src/ingestor/nlp/chunker.py

Splits large unstructured text into semantic chunks for ingestion into ChromaDB.
"""
import logging
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Chunks documents using LangChain text splitters."""

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n--- PAGE BREAK ---\n\n", "\n\n", "\n", ".", " ", ""],
            length_function=len
        )

    def chunk_text(self, text: str) -> List[str]:
        """Splits a single large text string into multiple smaller strings."""
        if not text or not text.strip():
            return []
            
        logger.debug(f"Chunking text of length {len(text)}...")
        chunks = self.splitter.split_text(text)
        logger.debug(f"Created {len(chunks)} chunks.")
        
        return chunks
