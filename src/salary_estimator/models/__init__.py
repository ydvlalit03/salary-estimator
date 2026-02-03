"""Data models for salary estimation."""

from salary_estimator.models.profile import ProfileData
from salary_estimator.models.estimation import SalaryRange, SalaryBenchmark, SearchResult, EstimationResult, ConfidenceInfo

__all__ = [
    "ProfileData",
    "SalaryRange",
    "SalaryBenchmark",
    "SearchResult",
    "EstimationResult",
    "ConfidenceInfo",
]
