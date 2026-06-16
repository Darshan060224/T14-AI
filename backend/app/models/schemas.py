"""
T14 AI - Pydantic Data Models

Request and response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field


# ─── Health Check ──────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model: str
    rag_documents: int = Field(
        ...,
        description="Number of document chunks in the vector store"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "running",
                "model": "qwen3:8b",
                "rag_documents": 150
            }]
        }
    }


# ─── Chat / Security Q&A ──────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for the security chat endpoint."""
    question: str = Field(
        ...,
        min_length=3,
        description="Cybersecurity question to ask"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "question": "What is Pass-the-Hash and how do I detect it?"
            }]
        }
    }


class ChatResponse(BaseModel):
    """Response from the security chat endpoint."""
    answer: str = Field(
        ...,
        description="AI-generated answer using RAG context"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Source documents used for the answer"
    )


# ─── Log Analysis ─────────────────────────────────────────

class LogRequest(BaseModel):
    """Request body for log analysis endpoint."""
    log: str = Field(
        ...,
        min_length=5,
        description="Raw security log entry to analyze"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "log": "Jun 15 10:23:01 server sshd[12345]: Failed password for root from 192.168.1.10 port 22 ssh2"
            }]
        }
    }


class IOCDetail(BaseModel):
    """Individual Indicator of Compromise."""
    type: str = Field(..., description="IOC type")
    value: str = Field(..., description="IOC value")


class LogAnalysis(BaseModel):
    """Structured log analysis response."""
    severity: str = Field(
        ...,
        description="Threat severity: Low, Medium, High, Critical"
    )
    attack_type: str = Field(
        ...,
        description="Identified attack category"
    )
    mitre_technique: str = Field(
        ...,
        description="MITRE ATT&CK Technique ID"
    )
    mitre_name: str = Field(
        ...,
        description="MITRE ATT&CK Technique Name"
    )
    iocs: list[IOCDetail] = Field(
        default_factory=list,
        description="Extracted Indicators of Compromise"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommended investigation and mitigation steps"
    )
    summary: str = Field(
        ...,
        description="Brief narrative summary of the finding"
    )


# ─── Document Upload ──────────────────────────────────────

class UploadResponse(BaseModel):
    """Response after uploading a knowledge base document."""
    filename: str
    chunks_created: int = Field(
        ...,
        description="Number of text chunks created and embedded"
    )
    status: str


# ─── Incident Summary ─────────────────────────────────────

class IncidentSummaryRequest(BaseModel):
    """Request body for incident summarization."""
    events: list[str] = Field(
        ...,
        min_length=1,
        description="List of security event log lines"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "events": [
                    "Failed password for root from 192.168.1.10",
                    "Accepted password for admin from 10.0.0.5",
                    "PowerShell -enc detected in process logs"
                ]
            }]
        }
    }


class IncidentSummary(BaseModel):
    """Structured incident summary response."""
    executive_summary: str
    severity: str
    affected_assets: list[str]
    indicators: list[IOCDetail]
    timeline: list[str]
    recommendations: list[str]
