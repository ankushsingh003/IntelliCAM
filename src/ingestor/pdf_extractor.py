"""
src/ingestor/pdf_extractor.py

Master orchestrator for the OCR pipeline. Handles single document 
extraction including digital text, image preprocessing, 
ensemble OCR for scanned pages, and table extraction.
"""
import logging
from typing import Dict, Any, List
import fitz  # PyMuPDF
from pathlib import Path

from src.ingestor.ocr.image_preprocessor import ImagePreprocessor
from src.ingestor.ocr.ensemble import OCREnsemble
from src.ingestor.ocr.table_extractor import TableExtractor

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Orchestrates full PDF extraction (Text, Tables, OCR)."""

    def __init__(self):
        self.ensemble = OCREnsemble()

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract all contents.
        Args:
            file_path: Absolute path to the PDF.
        Returns:
            Dict containing full text, tables, and page-level details.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Processing document: {path.name}")
        
        doc = fitz.open(file_path)
        full_text_blocks = []
        page_details = []
        
        # 1. Process Each Page (Digital Text + OCR Fallback)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Try native text extraction first
            text = page.get_text("text").strip()
            source = "digital"
            confidence = 1.0
            
            # If native text is too short, assume it's a scanned image
            if len(text) < 50:
                logger.debug(f"Page {page_num+1} seems scanned. Running OCR...")
                
                # Render page to image bytes
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                
                # Preprocess
                cv_img = ImagePreprocessor.preprocess_for_ocr(img_bytes)
                
                # Ensemble OCR
                text, confidence, source = self.ensemble.extract_best(cv_img)
            
            if text:
                full_text_blocks.append(text)
                page_details.append({
                    "page_number": page_num + 1,
                    "text_length": len(text),
                    "source": source,
                    "confidence": float(confidence)
                })

        doc.close()

        # 2. Extract Tables
        tables = TableExtractor.extract_tables_from_pdf(file_path)

        # 3. Assemble Output
        final_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text_blocks)
        
        return {
            "file_name": path.name,
            "total_pages": len(page_details),
            "full_text": final_text,
            "tables": tables,
            "page_details": page_details,
            "average_ocr_confidence": sum([p["confidence"] for p in page_details if p["source"] != "digital"]) / \
                                      max(1, len([p for p in page_details if p["source"] != "digital"]))
        }
