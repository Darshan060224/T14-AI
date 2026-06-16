"""
T14 AI - ChromaDB Vector Store

Manages the ChromaDB connection and provides methods for storing
and querying document embeddings for the RAG pipeline.
"""

import logging
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

# Global instances (initialized during app startup)
_chroma_client = None
_collection = None
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the sentence transformer embedding model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(
            "Loading embedding model: %s", settings.EMBEDDING_MODEL
        )
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _embedding_model


def get_chroma_client() -> chromadb.HttpClient:
    """Get or initialize the ChromaDB HTTP client."""
    global _chroma_client
    if _chroma_client is None:
        logger.info(
            "Connecting to ChromaDB at %s:%s",
            settings.CHROMA_HOST, settings.CHROMA_PORT
        )
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        logger.info("ChromaDB connection established")
    return _chroma_client


def get_collection() -> chromadb.Collection:
    """Get or create the security knowledge collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "T14 AI Security Knowledge Base"}
        )
        logger.info(
            "Collection '%s' ready with %d documents",
            settings.COLLECTION_NAME, _collection.count()
        )
    return _collection


def add_documents(
    texts: list[str],
    metadatas: list[dict],
    ids: list[str]
) -> int:
    """
    Add document chunks to the vector store.

    Args:
        texts: List of text chunks to embed and store.
        metadatas: List of metadata dicts for each chunk.
        ids: List of unique IDs for each chunk.

    Returns:
        Number of chunks added.
    """
    collection = get_collection()
    model = get_embedding_model()

    # Generate embeddings
    embeddings = model.encode(texts).tolist()

    # Add to ChromaDB in batches
    batch_size = 100
    total_added = 0

    for i in range(0, len(texts), batch_size):
        end = min(i + batch_size, len(texts))
        collection.add(
            documents=texts[i:end],
            embeddings=embeddings[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )
        total_added += (end - i)
        logger.info("Added batch %d-%d (%d chunks)", i, end, end - i)

    logger.info("Total documents in collection: %d", collection.count())
    return total_added


def query(query_text: str, n_results: int | None = None) -> dict:
    """
    Query the vector store for relevant document chunks.

    Args:
        query_text: The search query text.
        n_results: Number of results to return (default from settings).

    Returns:
        ChromaDB query results dict with documents, metadatas,
        and distances.
    """
    if n_results is None:
        n_results = settings.TOP_K_RESULTS

    collection = get_collection()
    model = get_embedding_model()

    # Generate query embedding
    query_embedding = model.encode([query_text]).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results


def get_document_count() -> int:
    """Get the total number of document chunks in the vector store."""
    try:
        collection = get_collection()
        return collection.count()
    except Exception:
        return 0


def reset_collection():
    """Delete and recreate the collection (useful for re-ingestion)."""
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(settings.COLLECTION_NAME)
        logger.info("Deleted collection '%s'", settings.COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
    get_collection()
