"""Streamlit frontend for salary estimation."""

import streamlit as st

from salary_estimator.graph import estimate_salary
from salary_estimator.nodes.knowledge_base import init_knowledge_base


# Page config
st.set_page_config(
    page_title="Salary Estimator",
    page_icon="💰",
    layout="wide",
)

# Initialize knowledge base on first run
if "kb_initialized" not in st.session_state:
    init_knowledge_base()
    st.session_state.kb_initialized = True


# Example profiles for quick testing
EXAMPLE_PROFILES = {
    "Senior SWE at Google (SF)": """
John Smith
Senior Software Engineer at Google

San Francisco Bay Area

About:
Experienced software engineer with 7 years of experience building scalable distributed systems.
Currently working on Google Cloud Platform infrastructure.

Experience:
- Senior Software Engineer at Google (2021 - Present, 3 years)
  Working on GCP Compute Engine, Kubernetes integration, and cloud infrastructure.

- Software Engineer at Stripe (2019 - 2021, 2 years)
  Built payment processing systems and fraud detection pipelines.

- Software Engineer at Airbnb (2017 - 2019, 2 years)
  Developed search ranking algorithms and backend services.

Education:
- M.S. Computer Science, Stanford University
- B.S. Computer Science, UC Berkeley

Skills:
Python, Go, Java, Kubernetes, Distributed Systems, Machine Learning, AWS, GCP, System Design
""",
    "ML Engineer at Meta (NYC)": """
Sarah Chen
Machine Learning Engineer at Meta

New York, NY

About:
Machine Learning Engineer focused on recommendation systems and NLP.
5 years of experience in applied ML at scale.

Experience:
- Machine Learning Engineer at Meta (2022 - Present, 2 years)
  Building recommendation models for Instagram Reels.

- ML Engineer at Amazon (2020 - 2022, 2 years)
  Developed Alexa NLU models and speech recognition.

- Data Scientist at Bloomberg (2019 - 2020, 1 year)
  Financial NLP and sentiment analysis.

Education:
- Ph.D. Computer Science (Machine Learning), CMU

Skills:
Python, PyTorch, TensorFlow, NLP, Recommendation Systems, Deep Learning, Spark, SQL
""",
    "Junior Developer at Startup (Austin)": """
Mike Johnson
Software Developer at TechStartup Inc

Austin, TX

About:
Junior developer passionate about web development and learning new technologies.

Experience:
- Software Developer at TechStartup Inc (2023 - Present, 1 year)
  Full-stack development with React and Node.js.

- Intern at Local Agency (2022 - 2023, 6 months)
  Built marketing websites and landing pages.

Education:
- B.S. Computer Science, UT Austin

Skills:
JavaScript, React, Node.js, Python, SQL, Git, AWS basics
""",
}


def render_sidebar():
    """Render the sidebar with instructions and examples."""
    with st.sidebar:
        st.header("📋 How to Use")
        st.markdown("""
        1. Paste a LinkedIn profile text in the input area
        2. Click **Estimate Salary**
        3. View the detailed estimation results

        ---

        **What gets analyzed:**
        - Job title & company
        - Years of experience
        - Location
        - Skills & education
        - Company tier (FAANG, startup, etc.)
        """)

        st.header("🚀 Quick Examples")
        selected_example = st.selectbox(
            "Load an example profile:",
            ["-- Select --"] + list(EXAMPLE_PROFILES.keys()),
        )

        if selected_example != "-- Select --":
            st.session_state.profile_input = EXAMPLE_PROFILES[selected_example]
            st.rerun()

        st.markdown("---")
        st.caption("Powered by LangGraph + Google Gemini")


def render_results(result: dict):
    """Render the estimation results."""
    if not result:
        return

    # Profile summary
    profile = result.get("profile_summary", {})
    salary = result.get("salary_estimate", {})
    confidence = result.get("confidence", {})

    # Main metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💵 Median Salary",
            value=f"${salary.get('median', 0):,}",
            delta=f"Range: ${salary.get('min', 0):,} - ${salary.get('max', 0):,}",
        )

    with col2:
        conf_score = confidence.get("score", 0)
        conf_level = confidence.get("level", "unknown")
        emoji = "🟢" if conf_level == "high" else "🟡" if conf_level == "medium" else "🔴"
        st.metric(
            label=f"{emoji} Confidence",
            value=f"{conf_score:.0%}",
            delta=f"{conf_level.title()} ({confidence.get('data_points', 0)} data points)",
        )

    with col3:
        st.metric(
            label="🎯 Profile Match",
            value=profile.get("title", "N/A")[:25],
            delta=f"{profile.get('years_of_experience', 0)} years exp",
        )

    st.divider()

    # Detailed sections
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Salary Breakdown")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | **Minimum** | ${salary.get('min', 0):,} |
        | **Maximum** | ${salary.get('max', 0):,} |
        | **Median** | ${salary.get('median', 0):,} |
        | **Currency** | {salary.get('currency', 'USD')} |
        """)

        st.subheader("👤 Profile Summary")
        st.markdown(f"""
        - **Title:** {profile.get('title', 'N/A')}
        - **Company:** {profile.get('company', 'N/A')}
        - **Location:** {profile.get('location', 'N/A')}
        - **Experience:** {profile.get('years_of_experience', 0)} years
        """)

    with col_right:
        st.subheader("🔍 Analysis Reasoning")
        st.info(result.get("reasoning", "No reasoning provided."))

        st.subheader("⚙️ Adjustments Applied")
        adjustments = result.get("adjustments", [])
        if adjustments:
            for adj in adjustments:
                st.markdown(f"- {adj}")
        else:
            st.markdown("_No adjustments applied_")

        st.subheader("📚 Data Sources")
        sources = result.get("sources", [])
        if sources:
            st.markdown(", ".join(f"`{s}`" for s in sources))
        else:
            st.markdown("_No external sources used_")

    # Raw JSON expander
    with st.expander("🔧 View Raw JSON Response"):
        st.json(result)


def main():
    """Main Streamlit app."""
    st.title("💰 Salary Estimator")
    st.markdown("Estimate market salary from LinkedIn profile data using AI-powered analysis.")

    render_sidebar()

    # Initialize session state
    if "profile_input" not in st.session_state:
        st.session_state.profile_input = ""
    if "result" not in st.session_state:
        st.session_state.result = None

    # Input area
    st.subheader("📝 Enter LinkedIn Profile")

    profile_text = st.text_area(
        label="Paste the LinkedIn profile text here:",
        value=st.session_state.profile_input,
        height=300,
        placeholder="""Paste a LinkedIn profile here. Include:
- Name and current title
- Company name
- Location
- Work experience with dates
- Education
- Skills

Example:
John Smith
Senior Software Engineer at Google
San Francisco, CA
...""",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        estimate_button = st.button("🔮 Estimate Salary", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=False):
            st.session_state.profile_input = ""
            st.session_state.result = None
            st.rerun()

    # Run estimation
    if estimate_button:
        if not profile_text.strip():
            st.error("Please enter a LinkedIn profile to analyze.")
        else:
            with st.spinner("Analyzing profile and gathering market data..."):
                try:
                    result = estimate_salary(profile_text)
                    st.session_state.result = result
                    st.session_state.profile_input = profile_text
                except Exception as e:
                    st.error(f"Error during estimation: {str(e)}")
                    st.session_state.result = None

    # Display results
    if st.session_state.result:
        st.divider()
        st.subheader("📈 Estimation Results")
        render_results(st.session_state.result)


if __name__ == "__main__":
    main()
