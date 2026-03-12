"""
src/ingestor/ocr/easyocr_extractor.py

EasyOCR wrapper configured for English and Hindi text extraction.
"""
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class EasyOCRExtractor:
    """Wrapper for EasyOCR library."""

    def __init__(self, languages: List[str] = None):
        if languages is None:
            languages = ['en', 'hi']
        
        from easyocr import Reader
        logger.info(f"Initializing EasyOCR for languages: {languages}")
        # gpu=False can be set dynamically based on environment, True default
        self.reader = Reader(languages, gpu=False)

    def extract_text(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extracts text from an image (numpy array).
        Returns the stitched text and the average confidence score.
        """
        # detail=1 returns [bbox, text, prob]
        results = self.reader.readtext(image, detail=1)
        
        texts = []
        confidences = []
        
        for bbox, text, prob in results:
            texts.append(text)
            confidences.append(prob)
            
        full_text = " ".join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return full_text, avg_confidence
