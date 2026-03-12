"""
src/ingestor/file_type_detector.py

MIME-based file type detection using python-magic.
Falls back to extension-based detection if python-magic is unavailable.
"""
from __future__ import annotations

import os
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Attempt to import python-magic (libmagic backed)
try:
    import magic  # python-magic or python-magic-bin
    _MAGIC_AVAILABLE = True
except ImportError:
    _MAGIC_AVAILABLE = False
    logger.warning("python-magic not available; falling back to extension-based MIME detection.")


@dataclass
class FileTypeResult:
    mime_type: str
    file_category: str   # 'pdf' | 'image' | 'spreadsheet' | 'word' | 'unknown'
    extension: str

    @property
    def is_pdf(self) -> bool:
        return self.file_category == "pdf"

    @property
    def is_image(self) -> bool:
        return self.file_category == "image"

    @property
    def is_spreadsheet(self) -> bool:
        return self.file_category == "spreadsheet"

    @property
    def is_word(self) -> bool:
        return self.file_category == "word"


_MIME_TO_CATEGORY: dict[str, str] = {
    "application/pdf": "pdf",
    "image/jpeg": "image",
    "image/png": "image",
    "image/tiff": "image",
    "image/bmp": "image",
    "image/webp": "image",
    "application/vnd.ms-excel": "spreadsheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
    "text/csv": "spreadsheet",
    "application/msword": "word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",
}

_EXT_TO_CATEGORY: dict[str, str] = {
    ".pdf": "pdf",
    ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".tiff": "image", ".tif": "image", ".bmp": "image",
    ".xls": "spreadsheet", ".xlsx": "spreadsheet", ".csv": "spreadsheet",
    ".doc": "word", ".docx": "word",
}


def detect_file_type(file_path: str | Path) -> FileTypeResult:
    """
    Detect the MIME type and category of a file.

    Args:
        file_path: Path to the file to inspect.

    Returns:
        FileTypeResult with mime_type, file_category, and extension.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    # 1. Try python-magic for true MIME detection
    if _MAGIC_AVAILABLE:
        try:
            mime_type: str = magic.from_file(str(path), mime=True)
        except Exception as e:
            logger.warning(f"python-magic failed for {path.name}: {e}; falling back.")
            mime_type = _fallback_mime(path, extension)
    else:
        mime_type = _fallback_mime(path, extension)

    category = _MIME_TO_CATEGORY.get(mime_type) or _EXT_TO_CATEGORY.get(extension, "unknown")

    logger.debug(f"Detected: {path.name} → mime={mime_type}, category={category}")
    return FileTypeResult(mime_type=mime_type, file_category=category, extension=extension)


def _fallback_mime(path: Path, extension: str) -> str:
    """Extension-based MIME fallback."""
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"
