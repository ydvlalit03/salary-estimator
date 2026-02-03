"""Query generator node for creating smart Google search queries."""

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from salary_estimator.state import SalaryEstimationState
from salary_estimator.utils.config import get_config


class SearchQueries(BaseModel):
    """Generated search queries for salary research."""

    queries: list[str] = Field(
        description="List of Google search queries to find salary information",
        min_length=1,
        max_length=5,
    )


QUERY_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at crafting Google search queries to find accurate salary information.

Given a professional profile, generate 3-5 targeted search queries that will help find real salary data for this person's role.

Guidelines for query generation:
1. Include the job title, location, and current year (2024/2025)
2. Target known salary data sources: levels.fyi, glassdoor, linkedin salary, indeed salary, payscale
3. Include variations: exact title, similar titles, company-specific if it's a known company
4. Consider experience level adjustments (add "senior", "staff", etc. as appropriate)
5. For remote roles, also search for the base location if available

Example queries for a "Senior Software Engineer at Stripe in San Francisco":
- "Senior Software Engineer salary San Francisco 2024"
- "Stripe Senior Engineer compensation levels.fyi"
- "Senior SWE total compensation Bay Area"
- "Software Engineer L5 salary San Francisco glassdoor"
- "Senior Software Engineer Stripe salary 2024"

Generate queries that will return the most relevant and accurate salary data."""),
    ("human", """Generate search queries for this profile:

Title: {title}
Company: {company}
Company Tier: {company_tier}
Location: {location}
Years of Experience: {years_of_experience}
Seniority Level: {seniority_level}
Skills: {skills}
Industry: {industry}""")
])


def generate_queries(state: SalaryEstimationState) -> dict:
    """Generate smart Google search queries for salary research.

    This is a LangGraph node that takes the current state and returns
    updates to the state.
    """
    profile = state.get("profile")
    if profile is None:
        raise ValueError("No profile data available - run profile_parser first")

    config = get_config()

    llm = ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0.3,  # Slight creativity for query variation
    )

    structured_llm = llm.with_structured_output(SearchQueries)

    chain = QUERY_GENERATION_PROMPT | structured_llm

    result = chain.invoke({
        "title": profile.title,
        "company": profile.company,
        "company_tier": profile.company_tier,
        "location": profile.location,
        "years_of_experience": profile.years_of_experience,
        "seniority_level": profile.seniority_level,
        "skills": ", ".join(profile.skills[:5]) if profile.skills else "N/A",
        "industry": profile.industry or "Technology",
    })

    # Limit to configured max
    queries = result.queries[:config.max_search_queries]

    return {"search_queries": queries}
