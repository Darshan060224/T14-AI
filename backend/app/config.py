"""
T14 AI - Application Configuration

Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Ollama LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")

    # ChromaDB Configuration
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chromadb")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))

    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # Application Metadata
    APP_TITLE: str = os.getenv("APP_TITLE", "T14 AI - SOC Analyst Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = (
        "AI-Powered SOC Analyst Assistant using FastAPI, "
        "Qwen3 8B (Ollama), and RAG with ChromaDB"
    )

    # Collection name for ChromaDB
    COLLECTION_NAME: str = "security_knowledge"

    # Data directory for knowledge base
    DATA_DIR: str = os.getenv(
        "DATA_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    )


settings = Settings()
