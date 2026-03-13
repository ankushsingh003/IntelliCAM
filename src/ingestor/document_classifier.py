"""
src/ingestor/document_classifier.py

LLM-based document type classifier.
Extracts first-page text and sends to GPT-4o for classification
into one of the defined Indian financial document types.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    GST_RETURN = "gst_return"
    INCOME_TAX_RETURN = "income_tax_return"
    BANK_STATEMENT = "bank_statement"
    ANNUAL_REPORT = "annual_report"
    FINANCIAL_STATEMENT = "financial_statement"
    BOARD_MEETING_MINUTES = "board_meeting_minutes"
    RATING_AGENCY_REPORT = "rating_agency_report"
    SHAREHOLDING_PATTERN = "shareholding_pattern"
    LEGAL_NOTICE = "legal_notice"
    SANCTION_LETTER = "sanction_letter"
    OTHER = "other"


@dataclass
class ClassificationResult:
    document_type: DocumentType
    confidence: float                       # 0.0 – 1.0
    reasoning: str = ""
    requires_manual_review: bool = False

    @property
    def is_structured(self) -> bool:
        return self.document_type in (
            DocumentType.GST_RETURN,
            DocumentType.INCOME_TAX_RETURN,
            DocumentType.BANK_STATEMENT,
        )

    @property
    def is_unstructured(self) -> bool:
        return not self.is_structured and self.document_type != DocumentType.OTHER

    @property
    def is_legal(self) -> bool:
        return self.document_type in (DocumentType.LEGAL_NOTICE, DocumentType.SANCTION_LETTER)


_CLASSIFICATION_PROMPT = """You are a financial document classifier specializing in Indian corporate lending documents.

Classify the following document text into EXACTLY ONE of these categories:
- gst_return: GST filing (GSTR-1, GSTR-2A, GSTR-2B, GSTR-3B, annual return)
- income_tax_return: Income Tax Return (ITR-1 through ITR-7, Form 16, 26AS)
- bank_statement: Bank account statement from any Indian bank
- annual_report: Company annual report (contains directors' report, auditor's report)
- financial_statement: Standalone financial statements (balance sheet, P&L, cash flow)
- board_meeting_minutes: Minutes of board meetings or AGM/EGM proceedings
- rating_agency_report: Credit rating report from CRISIL, ICRA, CARE, Brickwork, etc.
- shareholding_pattern: Shareholding pattern or share capital details
- legal_notice: Legal notice, demand notice, court summons, FIR copy
- sanction_letter: Loan sanction letter or term sheet from another bank/NBFC
- other: Does not fit any above category

Respond ONLY with a valid JSON object with these exact keys:
{{
  "document_type": "<category from above>",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence explanation>"
}}

Document text (first 500 words):
---
{text_sample}
---
"""


class DocumentClassifier:
    """
    Uses GPT-4o (or any configured LLM) to classify a document based on
    a 500-word text sample from its first page(s).
    """

    CONFIDENCE_THRESHOLD = 0.75  # Route to manual review below this

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: An OpenAI-compatible chat completions client.
                        If None, loads from configs/settings.py.
        """
        self._client = llm_client
        self._model = "gpt-4o"

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
            from configs.settings import settings
            return OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

    def classify(self, text_sample: str) -> ClassificationResult:
        """
        Classify a document given a text sample (≤ 500 words recommended).

        Args:
            text_sample: Extracted text from the document's first page(s).

        Returns:
            ClassificationResult with type, confidence, and reasoning.
        """
        if not text_sample or len(text_sample.strip()) < 20:
            logger.warning("Text sample too short for reliable classification.")
            return ClassificationResult(
                document_type=DocumentType.OTHER,
                confidence=0.0,
                reasoning="Insufficient text for classification.",
                requires_manual_review=True,
            )

        words = text_sample.split()
        truncated = " ".join(words[:500])

        prompt = _CLASSIFICATION_PROMPT.format(text_sample=truncated)

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=200,
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return ClassificationResult(
                document_type=DocumentType.OTHER,
                confidence=0.0,
                reasoning=f"LLM error: {str(e)[:100]}",
                requires_manual_review=True,
            )

        try:
            doc_type = DocumentType(data.get("document_type", "other"))
        except ValueError:
            doc_type = DocumentType.OTHER

        confidence = float(data.get("confidence", 0.0))
        reasoning = data.get("reasoning", "")

        result = ClassificationResult(
            document_type=doc_type,
            confidence=confidence,
            reasoning=reasoning,
            requires_manual_review=(confidence < self.CONFIDENCE_THRESHOLD),
        )

        logger.info(
            f"Classified as '{doc_type.value}' "
            f"(confidence={confidence:.2f}, review={result.requires_manual_review})"
        )
        return result

    def classify_from_file_text(self, full_text: str, max_words: int = 500) -> ClassificationResult:
        """Convenience method: pass full extracted text, auto-truncates."""
        sample = " ".join(full_text.split()[:max_words])
        return self.classify(sample)
