"""
T14 AI - RAG Retriever

Retrieves relevant cybersecurity documents from the vector store
and formats them as context for the LLM prompt.
"""

import logging

from app.rag.vectorstore import query

logger = logging.getLogger(__name__)


def retrieve(
    query_text: str,
    n_results: int = 5
) -> tuple[str, list[str]]:
    """
    Retrieve relevant documents and format as LLM context.

    Args:
        query_text: The user's query or log text.
        n_results: Number of document chunks to retrieve.

    Returns:
        Tuple of (formatted_context, list_of_source_names).
    """
    results = query(query_text, n_results=n_results)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        logger.info("No relevant documents found for query")
        return "", []

    # Format context with source attribution
    context_parts = []
    sources = []

    for i, (doc, meta, dist) in enumerate(
        zip(documents, metadatas, distances)
    ):
        source = meta.get("source", "unknown")
        relevance = round(1 - dist, 3) if dist else 0

        context_parts.append(
            f"[Source {i + 1}: {source} | "
            f"Relevance: {relevance}]\n{doc}"
        )

        if source not in sources:
            sources.append(source)

    formatted_context = "\n\n---\n\n".join(context_parts)

    logger.info(
        "Retrieved %d relevant chunks from %d sources",
        len(documents), len(sources)
    )

    return formatted_context, sources
