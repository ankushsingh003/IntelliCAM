"""
src/ingestor/ocr/ensemble.py

Confidence-based ensemble voting between Tesseract and EasyOCR.
Returns the result with the higher confidence score.
"""
import logging
from typing import Tuple
import numpy as np
from src.ingestor.ocr.easyocr_extractor import EasyOCRExtractor
from src.ingestor.ocr.tesseract_extractor import TesseractExtractor

logger = logging.getLogger(__name__)

class OCREnsemble:
    """Ensemble text extraction choosing the best result based on confidence."""

    def __init__(self):
        self.easyocr = EasyOCRExtractor(languages=['en', 'hi'])
        self.tesseract = TesseractExtractor()

    def extract_best(self, image: np.ndarray) -> Tuple[str, float, str]:
        """
        Runs both engines and returns the best text, confidence, and engine name.
        """
        logger.debug("Running EasyOCR...")
        easy_text, easy_conf = self.easyocr.extract_text(image)
        
        logger.debug("Running Tesseract...")
        tess_text, tess_conf = self.tesseract.extract_text(image)
        
        logger.debug(f"EasyOCR conf: {easy_conf:.2f}, Tesseract conf: {tess_conf:.2f}")

        if easy_conf >= tess_conf:
            return easy_text, easy_conf, "EasyOCR"
        else:
            return tess_text, tess_conf, "Tesseract"
