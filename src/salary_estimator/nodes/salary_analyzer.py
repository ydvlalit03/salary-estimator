"""Salary analyzer node using Gemini for final estimation."""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from salary_estimator.models import SalaryRange, EstimationResult, ConfidenceInfo
from salary_estimator.state import SalaryEstimationState
from salary_estimator.utils.config import get_config


class SalaryAnalysis(BaseModel):
    """Structured output for salary analysis."""

    salary_min: int = Field(description="Minimum estimated annual salary in USD")
    salary_max: int = Field(description="Maximum estimated annual salary in USD")
    salary_median: int = Field(description="Most likely/median annual salary in USD")
    confidence_score: float = Field(
        ge=0, le=1, description="Confidence score from 0.0 to 1.0"
    )
    confidence_level: str = Field(
        description="Confidence level: 'low', 'medium', or 'high'"
    )
    reasoning: str = Field(
        description="2-3 sentence explanation of the estimation logic and key factors"
    )
    adjustments: list[str] = Field(
        description="List of adjustments made (e.g., '+15% for SF location')"
    )


SALARY_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert compensation analyst. Your task is to estimate a realistic salary range based on profile data, web search results, and internal benchmarks.

Analysis Guidelines:
1. **Identify Base Salary**: Start with the most relevant data points from benchmarks and search results
2. **Remove Outliers**: Ignore salary figures that are clearly outliers (unusually high or low)
3. **Apply Adjustments**:
   - Location: Adjust for cost of living (SF/NYC +15-20%, Austin -10%, Remote -15%)
   - Company Tier: FAANG/Top Tier +20-30%, Startups vary widely
   - Experience: Each year above median adds 3-5%
   - Skills: In-demand skills (AI/ML, Cloud) add 5-10%
   - Seniority: Staff/Principal levels significantly higher than base

4. **Calculate Confidence**:
   - High (0.8-1.0): 5+ relevant data points, consistent ranges, matching location/role
   - Medium (0.5-0.79): 3-4 data points, some variation
   - Low (0.0-0.49): Few data points, high variation, uncertain matches

5. **Provide Reasoning**: Explain the key factors that influenced your estimate

Be conservative and realistic. Consider total compensation (base + bonus + equity) for tech roles."""),
    ("human", """Analyze and estimate salary for this profile:

## Profile
- Title: {title}
- Company: {company} ({company_tier})
- Location: {location}
- Years of Experience: {years_of_experience}
- Seniority Level: {seniority_level}
- Skills: {skills}
- Industry: {industry}

## Internal Benchmark Data
{kb_data}

## Web Search Results
{search_data}

Please provide a salary range estimate with confidence score and reasoning.""")
])


def _format_kb_data(state: SalaryEstimationState) -> str:
    """Format knowledge base matches for the prompt."""
    kb_matches = state.get("kb_matches", [])
    if not kb_matches:
        return "No internal benchmark data available."

    lines = []
    for match in kb_matches:
        lines.append(
            f"- {match.role} at {match.company_tier} company in {match.location}: "
            f"${match.salary_min:,}-${match.salary_max:,} (median: ${match.salary_median:,}) "
            f"for {match.years_of_experience_min}-{match.years_of_experience_max} YOE"
        )
    return "\n".join(lines)


def _format_search_data(state: SalaryEstimationState) -> str:
    """Format search results for the prompt."""
    search_results = state.get("search_results", [])
    if not search_results:
        return "No web search data available."

    lines = []
    for result in search_results:
        salaries = ", ".join(f"${s:,}" for s in result.salary_mentions) if result.salary_mentions else "no specific figures"
        lines.append(
            f"- [{result.source}] {result.title[:60]}...\n"
            f"  Salaries mentioned: {salaries}\n"
            f"  Snippet: {result.snippet[:150]}..."
        )
    return "\n".join(lines[:10])  # Limit to top 10


def _count_data_points(state: SalaryEstimationState) -> int:
    """Count total data points available."""
    count = 0
    count += len(state.get("kb_matches", []))
    for result in state.get("search_results", []):
        count += len(result.salary_mentions)
    return count


def analyze_salary(state: SalaryEstimationState) -> dict:
    """Analyze all data and produce final salary estimation.

    This is a LangGraph node that takes the current state and returns
    updates to the state.
    """
    profile = state.get("profile")
    if profile is None:
        raise ValueError("No profile data available")

    config = get_config()

    llm = ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0.1,  # Low temperature for consistent analysis
    )

    structured_llm = llm.with_structured_output(SalaryAnalysis)

    chain = SALARY_ANALYSIS_PROMPT | structured_llm

    # Format data for prompt
    kb_data = _format_kb_data(state)
    search_data = _format_search_data(state)

    analysis = chain.invoke({
        "title": profile.title,
        "company": profile.company,
        "company_tier": profile.company_tier,
        "location": profile.location,
        "years_of_experience": profile.years_of_experience,
        "seniority_level": profile.seniority_level,
        "skills": ", ".join(profile.skills[:5]) if profile.skills else "N/A",
        "industry": profile.industry or "Technology",
        "kb_data": kb_data,
        "search_data": search_data,
    })

    # Count data points
    data_points = _count_data_points(state)

    # Build final response
    salary_estimate = SalaryRange(
        currency="USD",
        min=analysis.salary_min,
        max=analysis.salary_max,
        median=analysis.salary_median,
    )

    confidence = ConfidenceInfo(
        score=analysis.confidence_score,
        level=analysis.confidence_level,
        data_points=data_points,
        factors=analysis.adjustments,
    )

    # Collect sources
    sources = ["internal_kb"] if state.get("kb_matches") else []
    search_sources = list(set(r.source for r in state.get("search_results", [])))
    sources.extend(search_sources[:5])

    # Build structured response
    final_response = EstimationResult(
        profile_summary={
            "title": profile.title,
            "company": profile.company,
            "years_of_experience": profile.years_of_experience,
            "location": profile.location,
        },
        salary_estimate=salary_estimate,
        confidence=confidence,
        reasoning=analysis.reasoning,
        sources=sources,
        adjustments=analysis.adjustments,
    ).model_dump()

    return {
        "salary_estimate": salary_estimate,
        "confidence_score": analysis.confidence_score,
        "reasoning": analysis.reasoning,
        "sources": sources,
        "adjustments": analysis.adjustments,
        "final_response": final_response,
    }
