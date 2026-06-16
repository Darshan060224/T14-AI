"""
T14 AI - Log Analysis Endpoint Tests

Tests for the /analyze-log endpoint with mocked dependencies.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


MOCK_ANALYSIS_RESULT = {
    "severity": "Medium",
    "attack_type": "Brute Force",
    "mitre_technique": "T1110",
    "mitre_name": "Brute Force",
    "iocs": [
        {"type": "ip_address", "value": "192.168.1.10"}
    ],
    "recommendations": [
        "Enable MFA for the targeted account",
        "Review login attempts from 192.168.1.10"
    ],
    "summary": "Multiple failed login attempts detected from 192.168.1.10"
}


@patch(
    "app.api.analyze.analyze_log",
    new_callable=AsyncMock,
    return_value=MOCK_ANALYSIS_RESULT
)
def test_analyze_log_returns_200(mock_analyze):
    """Test that /analyze-log returns HTTP 200."""
    response = client.post(
        "/analyze-log",
        json={
            "log": "Failed password for root from 192.168.1.10 port 22 ssh2"
        }
    )

    assert response.status_code == 200


@patch(
    "app.api.analyze.analyze_log",
    new_callable=AsyncMock,
    return_value=MOCK_ANALYSIS_RESULT
)
def test_analyze_log_response_structure(mock_analyze):
    """Test that /analyze-log returns correct structure."""
    response = client.post(
        "/analyze-log",
        json={
            "log": "Failed password for root from 192.168.1.10 port 22"
        }
    )
    data = response.json()

    assert "severity" in data
    assert "attack_type" in data
    assert "mitre_technique" in data
    assert "mitre_name" in data
    assert "iocs" in data
    assert "recommendations" in data
    assert "summary" in data


@patch(
    "app.api.analyze.analyze_log",
    new_callable=AsyncMock,
    return_value=MOCK_ANALYSIS_RESULT
)
def test_analyze_log_severity_values(mock_analyze):
    """Test that severity is a valid classification."""
    response = client.post(
        "/analyze-log",
        json={
            "log": "Failed password for root from 192.168.1.10 port 22"
        }
    )
    data = response.json()

    valid_severities = {"Low", "Medium", "High", "Critical"}
    assert data["severity"] in valid_severities


@patch(
    "app.api.analyze.analyze_log",
    new_callable=AsyncMock,
    return_value=MOCK_ANALYSIS_RESULT
)
def test_analyze_log_mitre_mapping(mock_analyze):
    """Test that MITRE technique is properly mapped."""
    response = client.post(
        "/analyze-log",
        json={
            "log": "Failed password for root from 192.168.1.10 port 22"
        }
    )
    data = response.json()

    assert data["mitre_technique"].startswith("T")
    assert data["mitre_name"] != ""


@patch(
    "app.api.analyze.analyze_log",
    new_callable=AsyncMock,
    return_value=MOCK_ANALYSIS_RESULT
)
def test_analyze_log_ioc_extraction(mock_analyze):
    """Test that IOCs are properly extracted."""
    response = client.post(
        "/analyze-log",
        json={
            "log": "Failed password for root from 192.168.1.10 port 22"
        }
    )
    data = response.json()

    assert len(data["iocs"]) > 0
    ioc = data["iocs"][0]
    assert "type" in ioc
    assert "value" in ioc


def test_analyze_log_rejects_short_input():
    """Test that /analyze-log rejects input that is too short."""
    response = client.post(
        "/analyze-log",
        json={"log": "Hi"}
    )

    assert response.status_code == 422


def test_analyze_log_rejects_empty_body():
    """Test that /analyze-log rejects empty requests."""
    response = client.post("/analyze-log", json={})

    assert response.status_code == 422
