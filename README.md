# 🏦 IntelliCAM — AI-Powered Corporate Credit Decisioning Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange?style=for-the-badge)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**Hackathon: Vivirth ML — "Intelli-Credit" Challenge**
*Next-Gen Corporate Credit Appraisal: Bridging the Intelligence Gap*

</div>

---

## 🎯 What is IntelliCAM?

IntelliCAM is an **end-to-end AI-powered Credit Decisioning Engine** that automates the preparation of a **Comprehensive Credit Appraisal Memo (CAM)** for Indian corporate loan applications.

It ingests multi-source data (GST filings, bank statements, annual reports, legal documents), performs autonomous web-scale research, scores the borrower across the **Five Cs of Credit**, and generates a fully explainable CAM — in minutes instead of weeks.

---

## 🏗️ Architecture

```
[Input Documents]
      │
      ▼
┌─────────────────────────┐
│  PHASE 1: Data Ingestor │
│  • Document Classifier  │
│  • OCR Pipeline         │
│  • GST/Bank Parser      │
│  • NLP/RAG Extractor    │
│  • Databricks Storage   │
└───────────┬─────────────┘
            │ Normalized Risk Data
            ▼
┌─────────────────────────┐
│  PHASE 2: Research Agent│
│  • Web Crawler (ReAct)  │
│  • MCA / e-Courts fetcher│
│  • News Sentiment (FinBERT)│
│  • Primary Insights Portal│
└───────────┬─────────────┘
            │ Enriched Risk Profile
            ▼
┌─────────────────────────────┐
│  PHASE 3: Recommendation    │
│  Engine                     │
│  • Five Cs Feature Engineer │
│  • XGBoost Scorer           │
│  • SHAP Explainability      │
│  • Decision Logic           │
│  • CAM Generator (PDF/Word) │
└───────────┬─────────────────┘
            │
            ▼
   [CAM Report + Decision]
   Approve/Reject + Limit + Rate
```

---

## 📁 Project Structure

```
IntelliCAM/
├── src/
│   ├── ingestor/               # Phase 1: Data Ingestor
│   │   ├── ocr/                # OCR pipeline (EasyOCR + Tesseract)
│   │   ├── structured/         # GST, Bank, ITR parsers
│   │   ├── nlp/                # RAG extraction pipeline
│   │   └── storage/            # Schema & Databricks writer
│   ├── research/               # Phase 2: Research Agent
│   │   └── tools/              # MCA, eCourts, News tools
│   ├── portal/                 # Credit Officer Portal
│   │   ├── backend/            # FastAPI backend
│   │   └── frontend/           # React UI
│   ├── engine/                 # Phase 3: Recommendation Engine
│   │   ├── features/           # Five Cs feature engineering
│   │   ├── model/              # XGBoost + rule-based scorer
│   │   ├── explainability/     # SHAP + narrative generator
│   │   ├── decision/           # Loan limit + pricing logic
│   │   └── cam/                # CAM document generator
│   └── api/                    # Master FastAPI orchestration API
├── tests/                      # All unit + integration tests
├── data/                       # Sample data (gitignored raw data)
├── models/                     # Trained ML models (gitignored)
├── configs/                    # Configuration files
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/ankushsingh003/IntelliCAM.git
cd IntelliCAM
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run the API
```bash
uvicorn src.api.main:app --reload --port 8000
```

### 4. Run Tests
```bash
pytest tests/ -v
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (for GPT-4o) |
| `TAVILY_API_KEY` | Tavily search API key |
| `GOOGLE_API_KEY` | Google Gemini API key (optional) |
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_TOKEN` | Databricks personal access token |
| `CHROMA_PERSIST_DIR` | Path for ChromaDB persistence |
| `REDIS_URL` | Redis URL for Celery task queue |

---

## 🧪 Evaluation Criteria

| Criterion | Our Approach |
|---|---|
| **Extraction Accuracy** | EasyOCR + Tesseract ensemble, OpenCV preprocessing, India-specific normalization |
| **Research Depth** | LangChain ReAct agent with MCA21, eCourts, RBI, SEBI, Tavily tools |
| **Explainability** | SHAP waterfall charts + GPT-4o narrative, full source citations |
| **Indian Context** | GSTR-2A vs 3B reconciliation, CIBIL integration, lakh/crore normalization |

---

## 📊 Five Cs of Credit Scoring

| C | Weight | Key Signals |
|---|---|---|
| Character | 25% | Litigation score, adverse news, CIBIL history |
| Capacity | 30% | DSCR, GST revenue, EBITDA margin vs sector |
| Capital | 20% | Net worth, D/E ratio, promoter contribution |
| Collateral | 15% | Asset type, LTV, MCA charge register |
| Conditions | 10% | Sector outlook, regulatory headwinds |

---

## 👥 Team

Built for the **Vivirth ML Hackathon** — Intelli-Credit Challenge

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
