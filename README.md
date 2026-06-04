<div align="center">

# 💰 Salary Estimator

### A LangGraph AI agent that estimates market salary from a LinkedIn profile

![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_KB-FF6446?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

---

## 📖 Overview

**Salary Estimator** takes a raw LinkedIn profile (pasted text or a file) and returns a **confidence-scored market salary range** with transparent reasoning. It's built as a **LangGraph agent** that doesn't rely on a single source: it parses the profile, then runs **web search** and a **vector knowledge base lookup in parallel**, merges the evidence, strips outliers, applies location and seniority adjustments, and scores how confident it is based on how much agreeing data it found.

The goal is an estimate you can *trust and explain* — not a number a model made up. Every result ships with the data points, the adjustments applied, and the sources used.

---

## 📑 Table of Contents

- [How it works](#-how-it-works)
- [Features](#-features)
- [Tech stack](#-tech-stack)
- [Installation](#-installation)
- [Getting API keys](#-getting-api-keys)
- [Usage](#-usage)
- [Output format](#-output-format)
- [Project structure](#-project-structure)

---

## 🔄 How it works

The agent is a LangGraph `StateGraph` with a **parallel fan-out** in the middle:

```
START ─▶ profile_parser ─▶ query_generator ─┬─▶ search_web ──┐
                                             │                ├─▶ analyze_salary ─▶ END
                                             └─▶ lookup_kb ───┘
                                               (parallel execution)
```

| Node | Role |
|------|------|
| **profile_parser** | Gemini extracts title, company, years of experience and location from raw profile text |
| **query_generator** | builds targeted salary search queries from the parsed profile |
| **search_web** | runs the queries via Google Programmable Search to gather live data points |
| **lookup_kb** | retrieves matching benchmarks from a ChromaDB vector store — *runs at the same time as web search* |
| **analyze_salary** | merges sources, removes outliers, applies location/company-tier/YOE adjustments, and computes a confidence score |

---

## ✨ Features

- **🧾 Profile parsing** — structured extraction (title, company, YOE, location) from messy profile text via Google Gemini
- **🔎 Smart search** — auto-generates focused salary search queries instead of one generic lookup
- **📚 Vector knowledge base** — a ChromaDB store of salary benchmarks for instant, offline-capable grounding
- **⚡ Parallel evidence gathering** — web search and KB lookup execute concurrently for speed
- **🧮 Intelligent analysis** — outlier removal + adjustments for location premium, company tier, and seniority
- **🎯 Confidence scoring** — a score and level (low/medium/high) derived from data quality and quantity, with the exact adjustments listed
- **🖥️ Multiple interfaces** — Streamlit web UI, CLI (file / stdin), and a programmatic Python API

---

## 🛠️ Tech stack

| Concern | Technology |
|---------|------------|
| **Orchestration** | LangGraph, LangChain |
| **LLM** | Google Gemini |
| **Vector DB** | ChromaDB |
| **Web search** | Google Programmable Search Engine (CSE) |
| **UI** | Streamlit |
| **Packaging** | `pip install -e .` (console entry point) |

---

## 📦 Installation

```bash
pip install -e .
cp .env.example .env
```

Add your credentials to `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_CSE_API_KEY=your_cse_api_key
```

Initialize the knowledge base:

```bash
salary-estimator --init-kb
```

---

## 🔑 Getting API keys

1. **Google Gemini** — create a key at [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Google Programmable Search** — create an engine at [Programmable Search Engine](https://programmablesearchengine.google.com/) (search the whole web), note the Search Engine ID (`cx`), then enable the Custom Search API in Google Cloud Console and create an API key with access to it

---

## 🚀 Usage

```bash
# Web UI (recommended)
streamlit run src/salary_estimator/app.py        # http://localhost:8501

# From a file
salary-estimator --file linkedin_profile.txt

# From stdin
cat profile.txt | salary-estimator

# Try the bundled example
salary-estimator --example
```

### Programmatic

```python
from salary_estimator.graph import estimate_salary

profile_text = """
Jane Doe — Staff Software Engineer at Meta, San Francisco, CA
Experience: Staff SWE @ Meta (2022–now), Senior SWE @ Netflix (2019–22), SWE @ Uber (2016–19)
Education: BS Computer Science, MIT
"""

result = estimate_salary(profile_text)
print(result)
```

---

## 📤 Output format

```json
{
  "profile_summary": {
    "title": "Senior Software Engineer",
    "company": "Google",
    "years_of_experience": 7,
    "location": "San Francisco, CA"
  },
  "salary_estimate": { "currency": "USD", "min": 280000, "max": 400000, "median": 340000 },
  "confidence": {
    "score": 0.82,
    "level": "high",
    "data_points": 8,
    "factors": ["+15% for SF Bay Area location", "+10% for FAANG company tier", "Adjusted for 7 YOE (senior level)"]
  },
  "reasoning": "Based on 8 data points from Levels.fyi, Glassdoor and internal benchmarks…",
  "sources": ["internal_kb", "levels.fyi", "glassdoor.com"]
}
```

---

## 🗂️ Project structure

```
src/salary_estimator/
├── graph.py          # LangGraph StateGraph (the agent)
├── nodes/            # profile_parser, query_generator, search_web, lookup_kb, analyze_salary
├── kb/               # ChromaDB knowledge base + seed benchmarks
├── app.py            # Streamlit UI
└── cli.py            # command-line entry point
tests/
```
