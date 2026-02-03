# Salary Estimator

A LangGraph-based AI agent that estimates market salary from LinkedIn profiles.

## Features

- **Profile Parsing**: Extracts structured data from LinkedIn profiles using Google Gemini
- **Smart Search**: Generates targeted Google search queries for salary data
- **Knowledge Base**: ChromaDB-powered vector database with salary benchmarks
- **Intelligent Analysis**: Combines multiple data sources, removes outliers, applies location/experience adjustments
- **Confidence Scoring**: Provides confidence scores based on data quality and quantity

## Architecture

```
START → profile_parser → query_generator → [search_web, lookup_kb] → analyze_salary → END
                                            ↑ parallel execution ↑
```

## Setup

### 1. Install Dependencies

```bash
cd ~/salary-estimator
pip install -e .
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_CSE_API_KEY=your_cse_api_key
```

### Getting API Keys

1. **Google Gemini API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key

2. **Google Custom Search Engine**:
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Create a new search engine (search the entire web)
   - Note the Search Engine ID (cx parameter)
   - Enable the Custom Search API in Google Cloud Console
   - Create an API key with Custom Search API access

### 3. Initialize Knowledge Base

```bash
salary-estimator --init-kb
```

## Usage

### Web Interface (Streamlit)

```bash
streamlit run src/salary_estimator/app.py
```

This launches a web UI at `http://localhost:8501` where you can:
- Paste LinkedIn profiles
- Load example profiles for testing
- View detailed salary estimates with confidence scores

### From a File (CLI)

```bash
salary-estimator --file linkedin_profile.txt
```

### From Stdin

```bash
cat profile.txt | salary-estimator
```

### Test with Example Profile

```bash
salary-estimator --example
```

### Programmatic Usage

```python
from salary_estimator.graph import estimate_salary

profile_text = """
Jane Doe
Staff Software Engineer at Meta

San Francisco, CA

Experience:
- Staff Software Engineer at Meta (2022 - Present)
- Senior Software Engineer at Netflix (2019 - 2022)
- Software Engineer at Uber (2016 - 2019)

Education: BS Computer Science, MIT
Skills: Python, Java, Distributed Systems, Machine Learning
"""

result = estimate_salary(profile_text)
print(result)
```

## Output Format

```json
{
  "profile_summary": {
    "title": "Senior Software Engineer",
    "company": "Google",
    "years_of_experience": 7,
    "location": "San Francisco, CA"
  },
  "salary_estimate": {
    "currency": "USD",
    "min": 280000,
    "max": 400000,
    "median": 340000
  },
  "confidence": {
    "score": 0.82,
    "level": "high",
    "data_points": 8,
    "factors": [
      "+15% for SF Bay Area location",
      "+10% for FAANG company tier",
      "Adjusted for 7 YOE (senior level)"
    ]
  },
  "reasoning": "Based on 8 data points from Levels.fyi, Glassdoor, and internal benchmarks. The estimate reflects SF Bay Area premium and FAANG-level compensation.",
  "sources": ["internal_kb", "levels.fyi", "glassdoor.com"],
  "adjustments": [
    "+15% for SF Bay Area location",
    "+10% for FAANG company tier"
  ]
}
```

## Development

### Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Project Structure

```
salary-estimator/
├── src/salary_estimator/
│   ├── main.py           # CLI entry point
│   ├── graph.py          # LangGraph workflow
│   ├── state.py          # State schema
│   ├── nodes/
│   │   ├── profile_parser.py    # Profile extraction
│   │   ├── query_generator.py   # Search query generation
│   │   ├── web_searcher.py      # Google Custom Search
│   │   ├── knowledge_base.py    # ChromaDB operations
│   │   └── salary_analyzer.py   # Final analysis
│   └── models/
│       ├── profile.py    # Profile data models
│       └── estimation.py # Estimation models
├── data/
│   └── salary_benchmarks.json  # Seed data for KB
└── tests/
    └── test_graph.py     # Integration tests
```
