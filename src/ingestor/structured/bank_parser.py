"""
src/ingestor/structured/bank_parser.py

Parses Indian bank statements and detects basic circular trading patterns.
"""
import pandas as pd
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BankStatementParser:
    """Parses Bank Statements and extracts features."""

    @staticmethod
    def parse_statement(tables: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts extracted tables into a standardized transaction DataFrame.
        """
        logger.info("Parsing bank statement tables into DataFrame...")
        # Mocking the conversion for the hackathon template
        # Need to handle standard HDFC/ICICI/SBI columns: Date, Narration, Chq/Ref, Value Dt, Withdrawal, Deposit, Balance
        data = [
            {"date": "2024-01-01", "narration": "NEFT-ABC CORP", "withdrawal": 0, "deposit": 500000, "balance": 1500000},
            {"date": "2024-01-02", "narration": "RTGS-XYZ LTD", "withdrawal": 450000, "deposit": 0, "balance": 1050000},
        ]
        return pd.DataFrame(data)

    @staticmethod
    def analyze_cash_flow(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates key banking metrics."""
        if df.empty:
            return {}
            
        total_inward = df['deposit'].sum()
        total_outward = df['withdrawal'].sum()
        avg_balance = df['balance'].mean()
        
        return {
            "total_inward": float(total_inward),
            "total_outward": float(total_outward),
            "average_balance": float(avg_balance),
            "inward_bounce_ratio": 0.02, # Mocked metric
            "outward_bounce_ratio": 0.01 # Mocked metric
        }

    @staticmethod
    def detect_circular_trading(df: pd.DataFrame) -> bool:
        """
        Detects if funds are coming in and immediately going out to related parties.
        (Simplified proxy logic for hackathon)
        """
        # A simple heuristic: High volume of same-day large transactions
        try:
            df['date'] = pd.to_datetime(df['date'])
            daily_aggregates = df.groupby('date').agg({'deposit': 'sum', 'withdrawal': 'sum'})
            
            # If daily withdrawal is > 95% of daily deposit repeatedly on large amounts
            circular_days = daily_aggregates[
                (daily_aggregates['deposit'] > 1000000) & 
                (daily_aggregates['withdrawal'] >= daily_aggregates['deposit'] * 0.95)
            ]
            
            return len(circular_days) > 3
        except Exception as e:
            logger.error(f"Circular trading detection failed: {e}")
            return False
