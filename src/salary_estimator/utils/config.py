"""Configuration management."""

import os
from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv


def _get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets or environment."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


class Config(BaseModel):
    """Application configuration."""

    google_api_key: str = Field(description="Google Gemini API key")
    google_cse_id: str = Field(description="Google Custom Search Engine ID")
    google_cse_api_key: str = Field(description="Google Custom Search API key")
    chromadb_path: str = Field(
        default="./data/chromadb", description="ChromaDB storage path"
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash", description="Gemini model to use"
    )
    max_search_queries: int = Field(
        default=5, description="Maximum search queries to generate"
    )
    max_search_results_per_query: int = Field(
        default=5, description="Max results per search query"
    )


@lru_cache
def get_config() -> Config:
    """Load and return configuration from Streamlit secrets or environment."""
    load_dotenv()

    return Config(
        google_api_key=_get_secret("GOOGLE_API_KEY"),
        google_cse_id=_get_secret("GOOGLE_CSE_ID"),
        google_cse_api_key=_get_secret("GOOGLE_CSE_API_KEY"),
        chromadb_path=_get_secret("CHROMADB_PATH", "./data/chromadb"),
        gemini_model=_get_secret("GEMINI_MODEL", "gemini-2.5-flash"),
    )
