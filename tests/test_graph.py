"""Integration tests for the salary estimation graph."""

import pytest
from unittest.mock import patch, MagicMock

from salary_estimator.models import ProfileData, SalaryBenchmark, SearchResult
from salary_estimator.state import SalaryEstimationState
from salary_estimator.nodes.knowledge_base import lookup_knowledge_base


# Sample profile for testing
SAMPLE_PROFILE = ProfileData(
    title="Senior Software Engineer",
    company="Google",
    company_tier="faang",
    years_of_experience=7,
    location="San Francisco, CA",
    skills=["Python", "Go", "Kubernetes"],
    education="M.S. Computer Science, Stanford",
    industry="Technology",
    seniority_level="senior",
)


class TestProfileData:
    """Tests for ProfileData model."""

    def test_profile_creation(self):
        """Test creating a ProfileData instance."""
        profile = ProfileData(
            title="Software Engineer",
            company="Startup Inc",
            years_of_experience=3,
            location="Austin, TX",
        )
        assert profile.title == "Software Engineer"
        assert profile.company_tier == "unknown"
        assert profile.seniority_level == "mid"

    def test_to_search_context(self):
        """Test generating search context string."""
        context = SAMPLE_PROFILE.to_search_context()
        assert "Senior Software Engineer" in context
        assert "Google" in context
        assert "San Francisco" in context
        assert "7 years" in context


class TestKnowledgeBase:
    """Tests for knowledge base operations."""

    def test_lookup_empty_profile(self):
        """Test KB lookup with no profile."""
        state: SalaryEstimationState = {}
        result = lookup_knowledge_base(state)
        assert result["kb_matches"] == []

    @patch("salary_estimator.nodes.knowledge_base._get_collection")
    def test_lookup_with_profile(self, mock_collection):
        """Test KB lookup with a valid profile."""
        # Mock ChromaDB collection
        mock_coll = MagicMock()
        mock_coll.count.return_value = 10
        mock_coll.query.return_value = {
            "metadatas": [[
                {
                    "role": "Senior Software Engineer",
                    "location": "San Francisco, CA",
                    "company_tier": "faang",
                    "years_of_experience_min": 5,
                    "years_of_experience_max": 10,
                    "salary_min": 280000,
                    "salary_max": 400000,
                    "salary_median": 340000,
                    "currency": "USD",
                    "source": "internal_kb",
                    "year": 2024,
                }
            ]],
            "distances": [[0.1]],
        }
        mock_collection.return_value = mock_coll

        state: SalaryEstimationState = {"profile": SAMPLE_PROFILE}
        result = lookup_knowledge_base(state)

        assert len(result["kb_matches"]) == 1
        assert result["kb_matches"][0].role == "Senior Software Engineer"
        assert result["kb_matches"][0].salary_median == 340000


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        result = SearchResult(
            query="Senior Software Engineer salary SF",
            source="glassdoor.com",
            title="Senior Software Engineer Salaries",
            snippet="Average salary is $180,000 to $250,000",
            salary_mentions=[180000, 250000],
            relevance_score=0.85,
        )
        assert result.source == "glassdoor.com"
        assert len(result.salary_mentions) == 2
        assert result.relevance_score == 0.85


class TestSalaryBenchmark:
    """Tests for SalaryBenchmark model."""

    def test_benchmark_creation(self):
        """Test creating a SalaryBenchmark instance."""
        benchmark = SalaryBenchmark(
            role="Software Engineer",
            location="New York, NY",
            salary_min=150000,
            salary_max=200000,
            salary_median=175000,
        )
        assert benchmark.currency == "USD"
        assert benchmark.source == "internal_kb"
        assert benchmark.company_tier == "unknown"


# Note: Full integration tests require API keys and are meant to be run manually
# pytest tests/test_graph.py -v
