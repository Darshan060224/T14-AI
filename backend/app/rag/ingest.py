"""
T14 AI - Document Ingestion Pipeline

Handles loading, chunking, and embedding cybersecurity documents
into the ChromaDB vector store for RAG retrieval.
"""

import hashlib
import logging
import os

from pypdf import PdfReader

from app.config import settings
from app.rag.vectorstore import add_documents, get_document_count

logger = logging.getLogger(__name__)


def _generate_chunk_id(source: str, chunk_index: int) -> str:
    """Generate a deterministic unique ID for a document chunk."""
    content = f"{source}::{chunk_index}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The full text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = settings.CHUNK_OVERLAP

    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence or paragraph boundary
        if end < len(text):
            # Look for paragraph break first
            break_pos = text.rfind("\n\n", start, end)
            if break_pos == -1 or break_pos <= start:
                # Look for sentence break
                break_pos = text.rfind(". ", start, end)
            if break_pos == -1 or break_pos <= start:
                # Look for any newline
                break_pos = text.rfind("\n", start, end)
            if break_pos > start:
                end = break_pos + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap
        if start >= len(text):
            break

    return chunks


def _load_txt(filepath: str) -> str:
    """Load a plain text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _load_pdf(filepath: str) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(filepath)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n\n".join(text_parts)


def _load_csv(filepath: str) -> str:
    """Load a CSV file as text (each row becomes a line)."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def load_document(filepath: str) -> str:
    """
    Load a document based on its file extension.

    Supports: .txt, .pdf, .csv, .md

    Args:
        filepath: Path to the document file.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If file format is not supported.
    """
    ext = os.path.splitext(filepath)[1].lower()

    loaders = {
        ".txt": _load_txt,
        ".md": _load_txt,
        ".pdf": _load_pdf,
        ".csv": _load_csv,
    }

    loader = loaders.get(ext)
    if loader is None:
        raise ValueError(
            f"Unsupported file format: {ext}. "
            f"Supported formats: {list(loaders.keys())}"
        )

    return loader(filepath)


def ingest_file(filepath: str) -> int:
    """
    Ingest a single file into the vector store.

    Args:
        filepath: Path to the document file.

    Returns:
        Number of chunks created.
    """
    filename = os.path.basename(filepath)
    logger.info("Ingesting file: %s", filename)

    # Load document text
    text = load_document(filepath)
    if not text.strip():
        logger.warning("Empty document: %s", filename)
        return 0

    # Split into chunks
    chunks = _chunk_text(text)
    logger.info("Created %d chunks from %s", len(chunks), filename)

    # Prepare metadata and IDs
    metadatas = [
        {
            "source": filename,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]
    ids = [
        _generate_chunk_id(filename, i)
        for i in range(len(chunks))
    ]

    # Add to vector store
    added = add_documents(texts=chunks, metadatas=metadatas, ids=ids)
    logger.info("Ingested %d chunks from %s", added, filename)

    return added


def ingest_directory(directory: str | None = None) -> int:
    """
    Ingest all supported documents from a directory (recursively).

    Args:
        directory: Path to the directory. Defaults to settings.DATA_DIR.

    Returns:
        Total number of chunks created across all files.
    """
    if directory is None:
        directory = settings.DATA_DIR

    if not os.path.exists(directory):
        logger.warning("Data directory not found: %s", directory)
        return 0

    supported_extensions = {".txt", ".md", ".pdf", ".csv"}
    total_chunks = 0

    for root, _dirs, files in os.walk(directory):
        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                filepath = os.path.join(root, filename)
                try:
                    chunks = ingest_file(filepath)
                    total_chunks += chunks
                except Exception as e:
                    logger.error(
                        "Failed to ingest %s: %s", filename, str(e)
                    )

    logger.info(
        "Ingestion complete: %d total chunks, %d docs in store",
        total_chunks, get_document_count()
    )
    return total_chunks


def ingest_uploaded_file(
    content: bytes,
    filename: str
) -> int:
    """
    Ingest an uploaded file from raw bytes.

    Args:
        content: Raw file content bytes.
        filename: Original filename (used for format detection).

    Returns:
        Number of chunks created.
    """
    import tempfile

    ext = os.path.splitext(filename)[1].lower()

    # Write to temporary file for processing
    with tempfile.NamedTemporaryFile(
        suffix=ext, delete=False, mode="wb"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return ingest_file(tmp_path)
    finally:
        os.unlink(tmp_path)
