# Salary Estimator

A **LangGraph** AI agent that estimates market salary from a LinkedIn profile. It parses the profile with Gemini, runs web search and a vector knowledge base **in parallel**, then analyzes the combined evidence to return a confidence-scored salary range with transparent reasoning.

---

## How It Works

```
START → profile_parser → query_generator → [ search_web , lookup_kb ] → analyze_salary → END
                                            ↑   parallel execution   ↑
```

The agent fans out to web search and a ChromaDB benchmark store simultaneously, removes outliers, applies location/experience adjustments, and scores its own confidence based on how much agreeing data it found.

---

## Features

- **Profile parsing** — extracts title, company, YOE and location from raw profile text using Google Gemini
- **Smart search** — generates targeted salary search queries
- **Vector knowledge base** — ChromaDB store of salary benchmarks for instant grounding
- **Intelligent analysis** — merges sources, removes outliers, adjusts for location and company tier
- **Confidence scoring** — returns a score + level based on data quality and quantity, with the adjustments it applied

---

## Tech Stack

- **Orchestration**: LangGraph, LangChain
- **LLM**: Google Gemini
- **Vector DB**: ChromaDB
- **Search**: Google Programmable Search (CSE)
- **UI**: Streamlit

---

## Quick Start

### Setup

```bash
pip install -e .
cp .env.example .env
```

Add your keys to `.env`:

```
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_CSE_API_KEY=your_cse_api_key
```

Initialize the knowledge base:

```bash
salary-estimator --init-kb
```

### Usage

```bash
# Web UI
streamlit run src/salary_estimator/app.py

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
result = estimate_salary(profile_text)
```

---

## Output

```json
{
  "salary_estimate": { "currency": "USD", "min": 280000, "max": 400000, "median": 340000 },
  "confidence": { "score": 0.82, "level": "high", "data_points": 8 },
  "adjustments": ["+15% for SF Bay Area", "+10% for FAANG tier"],
  "sources": ["internal_kb", "levels.fyi", "glassdoor.com"]
}
```
