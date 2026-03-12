"""
tests/test_classifier.py

Unit tests for Step 1: Document Classification & Routing
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from src.ingestor.document_classifier import (
    DocumentClassifier, DocumentType, ClassificationResult
)
from src.ingestor.file_type_detector import FileTypeResult
from src.ingestor.router import DocumentRouter, PipelineRoute, RoutingDecision


# ────────────────────────────────────────────────────────────────────────────
# DocumentClassifier Tests
# ────────────────────────────────────────────────────────────────────────────

class TestDocumentClassifier:

    def _make_mock_client(self, doc_type: str, confidence: float, reasoning: str = "test"):
        """Helper to build a mock OpenAI client returning a given classification."""
        import json
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "document_type": doc_type,
            "confidence": confidence,
            "reasoning": reasoning,
        })
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    def test_classify_gst_return_high_confidence(self):
        client = self._make_mock_client("gst_return", 0.95, "Contains GSTIN and GSTR-3B header")
        classifier = DocumentClassifier(llm_client=client)
        result = classifier.classify("GSTN: 27AAACR5055K1ZJ GSTR-3B summary return for FY 2023-24")
        assert result.document_type == DocumentType.GST_RETURN
        assert result.confidence == 0.95
        assert result.requires_manual_review is False

    def test_classify_bank_statement(self):
        client = self._make_mock_client("bank_statement", 0.92)
        classifier = DocumentClassifier(llm_client=client)
        result = classifier.classify("Account No: 001234567890 HDFC Bank Statement Jan 2024")
        assert result.document_type == DocumentType.BANK_STATEMENT
        assert result.is_structured is True

    def test_classify_annual_report(self):
        client = self._make_mock_client("annual_report", 0.88)
        classifier = DocumentClassifier(llm_client=client)
        result = classifier.classify("Directors Report for FY 2023-24. Dear Shareholders...")
        assert result.document_type == DocumentType.ANNUAL_REPORT
        assert result.is_unstructured is True

    def test_low_confidence_triggers_manual_review(self):
        client = self._make_mock_client("bank_statement", 0.60)
        classifier = DocumentClassifier(llm_client=client)
        result = classifier.classify("Some ambiguous text that is hard to classify")
        assert result.requires_manual_review is True

    def test_empty_text_returns_other_with_manual_review(self):
        classifier = DocumentClassifier(llm_client=MagicMock())
        result = classifier.classify("   ")
        assert result.document_type == DocumentType.OTHER
        assert result.requires_manual_review is True

    def test_is_legal_property(self):
        result = ClassificationResult(DocumentType.LEGAL_NOTICE, 0.9)
        assert result.is_legal is True
        result2 = ClassificationResult(DocumentType.BANK_STATEMENT, 0.9)
        assert result2.is_legal is False


# ────────────────────────────────────────────────────────────────────────────
# DocumentRouter Tests
# ────────────────────────────────────────────────────────────────────────────

class TestDocumentRouter:

    def _make_file_result(self, category: str, ext: str = ".pdf") -> FileTypeResult:
        return FileTypeResult(
            mime_type="application/pdf",
            file_category=category,
            extension=ext,
        )

    def _make_classification(
        self, doc_type: DocumentType, confidence: float = 0.9
    ) -> ClassificationResult:
        return ClassificationResult(
            document_type=doc_type,
            confidence=confidence,
            requires_manual_review=(confidence < 0.75),
        )

    def test_gst_routes_to_gst_processor(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("pdf"),
            self._make_classification(DocumentType.GST_RETURN),
        )
        assert decision.route == PipelineRoute.GST_PROCESSOR

    def test_bank_routes_to_bank_processor(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("spreadsheet", ".xlsx"),
            self._make_classification(DocumentType.BANK_STATEMENT),
        )
        assert decision.route == PipelineRoute.BANK_PROCESSOR

    def test_itr_routes_to_itr_processor(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("pdf"),
            self._make_classification(DocumentType.INCOME_TAX_RETURN),
        )
        assert decision.route == PipelineRoute.ITR_PROCESSOR

    def test_legal_notice_routes_to_legal_nlp(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("pdf"),
            self._make_classification(DocumentType.LEGAL_NOTICE),
        )
        assert decision.route == PipelineRoute.LEGAL_NLP_EXTRACTOR

    def test_annual_report_routes_to_nlp_extractor(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("pdf"),
            self._make_classification(DocumentType.ANNUAL_REPORT),
        )
        assert decision.route == PipelineRoute.NLP_EXTRACTOR

    def test_unknown_file_type_routes_to_manual_review(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("unknown", ".xyz"),
            self._make_classification(DocumentType.OTHER),
        )
        assert decision.route == PipelineRoute.MANUAL_REVIEW
        assert decision.requires_manual_review is True
        assert decision.priority == 2

    def test_low_confidence_routes_to_manual_review(self):
        router = DocumentRouter()
        decision = router.route(
            self._make_file_result("pdf"),
            self._make_classification(DocumentType.BANK_STATEMENT, confidence=0.50),
        )
        assert decision.route == PipelineRoute.MANUAL_REVIEW
        assert decision.requires_manual_review is True

    def test_route_batch(self):
        router = DocumentRouter()
        pairs = [
            (self._make_file_result("pdf"), self._make_classification(DocumentType.GST_RETURN)),
            (self._make_file_result("pdf"), self._make_classification(DocumentType.BANK_STATEMENT)),
        ]
        decisions = router.route_batch(pairs)
        assert len(decisions) == 2
        assert decisions[0].route == PipelineRoute.GST_PROCESSOR
        assert decisions[1].route == PipelineRoute.BANK_PROCESSOR
