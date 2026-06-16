"""
T14 AI - Ollama LLM Client

Async HTTP client for communicating with the Ollama API
to generate responses using Qwen3 8B.
"""

import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.7,
    model: str | None = None
) -> str:
    """
    Generate a text response from the Ollama LLM.

    Args:
        prompt: The user prompt to send to the model.
        system_prompt: Optional system prompt for role-setting.
        temperature: Sampling temperature (0.0 - 1.0).
        model: Model name override (defaults to settings).

    Returns:
        Generated text response from the LLM.

    Raises:
        httpx.HTTPError: If the Ollama API request fails.
    """
    if model is None:
        model = settings.OLLAMA_MODEL

    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    logger.info(
        "Sending request to Ollama (%s) - prompt length: %d chars",
        model, len(prompt)
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "").strip()

            logger.info(
                "Ollama response received - %d chars", len(answer)
            )
            return answer

        except httpx.ConnectError:
            logger.error(
                "Cannot connect to Ollama at %s. "
                "Is the Ollama service running?",
                settings.OLLAMA_BASE_URL
            )
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                "Ollama API error: %s %s",
                e.response.status_code, e.response.text
            )
            raise


async def generate_structured(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.3,
    model: str | None = None
) -> dict:
    """
    Generate a JSON-structured response from the Ollama LLM.

    The prompt should instruct the model to return valid JSON.
    Uses lower temperature for more deterministic structured output.

    Args:
        prompt: The user prompt (should request JSON output).
        system_prompt: Optional system prompt.
        temperature: Sampling temperature (lower = more deterministic).
        model: Model name override.

    Returns:
        Parsed JSON dict from the LLM response.
    """
    if model is None:
        model = settings.OLLAMA_MODEL

    url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    logger.info(
        "Sending structured request to Ollama (%s)", model
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "").strip()

            # Parse JSON response
            parsed = json.loads(answer)
            logger.info("Structured response parsed successfully")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse LLM JSON response: %s\nRaw: %s",
                str(e), answer[:500]
            )
            # Return a fallback structure
            return {
                "error": "Failed to parse structured response",
                "raw_response": answer
            }
        except httpx.ConnectError:
            logger.error(
                "Cannot connect to Ollama at %s",
                settings.OLLAMA_BASE_URL
            )
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                "Ollama API error: %s %s",
                e.response.status_code, e.response.text
            )
            raise


async def check_health() -> bool:
    """
    Check if Ollama is running and the model is available.

    Returns:
        True if Ollama is healthy, False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags"
            )
            response.raise_for_status()
            data = response.json()

            models = [
                m["name"] for m in data.get("models", [])
            ]
            model_available = any(
                settings.OLLAMA_MODEL in m for m in models
            )

            if not model_available:
                logger.warning(
                    "Model '%s' not found. Available: %s",
                    settings.OLLAMA_MODEL, models
                )

            return True
    except Exception as e:
        logger.error("Ollama health check failed: %s", str(e))
        return False
