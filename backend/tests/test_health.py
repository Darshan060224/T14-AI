"""
T14 AI - Health Endpoint Tests

Tests for the /health endpoint to verify the application
is running and responding correctly.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Test that /health returns HTTP 200."""
    with patch("app.main.get_document_count", return_value=0):
        response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that /health returns correct JSON structure."""
    with patch("app.main.get_document_count", return_value=42):
        response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "model" in data
    assert "rag_documents" in data


def test_health_check_status_running():
    """Test that /health reports status as 'running'."""
    with patch("app.main.get_document_count", return_value=0):
        response = client.get("/health")
    data = response.json()

    assert data["status"] == "running"


def test_health_check_model_configured():
    """Test that /health reports the configured model."""
    with patch("app.main.get_document_count", return_value=0):
        response = client.get("/health")
    data = response.json()

    assert data["model"] == "qwen3:8b"


def test_health_check_rag_document_count():
    """Test that /health reports correct RAG document count."""
    with patch("app.main.get_document_count", return_value=150):
        response = client.get("/health")
    data = response.json()

    assert data["rag_documents"] == 150
