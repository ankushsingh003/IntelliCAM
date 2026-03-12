"""
src/ingestor/ocr/image_preprocessor.py

OpenCV pipeline to preprocess images for optimal OCR.
Includes grayscale, binarization, deskewing, and noise reduction.
"""
import cv2
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """Handles image preprocessing for OCR."""

    @staticmethod
    def preprocess_for_ocr(image_bytes: bytes) -> np.ndarray:
        """
        Main pipeline: Takes raw image bytes, returns preprocessed OpenCV image.
        """
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image bytes")

        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Deskew
        gray = ImagePreprocessor.deskew(gray)

        # 3. Adaptive Thresholding (Binarization)
        # Using adaptive thresholding usually works best for document text
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        return thresh

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Detect outline and deskew image."""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # If angle is very small, ignore it
        if abs(angle) < 0.5:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
