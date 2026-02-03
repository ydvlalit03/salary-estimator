"""Profile data models."""

from pydantic import BaseModel, Field


class ProfileData(BaseModel):
    """Structured data extracted from a LinkedIn profile."""

    title: str = Field(description="Current job title/role")
    company: str = Field(description="Current company name")
    company_tier: str = Field(
        default="unknown",
        description="Company tier: 'faang', 'tier1', 'tier2', 'startup', 'unknown'",
    )
    years_of_experience: float = Field(
        ge=0, description="Total years of professional experience"
    )
    location: str = Field(description="Work location (city, state/country)")
    skills: list[str] = Field(default_factory=list, description="Key technical skills")
    education: str = Field(
        default="", description="Highest education level or notable degree"
    )
    industry: str = Field(default="", description="Industry sector")
    seniority_level: str = Field(
        default="mid",
        description="Seniority: 'entry', 'mid', 'senior', 'staff', 'principal', 'executive'",
    )

    def to_search_context(self) -> str:
        """Generate a context string for search query generation."""
        parts = [self.title]
        if self.company:
            parts.append(f"at {self.company}")
        if self.location:
            parts.append(f"in {self.location}")
        if self.years_of_experience:
            parts.append(f"with {self.years_of_experience:.0f} years experience")
        return " ".join(parts)
