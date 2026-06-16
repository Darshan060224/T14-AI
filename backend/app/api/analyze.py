"""
T14 AI - Log Analysis & Incident Summary API Routes

Endpoints for analyzing security logs and generating
incident summaries with MITRE ATT&CK mapping.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    IncidentSummary,
    IncidentSummaryRequest,
    LogAnalysis,
    LogRequest,
)
from app.services.log_analysis import analyze_log
from app.services.summary_generator import generate_summary

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze-log",
    response_model=LogAnalysis,
    summary="Analyze Security Log",
    description=(
        "Analyze a security log entry to identify threats, "
        "map MITRE ATT&CK techniques, extract IOCs, and "
        "provide investigation recommendations."
    )
)
async def analyze_log_endpoint(request: LogRequest) -> LogAnalysis:
    """
    Analyze a security log entry.

    Supports various log formats:
    - Windows Event Logs
    - Linux Syslogs
    - Firewall Logs
    - IDS/IPS Alerts
    - SIEM Alerts

    Returns structured analysis with severity, attack type,
    MITRE mapping, IOCs, and recommendations.
    """
    logger.info("Log analysis request (%d chars)", len(request.log))

    try:
        result = await analyze_log(request.log)

        return LogAnalysis(
            severity=result["severity"],
            attack_type=result["attack_type"],
            mitre_technique=result["mitre_technique"],
            mitre_name=result["mitre_name"],
            iocs=[
                {"type": ioc["type"], "value": ioc["value"]}
                for ioc in result.get("iocs", [])
            ],
            recommendations=result.get("recommendations", []),
            summary=result.get("summary", "Analysis complete.")
        )

    except Exception as e:
        logger.error("Log analysis error: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Analysis service error: {str(e)}"
        )


@router.post(
    "/incident-summary",
    response_model=IncidentSummary,
    summary="Generate Incident Summary",
    description=(
        "Generate a comprehensive executive incident summary "
        "from multiple security events. Includes affected assets, "
        "IOCs, timeline, and remediation recommendations."
    )
)
async def incident_summary_endpoint(
    request: IncidentSummaryRequest,
) -> IncidentSummary:
    """
    Generate an executive incident summary from multiple events.

    Input multiple security event log lines and receive a
    comprehensive incident report suitable for management review.
    """
    logger.info(
        "Incident summary request (%d events)", len(request.events)
    )

    try:
        result = await generate_summary(request.events)

        return IncidentSummary(
            executive_summary=result["executive_summary"],
            severity=result["severity"],
            affected_assets=result["affected_assets"],
            indicators=[
                {"type": ioc["type"], "value": ioc["value"]}
                for ioc in result.get("indicators", [])
            ],
            timeline=result["timeline"],
            recommendations=result["recommendations"]
        )

    except Exception as e:
        logger.error("Incident summary error: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Summary service error: {str(e)}"
        )
