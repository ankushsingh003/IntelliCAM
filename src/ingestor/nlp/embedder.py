"""
src/ingestor/nlp/embedder.py

Handles generating embeddings and interacting with ChromaDB.
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from configs.settings import settings

logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """Handles text embedding and storage in ChromaDB."""

    def __init__(self, collection_name: str = "intellicam_docs"):
        """Initializes the embedding model and vector store."""
        try:
            self.embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model=settings.embedding_model
            )
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_persist_dir
            )
            logger.info(f"Initialized ChromaDB at {settings.chroma_persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize Embedder: {e}")
            self.vectorstore = None

    def embed_and_store(self, chunks: List[str], metadata: Dict[str, Any]) -> List[str]:
        """
        Embeds a list of text chunks and stores them in ChromaDB.
        Attaches the same metadata dict to all chunks.
        """
        if not self.vectorstore or not chunks:
            return []

        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        metadatas = [metadata for _ in range(len(chunks))]

        try:
            self.vectorstore.add_texts(
                texts=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully embedded and stored {len(chunks)} chunks.")
            return ids
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return []

    def similarity_search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Any]:
        """
        Searches the vector store for chunks most similar to the query.
        Returns LangChain Document objects.
        """
        if not self.vectorstore:
            return []
            
        logger.debug(f"Executing vector search: '{query}'")
        try:
            docs = self.vectorstore.similarity_search(
                query=query,
                k=top_k,
                filter=filter_dict
            )
            return docs
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
