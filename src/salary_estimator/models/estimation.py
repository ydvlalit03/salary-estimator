"""Salary estimation data models."""

from pydantic import BaseModel, Field


class SalaryRange(BaseModel):
    """Estimated salary range."""

    currency: str = Field(default="USD", description="Currency code")
    min: int = Field(description="Minimum salary estimate")
    max: int = Field(description="Maximum salary estimate")
    median: int = Field(description="Median/expected salary")


class SalaryBenchmark(BaseModel):
    """Internal knowledge base salary benchmark."""

    role: str = Field(description="Job role/title")
    location: str = Field(description="Location")
    company_tier: str = Field(default="unknown", description="Company tier")
    years_of_experience_min: int = Field(default=0)
    years_of_experience_max: int = Field(default=30)
    salary_min: int = Field(description="Minimum salary in range")
    salary_max: int = Field(description="Maximum salary in range")
    salary_median: int = Field(description="Median salary")
    currency: str = Field(default="USD")
    source: str = Field(default="internal_kb", description="Data source")
    year: int = Field(default=2024, description="Data year")


class SearchResult(BaseModel):
    """Processed web search result with salary information."""

    query: str = Field(description="The search query used")
    source: str = Field(description="Source website/domain")
    title: str = Field(description="Result title")
    snippet: str = Field(description="Result snippet/description")
    salary_mentions: list[int] = Field(
        default_factory=list, description="Salary figures found in result"
    )
    relevance_score: float = Field(
        default=0.5, ge=0, le=1, description="How relevant this result is"
    )


class ConfidenceInfo(BaseModel):
    """Confidence information for the estimate."""

    score: float = Field(ge=0, le=1, description="Confidence score 0-1")
    level: str = Field(description="Confidence level: 'low', 'medium', 'high'")
    data_points: int = Field(description="Number of data points used")
    factors: list[str] = Field(
        default_factory=list, description="Factors affecting confidence"
    )


class EstimationResult(BaseModel):
    """Complete salary estimation result."""

    profile_summary: dict = Field(description="Summary of extracted profile")
    salary_estimate: SalaryRange = Field(description="Estimated salary range")
    confidence: ConfidenceInfo = Field(description="Confidence information")
    reasoning: str = Field(description="Explanation of the estimation logic")
    sources: list[str] = Field(description="Data sources used")
    adjustments: list[str] = Field(
        default_factory=list, description="Adjustments made to base salary"
    )
