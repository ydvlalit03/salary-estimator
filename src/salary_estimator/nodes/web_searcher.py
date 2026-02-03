"""Web searcher node using Google Custom Search API."""

import re
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from salary_estimator.models import SearchResult
from salary_estimator.state import SalaryEstimationState
from salary_estimator.utils.config import get_config


# Regex patterns for extracting salary mentions
SALARY_PATTERNS = [
    r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per\s+)?(?:year|yr|annually|/yr))?',
    r'[\d,]+k\s*-\s*[\d,]+k',
    r'\$[\d,]+k',
    r'(?:salary|compensation|pay|total\s+comp)[:\s]*\$?[\d,]+',
]


def _extract_salary_mentions(text: str) -> list[int]:
    """Extract salary figures from text."""
    salaries = []

    for pattern in SALARY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract numeric values
            numbers = re.findall(r'[\d,]+', match)
            for num_str in numbers:
                try:
                    num = int(num_str.replace(',', ''))
                    # Handle 'k' notation
                    if 'k' in match.lower() and num < 1000:
                        num *= 1000
                    # Filter to reasonable salary range
                    if 30000 <= num <= 2000000:
                        salaries.append(num)
                except ValueError:
                    continue

    return list(set(salaries))  # Remove duplicates


def _calculate_relevance(result: dict, query: str) -> float:
    """Calculate relevance score for a search result."""
    score = 0.5  # Base score

    title = result.get("title", "").lower()
    snippet = result.get("snippet", "").lower()
    link = result.get("link", "").lower()

    # Boost for known salary sources
    trusted_domains = ["levels.fyi", "glassdoor", "indeed", "payscale", "linkedin"]
    domain = urlparse(link).netloc
    if any(d in domain for d in trusted_domains):
        score += 0.2

    # Boost for salary keywords in title/snippet
    salary_keywords = ["salary", "compensation", "pay", "wage", "earning", "total comp"]
    if any(kw in title or kw in snippet for kw in salary_keywords):
        score += 0.15

    # Boost for recent year mentions
    if "2024" in snippet or "2025" in snippet:
        score += 0.1

    # Boost for specific numbers in snippet
    if re.search(r'\$[\d,]+', snippet):
        score += 0.05

    return min(score, 1.0)


def search_web(state: SalaryEstimationState) -> dict:
    """Execute Google searches and parse salary information.

    This is a LangGraph node that takes the current state and returns
    updates to the state.
    """
    queries = state.get("search_queries", [])
    if not queries:
        return {"search_results": []}

    config = get_config()

    # Build the Custom Search service
    try:
        service = build(
            "customsearch",
            "v1",
            developerKey=config.google_cse_api_key,
        )
    except Exception as e:
        print(f"Warning: Could not initialize Google Custom Search: {e}")
        return {"search_results": []}

    all_results = []

    for query in queries:
        try:
            response = (
                service.cse()
                .list(
                    q=query,
                    cx=config.google_cse_id,
                    num=config.max_search_results_per_query,
                )
                .execute()
            )

            items = response.get("items", [])

            for item in items:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")

                # Extract domain
                domain = urlparse(link).netloc

                # Extract salary mentions from snippet
                salary_mentions = _extract_salary_mentions(f"{title} {snippet}")

                # Calculate relevance
                relevance = _calculate_relevance(item, query)

                result = SearchResult(
                    query=query,
                    source=domain,
                    title=title,
                    snippet=snippet,
                    salary_mentions=salary_mentions,
                    relevance_score=relevance,
                )
                all_results.append(result)

        except HttpError as e:
            print(f"Warning: Search failed for query '{query}': {e}")
            continue
        except Exception as e:
            print(f"Warning: Unexpected error for query '{query}': {e}")
            continue

    # Sort by relevance and deduplicate by source
    all_results.sort(key=lambda x: x.relevance_score, reverse=True)

    # Keep top results, preferring diversity of sources
    seen_sources = set()
    filtered_results = []
    for result in all_results:
        if len(filtered_results) >= 15:  # Max 15 results total
            break
        if result.source not in seen_sources or len(filtered_results) < 5:
            filtered_results.append(result)
            seen_sources.add(result.source)

    return {"search_results": filtered_results}
