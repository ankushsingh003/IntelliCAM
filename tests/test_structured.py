"""
tests/test_structured.py

Unit tests for structured data processing.
"""
import pytest
import pandas as pd
from src.ingestor.structured.gst_parser import GSTParser
from src.ingestor.structured.bank_parser import BankStatementParser
from src.ingestor.structured.itr_parser import ITRParser
from src.ingestor.structured.reconciler import CrossSourceReconciler

class TestStructuredParsers:
    
    def test_gst_reconciliation(self):
        # 3B claims 1.2M, 2B only shows 1.0M. 20% variance should trigger flag.
        res = GSTParser.reconcile_2b_vs_3b(
            gstr2b_data={"total_itc_available": 1000000.0},
            gstr3b_data={"total_itc_eligible": 1200000.0}
        )
        assert res["variance_pct"] == 20.0
        assert res["flag_excess_itc"] is True

    def test_bank_analysis(self):
        df = BankStatementParser.parse_statement([])
        metrics = BankStatementParser.analyze_cash_flow(df)
        assert metrics["total_inward"] == 500000.0
        assert metrics["total_outward"] == 450000.0
        
    def test_itr_extraction(self):
        res = ITRParser.extract_metrics("dummy text")
        assert res["gross_total_income"] == 25000000.0

class TestReconciler:
    
    def test_gst_vs_bank_mismatch(self):
        # GST is 20M, Bank inward is only 10M -> 50% variance, should flag
        res = CrossSourceReconciler.reconcile_gst_vs_bank(20000000.0, 10000000.0)
        assert res["flag_revenue_mismatch"] is True
        assert res["variance_pct"] == 50.0

    def test_gst_vs_itr_match_no_flag(self):
        # GST 20M, ITR 19M -> 5% variance, shouldn't flag
        res = CrossSourceReconciler.reconcile_gst_vs_itr(20000000.0, 19000000.0)
        assert res["flag_itr_gst_mismatch"] is False
