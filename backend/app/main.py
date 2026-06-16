"""
T14 AI - Main Application

AI-Powered SOC Analyst Assistant using FastAPI, Qwen3 8B (Ollama),
and RAG with ChromaDB.

Endpoints:
    GET  /health           - Health check
    POST /chat             - Security Q&A (RAG-enhanced)
    POST /analyze-log      - Log analysis with MITRE mapping
    POST /incident-summary - Executive incident summary
    POST /upload-document  - Upload knowledge base documents
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.analyze import router as analyze_router
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.config import settings
from app.models.schemas import HealthResponse
from app.rag.ingest import ingest_directory
from app.rag.vectorstore import get_document_count, get_embedding_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Preload the embedding model
    - Ingest knowledge base documents from data/ directory

    Shutdown:
    - Cleanup resources
    """
    logger.info("=" * 60)
    logger.info("T14 AI - Starting up...")
    logger.info("=" * 60)

    # Preload embedding model (avoid cold start on first request)
    logger.info("Preloading embedding model: %s", settings.EMBEDDING_MODEL)
    try:
        get_embedding_model()
        logger.info("Embedding model loaded successfully")
    except Exception as e:
        logger.error("Failed to load embedding model: %s", str(e))

    # Ingest knowledge base documents
    logger.info("Ingesting knowledge base from: %s", settings.DATA_DIR)
    try:
        total_chunks = ingest_directory()
        logger.info(
            "Knowledge base ready: %d chunks ingested", total_chunks
        )
    except Exception as e:
        logger.error("Knowledge base ingestion failed: %s", str(e))
        logger.info("The app will still run, but RAG context may be limited")

    logger.info("=" * 60)
    logger.info("T14 AI - Ready to serve!")
    logger.info("Swagger UI: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("T14 AI - Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)
app.include_router(analyze_router)
app.include_router(upload_router)

# Serve static files (CSS, JS) — works in both Docker and local dev
_app_root = os.path.dirname(os.path.dirname(__file__))
static_dir = os.path.join(_app_root, "static")  # Docker: /app/static
if not os.path.exists(static_dir):
    # Local dev: backend/app/../../frontend
    static_dir = os.path.join(_app_root, "..", "frontend")
    static_dir = os.path.abspath(static_dir)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Check the health status of the T14 AI application."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the application status, configured LLM model,
    and number of documents in the RAG knowledge base.
    """
    doc_count = get_document_count()

    return HealthResponse(
        status="running",
        model=settings.OLLAMA_MODEL,
        rag_documents=doc_count
    )


@app.get("/", include_in_schema=False)
async def serve_ui():
    """Serve the T14 AI web interface."""
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
