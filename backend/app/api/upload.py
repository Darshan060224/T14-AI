"""
T14 AI - Document Upload API Route

Upload cybersecurity documents to the RAG knowledge base.
"""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import UploadResponse
from app.rag.ingest import ingest_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Knowledge Base"])

# Supported file types and max size (10 MB)
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".csv", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload-document",
    response_model=UploadResponse,
    summary="Upload Knowledge Base Document",
    description=(
        "Upload a cybersecurity document (PDF, TXT, CSV, MD) "
        "to the RAG knowledge base. The document will be chunked, "
        "embedded, and stored in the vector database for retrieval."
    )
)
async def upload_document(
    file: UploadFile = File(
        ...,
        description="Document file (PDF, TXT, CSV, or MD)"
    )
) -> UploadResponse:
    """
    Upload and ingest a document into the knowledge base.

    Supported formats: PDF, TXT, CSV, MD

    The document is:
    1. Parsed and text extracted
    2. Split into overlapping chunks (500 chars, 100 overlap)
    3. Embedded using sentence-transformers
    4. Stored in ChromaDB for RAG retrieval
    """
    # Validate file extension
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format: {ext}. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        )

    logger.info("Upload request: %s", filename)

    try:
        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"File too large ({len(content)} bytes). "
                    f"Maximum: {MAX_FILE_SIZE} bytes (10 MB)"
                )
            )

        # Ingest the document
        chunks_created = ingest_uploaded_file(content, filename)

        logger.info(
            "Document ingested: %s (%d chunks)", filename, chunks_created
        )

        return UploadResponse(
            filename=filename,
            chunks_created=chunks_created,
            status="ingested"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload error for %s: %s", filename, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(e)}"
        )
