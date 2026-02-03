"""LangGraph workflow for salary estimation."""

from langgraph.graph import StateGraph, START, END

from salary_estimator.state import SalaryEstimationState
from salary_estimator.nodes import (
    parse_profile,
    generate_queries,
    search_web,
    lookup_knowledge_base,
    analyze_salary,
)


def build_graph() -> StateGraph:
    """Build and return the salary estimation LangGraph workflow.

    The workflow follows this structure:
        START
          │
          ▼
    parse_profile
          │
          ▼
    generate_queries
          │
          ├──────────────┐
          ▼              ▼
     search_web    lookup_kb
          │              │
          └──────┬───────┘
                 ▼
          analyze_salary
                 │
                 ▼
               END
    """
    # Create the graph
    graph = StateGraph(SalaryEstimationState)

    # Add all nodes
    graph.add_node("parse_profile", parse_profile)
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_web", search_web)
    graph.add_node("lookup_kb", lookup_knowledge_base)
    graph.add_node("analyze_salary", analyze_salary)

    # Define the flow
    # START -> parse_profile
    graph.add_edge(START, "parse_profile")

    # parse_profile -> generate_queries
    graph.add_edge("parse_profile", "generate_queries")

    # generate_queries -> parallel (search_web, lookup_kb)
    graph.add_edge("generate_queries", "search_web")
    graph.add_edge("generate_queries", "lookup_kb")

    # Both parallel nodes -> analyze_salary
    graph.add_edge("search_web", "analyze_salary")
    graph.add_edge("lookup_kb", "analyze_salary")

    # analyze_salary -> END
    graph.add_edge("analyze_salary", END)

    return graph


def compile_graph():
    """Compile and return the runnable graph."""
    graph = build_graph()
    return graph.compile()


# Create a singleton compiled graph for reuse
_compiled_graph = None


def get_graph():
    """Get or create the compiled graph singleton."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = compile_graph()
    return _compiled_graph


def estimate_salary(profile_text: str) -> dict:
    """Run the salary estimation workflow.

    Args:
        profile_text: Raw LinkedIn profile text or structured profile data.

    Returns:
        Dictionary containing the estimation result with salary range,
        confidence score, reasoning, and sources.
    """
    graph = get_graph()

    initial_state = {"raw_profile": profile_text}

    # Run the graph
    final_state = graph.invoke(initial_state)

    return final_state.get("final_response", {})
