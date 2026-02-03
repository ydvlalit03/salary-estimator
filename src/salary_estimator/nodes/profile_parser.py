"""Profile parser node using Gemini to extract structured data."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from salary_estimator.models import ProfileData
from salary_estimator.state import SalaryEstimationState
from salary_estimator.utils.config import get_config


PROFILE_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting structured information from LinkedIn profiles.
Given a LinkedIn profile (as text or semi-structured data), extract the following information:

1. **title**: Current job title/role (e.g., "Senior Software Engineer", "Product Manager")
2. **company**: Current company name
3. **company_tier**: Classify the company as one of: 'faang' (Google, Meta, Apple, Amazon, Netflix, Microsoft), 'tier1' (well-known tech companies like Stripe, Airbnb, Uber, etc.), 'tier2' (mid-size tech companies), 'startup', or 'unknown'
4. **years_of_experience**: Total years of professional experience (calculate from work history if needed)
5. **location**: Work location (city, state/country). If remote, note "Remote" but try to identify the person's base location too.
6. **skills**: List of key technical or professional skills (up to 10 most relevant)
7. **education**: Highest education level or notable degree (e.g., "BS Computer Science, Stanford")
8. **industry**: Industry sector (e.g., "Technology", "Finance", "Healthcare")
9. **seniority_level**: One of: 'entry' (0-2 years), 'mid' (2-5 years), 'senior' (5-8 years), 'staff' (8-12 years), 'principal' (12+ years), 'executive' (VP/C-level)

Be precise and extract only what's explicitly stated or can be reasonably inferred. For years of experience, sum up the durations of all positions listed."""),
    ("human", "Please extract structured information from this LinkedIn profile:\n\n{profile_text}")
])


def parse_profile(state: SalaryEstimationState) -> dict:
    """Parse raw LinkedIn profile text into structured ProfileData.

    This is a LangGraph node that takes the current state and returns
    updates to the state.
    """
    raw_profile = state.get("raw_profile", "")
    if not raw_profile:
        raise ValueError("No profile text provided in state")

    config = get_config()

    # Initialize Gemini with structured output
    llm = ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0,
    )

    # Use structured output to get ProfileData directly
    structured_llm = llm.with_structured_output(ProfileData)

    chain = PROFILE_EXTRACTION_PROMPT | structured_llm

    profile = chain.invoke({"profile_text": raw_profile})

    return {"profile": profile}
