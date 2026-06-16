"""
T14 AI - Chat Endpoint Tests

Tests for the /chat endpoint with mocked Ollama and ChromaDB.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.chat.retrieve")
@patch("app.api.chat.generate", new_callable=AsyncMock)
def test_chat_returns_200(mock_generate, mock_retrieve):
    """Test that /chat returns HTTP 200 with valid input."""
    mock_retrieve.return_value = (
        "MITRE T1110: Brute Force attack technique...",
        ["mitre_attack_techniques.txt"]
    )
    mock_generate.return_value = (
        "Pass-the-Hash is an attack technique where..."
    )

    response = client.post(
        "/chat",
        json={"question": "What is Pass-the-Hash?"}
    )

    assert response.status_code == 200


@patch("app.api.chat.retrieve")
@patch("app.api.chat.generate", new_callable=AsyncMock)
def test_chat_response_structure(mock_generate, mock_retrieve):
    """Test that /chat returns correct JSON structure."""
    mock_retrieve.return_value = ("context", ["source.txt"])
    mock_generate.return_value = "Test answer"

    response = client.post(
        "/chat",
        json={"question": "What is SQL injection?"}
    )
    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)


@patch("app.api.chat.retrieve")
@patch("app.api.chat.generate", new_callable=AsyncMock)
def test_chat_includes_rag_sources(mock_generate, mock_retrieve):
    """Test that /chat includes RAG source references."""
    mock_retrieve.return_value = (
        "Relevant context",
        ["mitre_attack_techniques.txt", "security_fundamentals.txt"]
    )
    mock_generate.return_value = "Detailed answer"

    response = client.post(
        "/chat",
        json={"question": "Explain MITRE T1110"}
    )
    data = response.json()

    assert len(data["sources"]) == 2
    assert "mitre_attack_techniques.txt" in data["sources"]


def test_chat_rejects_short_question():
    """Test that /chat rejects questions that are too short."""
    response = client.post(
        "/chat",
        json={"question": "Hi"}
    )

    assert response.status_code == 422  # Validation error


def test_chat_rejects_empty_body():
    """Test that /chat rejects requests with no body."""
    response = client.post("/chat", json={})

    assert response.status_code == 422


@patch("app.api.chat.retrieve")
@patch("app.api.chat.generate", new_callable=AsyncMock)
def test_chat_handles_no_rag_context(mock_generate, mock_retrieve):
    """Test that /chat works when RAG returns no results."""
    mock_retrieve.return_value = ("", [])
    mock_generate.return_value = "Answer without RAG context"

    response = client.post(
        "/chat",
        json={"question": "What is a zero-day exploit?"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["answer"] == "Answer without RAG context"
    assert data["sources"] == []
