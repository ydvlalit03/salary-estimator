"""Configuration management."""

import os
from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Config(BaseModel):
    """Application configuration."""

    google_api_key: str = Field(description="Google Gemini API key")
    google_cse_id: str = Field(description="Google Custom Search Engine ID")
    google_cse_api_key: str = Field(description="Google Custom Search API key")
    chromadb_path: str = Field(
        default="./data/chromadb", description="ChromaDB storage path"
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash", description="Gemini model to use"
    )
    max_search_queries: int = Field(
        default=5, description="Maximum search queries to generate"
    )
    max_search_results_per_query: int = Field(
        default=5, description="Max results per search query"
    )


@lru_cache
def get_config() -> Config:
    """Load and return configuration from environment."""
    load_dotenv()

    return Config(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        google_cse_id=os.getenv("GOOGLE_CSE_ID", ""),
        google_cse_api_key=os.getenv("GOOGLE_CSE_API_KEY", ""),
        chromadb_path=os.getenv("CHROMADB_PATH", "./data/chromadb"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    )
