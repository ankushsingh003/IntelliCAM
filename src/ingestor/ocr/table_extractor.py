"""
src/ingestor/ocr/table_extractor.py

Uses pdfplumber for native PDF table extraction (fast, accurate for digital PDFs).
"""
import logging
from typing import List, Dict, Any, Optional
import pdfplumber

logger = logging.getLogger(__name__)

class TableExtractor:
    """Extracts tables from PDFs using pdfplumber."""

    @staticmethod
    def extract_tables_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts all tables from a PDF file.
        Returns a list of dicts: {"page": int, "table_data": list of lists}
        """
        tables_found = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    extracted_tables = page.extract_tables()
                    for table in extracted_tables:
                        if table:
                            cleaned_table = [
                                [cell if cell is not None else "" for cell in row]
                                for row in table
                            ]
                            tables_found.append({
                                "page": i + 1,
                                "table_data": cleaned_table
                            })
        except Exception as e:
            logger.error(f"Failed to extract tables from {pdf_path}: {e}")
            
        return tables_found
