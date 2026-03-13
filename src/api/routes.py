"""
src/api/routes.py

Endpoints for triggering the full IntelliCAM pipeline.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.ingestor.ingestor_pipeline import DataIngestorPipeline
from src.research.research_pipeline import ResearchPipeline
from src.engine.decision_report import ReportBuilder

logger = logging.getLogger(__name__)
router = APIRouter()

class AppraisalRequest(BaseModel):
    cin: str = Field(description="Corporate Identification Number", example="U72900KA2020PTC123456")
    documents_folder_path: str = Field(description="Local path to the folder containing GST, Bank, ITR, and PDF docs")
    credit_officer_notes: str = Field(default="", description="Optional manual field notes")

class AppraisalResponse(BaseModel):
    status: str
    message: str
    report_id: str

ingestor = DataIngestorPipeline()
researcher = ResearchPipeline()
reporter = ReportBuilder()

def run_full_pipeline(payload: AppraisalRequest):
    """Executes Phase 1, 2, and 3 synchronously (or background)."""
    try:
        logger.info(f"--- STARTED FULL APPRAISAL PIPELINE FOR {payload.cin} ---")
        
        ingestor_profile = ingestor.process_directory(payload.cin, payload.documents_folder_path)
        
        reconciled_profile = researcher.execute(
            ingestor_profile, 
            primary_insights={"raw_notes": payload.credit_officer_notes} if payload.credit_officer_notes else {}
        )
        
        final_report = reporter.generate_report(reconciled_profile)
        
        logger.info(f"--- FINISHED FINAL REPORT: RECOMMENDATION = {final_report.engine_recommendation} ---")
        return final_report
        
    except Exception as e:
        logger.error(f"Pipeline failed for {payload.cin}: {e}", exc_info=True)

@router.post("/appraise", response_model=AppraisalResponse)
async def trigger_appraisal(payload: AppraisalRequest, background_tasks: BackgroundTasks):
    """
    Triggers the end-to-end IntelliCAM analysis pipeline.
    Because it takes time (OCR, LLMs, web research), it runs in the background.
    """
    logger.info(f"Received appraisal request for CIN: {payload.cin}")
    
    background_tasks.add_task(run_full_pipeline, payload)
    
    return AppraisalResponse(
        status="Processing",
        message="Appraisal pipeline started in the background. Check logs for the final output.",
        report_id=f"PENDING_{payload.cin}"
    )

@router.post("/appraise_sync")
async def trigger_appraisal_sync(payload: AppraisalRequest):
    """Testing endpoint: Runs the whole pipeline synchronously and blocks until the Report JSON is returned."""
    try:
        report = run_full_pipeline(payload)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
