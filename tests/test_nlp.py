"""
tests/test_nlp.py

Unit tests for NLP components including chunker, embedder, and postprocessor.
"""
import pytest
from src.ingestor.nlp.chunker import DocumentChunker
from src.ingestor.nlp.postprocessor import IndianContextPostprocessor

class TestDocumentChunker:
    
    def test_chunking_large_text(self):
        text = "A" * 2000
        chunker = DocumentChunker(chunk_size=1500, chunk_overlap=200)
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 2
        assert len(chunks[0]) == 1500
        assert len(chunks[1]) == 700

    def test_chunking_empty_string(self):
        chunker = DocumentChunker()
        chunks = chunker.chunk_text("")
        assert chunks == []

class TestIndianContextPostprocessor:

    def test_crope_conversion(self):
        val = IndianContextPostprocessor.normalize_currency_to_inr_absolute("1.5 Cr")
        assert val == 15000000.0
        
    def test_lakh_conversion(self):
        val = IndianContextPostprocessor.normalize_currency_to_inr_absolute("25 Lakhs")
        assert val == 2500000.0
        
    def test_plain_number(self):
        val = IndianContextPostprocessor.normalize_currency_to_inr_absolute("50,000")
        assert val == 50000.0
        
    def test_unparsable_string(self):
        val = IndianContextPostprocessor.normalize_currency_to_inr_absolute("Unknown Amount")
        assert val == 0.0
