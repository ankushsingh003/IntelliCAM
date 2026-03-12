"""
src/ingestor/nlp/extractor_prompts.py

Contains zero-shot / few-shot prompt templates for specific data extraction tasks.
"""

BOARD_MEETING_PROMPT = """
You are analyzing Board Meeting Minutes for an Indian corporate borrower.
Based on the provided text, extract key decisions related to borrowing, restructuring, or collateral changes.

Text Context:
{context}

Return a valid JSON object matching this schema:
{{
    "authorized_borrowing_limit_crs": <float or null>,
    "key_decisions": ["string", "string"],
    "new_collateral_pledged": ["string", "string"],
    "management_changes": ["string", "string"]
}}
"""

ANNUAL_REPORT_MD&A_PROMPT = """
Analyze the Management Discussion & Analysis (MD&A) section from the company's Annual Report.
Identify key growth drivers, risks, and forward-looking guidance.

Text Context:
{context}

Return a valid JSON object matching this schema:
{{
    "future_guidance": "string summary",
    "key_risks_identified": ["string", "string"],
    "industry_tailwinds": ["string", "string"],
    "capex_plans": "string summary"
}}
"""

LEGAL_NOTICE_PROMPT = """
Analyze the provided legal document (Notice, Summons, or Default Notice) under Indian jurisdiction.
Identify the plaintiff, the amount involved, and the severity of the legal action.

Text Context:
{context}

Return a valid JSON object matching this schema:
{{
    "plaintiff_or_issuer": "string",
    "amount_in_dispute_crs": <float or null>,
    "severity": "High" | "Medium" | "Low",
    "summary": "string"
}}
"""
