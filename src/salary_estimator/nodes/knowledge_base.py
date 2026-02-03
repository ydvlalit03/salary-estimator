"""Knowledge base node using ChromaDB for salary benchmarks."""

import json
from pathlib import Path

import chromadb
from chromadb.config import Settings

from salary_estimator.models import ProfileData, SalaryBenchmark
from salary_estimator.state import SalaryEstimationState
from salary_estimator.utils.config import get_config


_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection."""
    global _client, _collection

    if _collection is not None:
        return _collection

    config = get_config()
    db_path = Path(config.chromadb_path)
    db_path.mkdir(parents=True, exist_ok=True)

    _client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False),
    )

    _collection = _client.get_or_create_collection(
        name="salary_benchmarks",
        metadata={"description": "Salary benchmark data for various roles and locations"},
    )

    return _collection


def init_knowledge_base(seed_data_path: str | None = None) -> int:
    """Initialize the knowledge base with seed data.

    Args:
        seed_data_path: Path to JSON file with seed data. If None, uses default.

    Returns:
        Number of records added.
    """
    collection = _get_collection()

    # Check if already populated
    if collection.count() > 0:
        return collection.count()

    # Load seed data
    if seed_data_path is None:
        seed_data_path = Path(__file__).parent.parent.parent.parent / "data" / "salary_benchmarks.json"
    else:
        seed_data_path = Path(seed_data_path)

    if not seed_data_path.exists():
        return 0

    with open(seed_data_path) as f:
        benchmarks = json.load(f)

    # Add to ChromaDB
    documents = []
    metadatas = []
    ids = []

    for i, benchmark in enumerate(benchmarks):
        # Create searchable document text
        doc = (
            f"{benchmark['role']} {benchmark['location']} "
            f"{benchmark['company_tier']} {benchmark['years_of_experience_min']}-"
            f"{benchmark['years_of_experience_max']} years"
        )
        documents.append(doc)
        metadatas.append(benchmark)
        ids.append(f"benchmark_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return len(benchmarks)


def lookup_knowledge_base(state: SalaryEstimationState) -> dict:
    """Query the knowledge base for relevant salary benchmarks.

    This is a LangGraph node that takes the current state and returns
    updates to the state.
    """
    profile = state.get("profile")
    if profile is None:
        return {"kb_matches": []}

    collection = _get_collection()

    # Ensure KB is initialized
    if collection.count() == 0:
        init_knowledge_base()

    # Build query from profile
    query_text = f"{profile.title} {profile.location} {profile.seniority_level}"

    # Query ChromaDB
    results = collection.query(
        query_texts=[query_text],
        n_results=10,
        include=["metadatas", "distances"],
    )

    # Convert to SalaryBenchmark objects and filter by experience
    kb_matches = []
    if results["metadatas"]:
        for metadata in results["metadatas"][0]:
            # Filter by years of experience if available
            yoe = profile.years_of_experience
            yoe_min = metadata.get("years_of_experience_min", 0)
            yoe_max = metadata.get("years_of_experience_max", 30)

            # Allow some flexibility in matching (within 2 years)
            if yoe_min - 2 <= yoe <= yoe_max + 2:
                kb_matches.append(SalaryBenchmark(**metadata))

    # Limit to top 5 most relevant
    kb_matches = kb_matches[:5]

    return {"kb_matches": kb_matches}
