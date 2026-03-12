"""
src/ingestor/ocr/tesseract_extractor.py

Pytesseract wrapper as a fallback/alternative OCR engine.
"""
import logging
import pytesseract
from typing import Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class TesseractExtractor:
    """Wrapper for Tesseract OCR."""

    def __init__(self, tesseract_cmd: str = None):
        """
        Optionally override the path to the tesseract executable.
        E.g., /usr/bin/tesseract or C:\\Program Files\\Tesseract-OCR\\tesseract.exe
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image: np.ndarray, lang: str = 'eng+hin') -> Tuple[str, float]:
        """
        Extracts text and computes average confidence using image_to_data.
        """
        try:
            # Get full text
            text = pytesseract.image_to_string(image, lang=lang)
            
            # Get data for confidence calculation
            data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            df = pd.DataFrame(data)
            
            # Filter out empty text blocks usually scored as -1 or 0 irregularly
            valid_conf = df[df['conf'] > 0]
            avg_confidence = valid_conf['conf'].mean() / 100.0 if not valid_conf.empty else 0.0
            
            return text, float(avg_confidence)
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return "", 0.0
