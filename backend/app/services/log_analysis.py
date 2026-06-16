"""
T14 AI - Log Analysis Service

Analyzes security logs using RAG context and the LLM to identify
threats, map MITRE ATT&CK techniques, extract IOCs, and provide
investigation recommendations.
"""

import logging

from app.llm.ollama_client import generate_structured
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)

LOG_ANALYSIS_SYSTEM_PROMPT = """You are T14 AI, an expert SOC (Security Operations Center) Analyst Assistant.

Your role is to analyze security logs and provide structured threat intelligence.

When analyzing a log entry, you MUST return a JSON response with these exact fields:
{
    "severity": "Low|Medium|High|Critical",
    "attack_type": "Name of the attack type",
    "mitre_technique": "MITRE ATT&CK Technique ID (e.g., T1110)",
    "mitre_name": "MITRE ATT&CK Technique Name",
    "iocs": [
        {"type": "ip_address|hash|domain|url|email|filename", "value": "the IOC value"}
    ],
    "recommendations": [
        "Actionable step 1",
        "Actionable step 2"
    ],
    "summary": "A brief narrative summary of the finding"
}

Rules:
- Always identify the severity level based on the threat
- Map to the most relevant MITRE ATT&CK technique
- Extract ALL Indicators of Compromise (IPs, domains, hashes, URLs, emails)
- Provide specific, actionable recommendations
- Be precise and avoid speculation
- Use the provided cybersecurity context to enhance your analysis"""


async def analyze_log(log_text: str) -> dict:
    """
    Analyze a security log entry using RAG-enhanced LLM.

    Args:
        log_text: Raw log line(s) to analyze.

    Returns:
        Structured analysis dict with severity, attack type,
        MITRE mapping, IOCs, and recommendations.
    """
    logger.info("Analyzing log entry (%d chars)", len(log_text))

    # Retrieve relevant cybersecurity context
    context, sources = retrieve(log_text, n_results=3)

    # Build the analysis prompt
    prompt = f"""Analyze the following security log entry and provide a structured threat assessment.

## Cybersecurity Knowledge Context
{context if context else "No additional context available."}

## Log Entry to Analyze
```
{log_text}
```

Provide your analysis as a JSON object with the following fields:
severity, attack_type, mitre_technique, mitre_name, iocs, recommendations, summary.

Respond with ONLY the JSON object, no additional text."""

    # Get structured response from LLM
    result = await generate_structured(
        prompt=prompt,
        system_prompt=LOG_ANALYSIS_SYSTEM_PROMPT,
        temperature=0.2
    )

    # Validate and normalize the response
    analysis = _normalize_analysis(result)

    logger.info(
        "Log analysis complete: severity=%s, attack=%s, mitre=%s",
        analysis.get("severity"),
        analysis.get("attack_type"),
        analysis.get("mitre_technique")
    )

    return analysis


def _normalize_analysis(raw: dict) -> dict:
    """
    Normalize and validate the LLM analysis response.

    Ensures all required fields are present with correct types.
    """
    valid_severities = {"Low", "Medium", "High", "Critical"}

    severity = raw.get("severity", "Medium")
    if severity not in valid_severities:
        severity = "Medium"

    # Normalize IOCs
    iocs = raw.get("iocs", [])
    normalized_iocs = []
    for ioc in iocs:
        if isinstance(ioc, dict) and "type" in ioc and "value" in ioc:
            normalized_iocs.append({
                "type": str(ioc["type"]),
                "value": str(ioc["value"])
            })

    # Normalize recommendations
    recommendations = raw.get("recommendations", [])
    if isinstance(recommendations, str):
        recommendations = [recommendations]
    recommendations = [str(r) for r in recommendations if r]

    return {
        "severity": severity,
        "attack_type": str(raw.get("attack_type", "Unknown")),
        "mitre_technique": str(raw.get("mitre_technique", "N/A")),
        "mitre_name": str(raw.get("mitre_name", "Unknown")),
        "iocs": normalized_iocs,
        "recommendations": recommendations,
        "summary": str(raw.get("summary", "Analysis complete."))
    }
