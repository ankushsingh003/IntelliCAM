"""
src/ingestor/router.py

Document routing logic: Takes a FileTypeResult + ClassificationResult
and returns the correct processing pipeline to invoke.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from src.ingestor.document_classifier import ClassificationResult, DocumentType
from src.ingestor.file_type_detector import FileTypeResult

logger = logging.getLogger(__name__)


class PipelineRoute(str, Enum):
    """Named processing routes available in the system."""
    GST_PROCESSOR      = "gst_processor"
    BANK_PROCESSOR     = "bank_processor"
    ITR_PROCESSOR      = "itr_processor"
    NLP_EXTRACTOR      = "nlp_extractor"      # generic unstructured
    LEGAL_NLP_EXTRACTOR= "legal_nlp_extractor" # legal notices & sanction letters
    MANUAL_REVIEW      = "manual_review"      # low confidence / unknown


@dataclass
class RoutingDecision:
    route: PipelineRoute
    doc_type: DocumentType
    file_category: str
    reason: str
    requires_manual_review: bool = False
    priority: int = 1  # 1 = normal, 2 = urgent (manual review)


_DOC_TYPE_TO_ROUTE: dict[DocumentType, PipelineRoute] = {
    DocumentType.GST_RETURN:           PipelineRoute.GST_PROCESSOR,
    DocumentType.INCOME_TAX_RETURN:    PipelineRoute.ITR_PROCESSOR,
    DocumentType.BANK_STATEMENT:       PipelineRoute.BANK_PROCESSOR,
    DocumentType.ANNUAL_REPORT:        PipelineRoute.NLP_EXTRACTOR,
    DocumentType.FINANCIAL_STATEMENT:  PipelineRoute.NLP_EXTRACTOR,
    DocumentType.BOARD_MEETING_MINUTES: PipelineRoute.NLP_EXTRACTOR,
    DocumentType.RATING_AGENCY_REPORT: PipelineRoute.NLP_EXTRACTOR,
    DocumentType.SHAREHOLDING_PATTERN: PipelineRoute.NLP_EXTRACTOR,
    DocumentType.LEGAL_NOTICE:         PipelineRoute.LEGAL_NLP_EXTRACTOR,
    DocumentType.SANCTION_LETTER:      PipelineRoute.LEGAL_NLP_EXTRACTOR,
    DocumentType.OTHER:                PipelineRoute.MANUAL_REVIEW,
}


class DocumentRouter:
    """
    Routes a document to the appropriate processing pipeline
    based on its file type and LLM classification result.
    """

    def route(
        self,
        file_result: FileTypeResult,
        classification: ClassificationResult,
    ) -> RoutingDecision:
        """
        Determine the correct pipeline for the given document.

        Args:
            file_result: Output of FileTypeDetector.
            classification: Output of DocumentClassifier.

        Returns:
            RoutingDecision describing where to send the document.
        """
        if file_result.file_category == "unknown":
            return RoutingDecision(
                route=PipelineRoute.MANUAL_REVIEW,
                doc_type=DocumentType.OTHER,
                file_category=file_result.file_category,
                reason="Unknown file type — cannot process automatically.",
                requires_manual_review=True,
                priority=2,
            )

        if classification.requires_manual_review:
            return RoutingDecision(
                route=PipelineRoute.MANUAL_REVIEW,
                doc_type=classification.document_type,
                file_category=file_result.file_category,
                reason=(
                    f"Low classification confidence ({classification.confidence:.0%}). "
                    f"Tentative type: {classification.document_type.value}. "
                    "Credit officer review required."
                ),
                requires_manual_review=True,
                priority=2,
            )

        route = _DOC_TYPE_TO_ROUTE.get(classification.document_type, PipelineRoute.MANUAL_REVIEW)

        decision = RoutingDecision(
            route=route,
            doc_type=classification.document_type,
            file_category=file_result.file_category,
            reason=(
                f"Classified as '{classification.document_type.value}' "
                f"(confidence={classification.confidence:.0%}) → routed to {route.value}."
            ),
            requires_manual_review=False,
            priority=1,
        )

        logger.info(
            f"ROUTE: {file_result.extension} file classified as "
            f"{classification.document_type.value} → {route.value}"
        )
        return decision

    def route_batch(
        self,
        documents: list[tuple[FileTypeResult, ClassificationResult]],
    ) -> list[RoutingDecision]:
        """Route a batch of documents, returning decisions in the same order."""
        return [self.route(ft, cl) for ft, cl in documents]
