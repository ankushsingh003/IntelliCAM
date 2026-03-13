"""
src/portal/backend/routes/insights.py

API routes for submitting and interpreting Credit Officer field notes.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.portal.backend.ai_interpreter import FieldNoteInterpreter
from src.ingestor.storage.schema import CompanyIdentitySchema

logger = logging.getLogger(__name__)
router = APIRouter()
interpreter = FieldNoteInterpreter()

class InsightSubmission(BaseModel):
    cin: str = Field(description="Company CIN")
    raw_field_notes: str = Field(description="Raw, unstructured text notes from the Credit Officer.")

class ParsedInsightResponse(BaseModel):
    cin: str
    parsed_json: dict
    confidence_score: float

@router.post("/submit", response_model=ParsedInsightResponse)
async def submit_insight(payload: InsightSubmission):
    """
    Accepts raw field notes from a Credit Officer, uses LLM to interpret them 
    into structured variables (e.g. Management Quality, Factory Status), 
    and saves them to the risk profile.
    """
    logger.info(f"Received field notes for CIN: {payload.cin}")
    
    if not payload.raw_field_notes.strip():
        raise HTTPException(status_code=400, detail="Field notes cannot be empty.")
        
    try:
        structured_data = interpreter.interpret_notes(payload.raw_field_notes)
        
        logger.info("Successfully interpreted field notes.")
        
        return ParsedInsightResponse(
            cin=payload.cin,
            parsed_json=structured_data,
            confidence_score=0.95  # Mock confidence for now
        )
    except Exception as e:
        logger.error(f"Error interpreting notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to interpret field notes.")
