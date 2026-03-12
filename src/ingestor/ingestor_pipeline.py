"""
src/ingestor/ingestor_pipeline.py

Master Orchestrator for Phase 1: Data Ingestor.
Coordinates Document Classification, OCR, Structured Parsers, 
NLP extraction, and Storage.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List

from src.ingestor.file_type_detector import detect_file_type
from src.ingestor.document_classifier import DocumentClassifier
from src.ingestor.router import DocumentRouter, PipelineRoute
from src.ingestor.pdf_extractor import PDFExtractor

from src.ingestor.structured.gst_parser import GSTParser
from src.ingestor.structured.bank_parser import BankStatementParser
from src.ingestor.structured.reconciler import CrossSourceReconciler

from src.ingestor.nlp.chunker import DocumentChunker
from src.ingestor.nlp.embedder import DocumentEmbedder

from src.ingestor.storage.schema import UnifiedRiskProfile, CompanyIdentitySchema
from src.ingestor.storage.quality_scorer import DataQualityScorer
from src.ingestor.storage.databricks_writer import DatabricksWriter

logger = logging.getLogger(__name__)

class DataIngestorPipeline:
    """Master Pipeline for Data Ingestion (Phase 1)."""

    def __init__(self):
        self.classifier = DocumentClassifier()
        self.router = DocumentRouter()
        self.pdf_extractor = PDFExtractor()
        
        self.chunker = DocumentChunker()
        self.embedder = DocumentEmbedder()
        
        self.writer = DatabricksWriter()
        self.scorer = DataQualityScorer()

    def process_directory(self, customer_cin: str, dir_path: str) -> UnifiedRiskProfile:
        """
        Process all documents in a directory for a given customer.
        Returns the initial unified risk profile.
        """
        target_dir = Path(dir_path)
        if not target_dir.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        logger.info(f"Starting Data Ingestion Pipeline for CIN: {customer_cin}")
        
        # Accumulators
        gst_data = {}
        bank_data = {}
        itr_data = {}
        
        # 1. Process files
        for file_path in target_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                self._process_single_file(file_path, customer_cin, gst_data, bank_data, itr_data)

        # 2. Reconcile Structured Data
        reconciliation = CrossSourceReconciler.generate_consolidated_report(gst_data, bank_data, itr_data)
        logger.info(f"Reconciliation Status: {reconciliation.get('status')}")

        # 3. Assemble Initial Profile
        profile = UnifiedRiskProfile(
            identity=CompanyIdentitySchema(company_name="Pending Profile", cin=customer_cin),
            financials=[],
            bank_flows=[],
            legal_risks=[],
            data_completeness_score=0.0
        )
        
        # 4. Score Quality
        score = self.scorer.calculate_completeness(profile)
        profile.data_completeness_score = score
        
        # 5. Write to Lake
        self.writer.write_profile(profile)
        
        return profile

    def _process_single_file(self, file_path: Path, cin: str, gst_data: dict, bank_data: dict, itr_data: dict):
        """Routes and executes logic for a single document."""
        logger.info(f"Processing file: {file_path.name}")
        
        # 1. Detect & Extract
        file_info = detect_file_type(file_path)
        
        if file_info.is_pdf:
            doc_data = self.pdf_extractor.process_document(str(file_path))
            full_text = doc_data["full_text"]
        else:
            logger.warning(f"Skipping non-PDF file currently: {file_path.name}")
            return

        # 2. Classify
        classification = self.classifier.classify_from_file_text(full_text)
        
        # 3. Route
        decision = self.router.route(file_info, classification)
        
        # 4. Embed to Vector Store (for all unstructured access later)
        chunks = self.chunker.chunk_text(full_text)
        if chunks:
            self.embedder.embed_and_store(chunks, {"cin": cin, "file_name": file_path.name, "doc_type": classification.document_type.value})

        # 5. Execute Structured Pipeline based on route
        if decision.route == PipelineRoute.GST_PROCESSOR:
            parsed = GSTParser.parse_gstr3b(doc_data)
            gst_data.update(parsed)
            
        elif decision.route == PipelineRoute.BANK_PROCESSOR:
            # Mock bank table processing for the flow
            parsed = BankStatementParser.analyze_cash_flow(BankStatementParser.parse_statement([]))
            bank_data.update(parsed)
            
        else:
            # ReAct agent or NLP extractor will pick this up in Phase 2/3
            logger.debug(f"{file_path.name} routed to Unstructured pool.")

