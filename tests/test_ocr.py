"""
tests/test_ocr.py

Unit tests for OCR components. We use mocks to avoid requiring 
heavy OCR engines and actual PDF parsing during basic CI tests.
"""
from __future__ import annotations

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.ingestor.ocr.image_preprocessor import ImagePreprocessor
from src.ingestor.ocr.ensemble import OCREnsemble

class TestImagePreprocessor:
    def test_deskew_no_op_on_empty(self):
        empty_img = np.zeros((100, 100), dtype=np.uint8)
        result = ImagePreprocessor.deskew(empty_img)
        assert np.array_equal(result, empty_img)

class TestOCREnsemble:
    @patch("src.ingestor.ocr.easyocr_extractor.EasyOCRExtractor.extract_text")
    @patch("src.ingestor.ocr.tesseract_extractor.TesseractExtractor.extract_text")
    def test_ensemble_chooses_higher_confidence(self, mock_tess, mock_easy):
        # EasyOCR has higher confidence
        mock_easy.return_value = ("Easy Text", 0.95)
        mock_tess.return_value = ("Tess Text", 0.80)

        with patch("src.ingestor.ocr.easyocr_extractor.EasyOCRExtractor.__init__", return_value=None), \
             patch("src.ingestor.ocr.tesseract_extractor.TesseractExtractor.__init__", return_value=None):
            
            ensemble = OCREnsemble()
            # Manually set mocked instances
            ensemble.easyocr = MagicMock()
            ensemble.easyocr.extract_text = mock_easy
            ensemble.tesseract = MagicMock()
            ensemble.tesseract.extract_text = mock_tess

            dummy_img = np.zeros((10,10))
            text, conf, engine = ensemble.extract_best(dummy_img)

            assert text == "Easy Text"
            assert conf == 0.95
            assert engine == "EasyOCR"

    @patch("src.ingestor.ocr.easyocr_extractor.EasyOCRExtractor.extract_text")
    @patch("src.ingestor.ocr.tesseract_extractor.TesseractExtractor.extract_text")
    def test_ensemble_chooses_tesseract(self, mock_tess, mock_easy):
        # Tesseract has higher confidence
        mock_easy.return_value = ("Easy Text", 0.60)
        mock_tess.return_value = ("Tess Text", 0.88)

        with patch("src.ingestor.ocr.easyocr_extractor.EasyOCRExtractor.__init__", return_value=None), \
             patch("src.ingestor.ocr.tesseract_extractor.TesseractExtractor.__init__", return_value=None):
            
            ensemble = OCREnsemble()
            ensemble.easyocr = MagicMock()
            ensemble.easyocr.extract_text = mock_easy
            ensemble.tesseract = MagicMock()
            ensemble.tesseract.extract_text = mock_tess

            dummy_img = np.zeros((10,10))
            text, conf, engine = ensemble.extract_best(dummy_img)

            assert text == "Tess Text"
            assert conf == 0.88
            assert engine == "Tesseract"
