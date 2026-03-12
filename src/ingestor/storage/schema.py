"""
src/ingestor/storage/schema.py

Defines Pydantic schemas for the normalized data ready for Delta Lake storage.
"""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class CompanyIdentitySchema(BaseModel):
    """Core identity information."""
    company_name: str
    cin: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    industry_sector: Optional[str] = None

class FinancialMetricsSchema(BaseModel):
    """Normalized financial facts."""
    cin: str
    financial_year: str
    revenue_crs: float = Field(default=0.0)
    ebitda_crs: float = Field(default=0.0)
    net_profit_crs: float = Field(default=0.0)
    total_debt_crs: float = Field(default=0.0)
    net_worth_crs: float = Field(default=0.0)

class BankFlowSchema(BaseModel):
    """Aggregated bank statement flows."""
    cin: str
    month_year: str
    total_inward_flows: float
    total_outward_flows: float
    average_balance: float
    bounce_count: int = 0

class LegalRiskSchema(BaseModel):
    """Extracted legal/dispute flags."""
    cin: str
    case_type: str
    severity: str  # High, Medium, Low
    amount_involved_crs: Optional[float] = 0.0
    status: str

class UnifiedRiskProfile(BaseModel):
    """The master JSON that combines all data for the Recommendation Engine."""
    identity: CompanyIdentitySchema
    financials: List[FinancialMetricsSchema]
    bank_flows: List[BankFlowSchema]
    legal_risks: List[LegalRiskSchema]
    data_completeness_score: float = Field(ge=0.0, le=100.0)
