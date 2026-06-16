"""
T14 AI - Incident Summary Generator

Takes multiple security events and generates a comprehensive
executive incident summary using RAG context and the LLM.
"""

import logging

from app.llm.ollama_client import generate_structured
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are T14 AI, a senior SOC analyst creating executive incident summaries.

Given multiple security events, generate a comprehensive incident summary report.

Return a JSON object with:
{
    "executive_summary": "A brief paragraph summarizing the incident",
    "severity": "Low|Medium|High|Critical",
    "affected_assets": ["list of affected systems, IPs, users"],
    "indicators": [
        {"type": "ip_address|hash|domain|url|email", "value": "the IOC"}
    ],
    "timeline": [
        "Event 1 description with timestamp",
        "Event 2 description with timestamp"
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ]
}

Rules:
- Provide a clear executive summary suitable for management
- Determine overall severity based on all events combined
- Extract and list all affected assets (IPs, hostnames, usernames)
- Extract all IOCs (IP addresses, hashes, domains, URLs)
- Create a chronological timeline of events
- Provide specific, actionable remediation steps
- Reference MITRE ATT&CK techniques where applicable"""


async def generate_summary(events: list[str]) -> dict:
    """
    Generate an executive incident summary from multiple events.

    Args:
        events: List of security event log lines.

    Returns:
        Structured incident summary dict.
    """
    logger.info("Generating incident summary for %d events", len(events))

    # Combine events for context retrieval
    combined_events = "\n".join(events[:20])  # Limit to 20 events

    # Retrieve relevant incident response context
    context, sources = retrieve(
        f"incident response {combined_events[:200]}",
        n_results=3
    )

    # Build the events section
    events_text = "\n".join(
        f"  [{i + 1}] {event}" for i, event in enumerate(events)
    )

    prompt = f"""Generate a comprehensive incident summary for the following security events.

## Cybersecurity Knowledge Context
{context if context else "No additional context available."}

## Security Events
{events_text}

Analyze all events together and provide a JSON incident summary with:
executive_summary, severity, affected_assets, indicators, timeline, recommendations.

Respond with ONLY the JSON object."""

    result = await generate_structured(
        prompt=prompt,
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        temperature=0.3
    )

    # Normalize response
    summary = _normalize_summary(result)

    logger.info(
        "Incident summary generated: severity=%s, %d assets, %d IOCs",
        summary.get("severity"),
        len(summary.get("affected_assets", [])),
        len(summary.get("indicators", []))
    )

    return summary


def _normalize_summary(raw: dict) -> dict:
    """Normalize and validate the incident summary response."""

    valid_severities = {"Low", "Medium", "High", "Critical"}

    severity = raw.get("severity", "Medium")
    if severity not in valid_severities:
        severity = "Medium"

    # Normalize indicators
    indicators = raw.get("indicators", [])
    normalized_indicators = []
    for ioc in indicators:
        if isinstance(ioc, dict) and "type" in ioc and "value" in ioc:
            normalized_indicators.append({
                "type": str(ioc["type"]),
                "value": str(ioc["value"])
            })

    # Normalize lists
    affected_assets = raw.get("affected_assets", [])
    if isinstance(affected_assets, str):
        affected_assets = [affected_assets]

    timeline = raw.get("timeline", [])
    if isinstance(timeline, str):
        timeline = [timeline]

    recommendations = raw.get("recommendations", [])
    if isinstance(recommendations, str):
        recommendations = [recommendations]

    return {
        "executive_summary": str(
            raw.get("executive_summary", "Incident summary unavailable.")
        ),
        "severity": severity,
        "affected_assets": [str(a) for a in affected_assets],
        "indicators": normalized_indicators,
        "timeline": [str(t) for t in timeline],
        "recommendations": [str(r) for r in recommendations]
    }
