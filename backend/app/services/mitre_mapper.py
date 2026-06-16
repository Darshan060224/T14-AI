"""
T14 AI - MITRE ATT&CK Mapper

Maps detected activities and threats to MITRE ATT&CK techniques
using RAG-enhanced lookup and LLM analysis.
"""

import logging

from app.llm.ollama_client import generate_structured
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)

MITRE_SYSTEM_PROMPT = """You are T14 AI, a cybersecurity expert specializing in MITRE ATT&CK framework mapping.

Given a description of an activity, threat, or security event, map it to the most relevant MITRE ATT&CK techniques.

Return a JSON object with:
{
    "techniques": [
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "description": "Brief description of the technique",
            "detection": "How to detect this technique",
            "mitigation": "How to mitigate this technique"
        }
    ],
    "confidence": "High|Medium|Low",
    "explanation": "Why these techniques were mapped"
}

Rules:
- Map to the most specific sub-technique when applicable (e.g., T1059.001 instead of T1059)
- Include the tactic category (Initial Access, Execution, Persistence, etc.)
- Provide practical detection and mitigation advice
- Use the provided context to improve accuracy"""


async def map_to_mitre(description: str) -> dict:
    """
    Map a security activity or threat to MITRE ATT&CK techniques.

    Args:
        description: Description of the activity, threat, or event.

    Returns:
        Dict with matched techniques, confidence, and explanation.
    """
    logger.info("Mapping to MITRE ATT&CK: %s", description[:100])

    # Retrieve MITRE-related context from knowledge base
    context, sources = retrieve(
        f"MITRE ATT&CK technique {description}",
        n_results=5
    )

    prompt = f"""Map the following activity to MITRE ATT&CK techniques.

## Cybersecurity Knowledge Context
{context if context else "No additional context available."}

## Activity to Map
{description}

Respond with ONLY a JSON object containing: techniques (array), confidence, explanation."""

    result = await generate_structured(
        prompt=prompt,
        system_prompt=MITRE_SYSTEM_PROMPT,
        temperature=0.2
    )

    # Normalize response
    techniques = result.get("techniques", [])
    if isinstance(techniques, dict):
        techniques = [techniques]

    normalized_techniques = []
    for tech in techniques:
        if isinstance(tech, dict):
            normalized_techniques.append({
                "technique_id": str(
                    tech.get("technique_id", "N/A")
                ),
                "technique_name": str(
                    tech.get("technique_name", "Unknown")
                ),
                "tactic": str(tech.get("tactic", "Unknown")),
                "description": str(
                    tech.get("description", "")
                ),
                "detection": str(tech.get("detection", "")),
                "mitigation": str(tech.get("mitigation", "")),
            })

    return {
        "techniques": normalized_techniques,
        "confidence": str(result.get("confidence", "Medium")),
        "explanation": str(result.get("explanation", "")),
        "sources": sources
    }
