"""
T14 AI - Chat API Route

RAG-enhanced security Q&A endpoint powered by Qwen3 8B.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.llm.ollama_client import generate
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

CHAT_SYSTEM_PROMPT = """You are T14 AI, an expert AI-powered SOC (Security Operations Center) Analyst Assistant.

Your responsibilities:
- Answer cybersecurity questions accurately and thoroughly
- Explain security concepts, attack techniques, and defense strategies
- Help analysts understand threats, vulnerabilities, and mitigations
- Reference MITRE ATT&CK framework when relevant
- Provide practical, actionable guidance

Rules:
- Be precise and technical, but explain clearly
- Always reference MITRE ATT&CK technique IDs when discussing attack techniques
- Suggest detection methods and defensive measures
- If provided with context from the knowledge base, use it to enhance your answer
- Acknowledge uncertainty when you're not sure about something
- Format your response with clear sections and bullet points when appropriate"""


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Security Chat Assistant",
    description=(
        "Ask cybersecurity questions. Uses RAG to retrieve "
        "relevant knowledge base documents and provides "
        "expert-level security guidance."
    )
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    RAG-enhanced security Q&A.

    The system retrieves relevant documents from the cybersecurity
    knowledge base, combines them with the user's question, and
    sends everything to Qwen3 8B for a comprehensive answer.
    """
    logger.info("Chat request: %s", request.question[:100])

    try:
        # Step 1: Retrieve relevant context from knowledge base
        context, sources = retrieve(request.question, n_results=5)

        # Step 2: Build the prompt with RAG context
        if context:
            prompt = f"""Use the following cybersecurity knowledge base context to answer the question.
If the context is relevant, incorporate it into your answer and cite the sources.
If the context is not relevant to the question, use your own knowledge.

## Knowledge Base Context
{context}

## Question
{request.question}

## Instructions
Provide a comprehensive, well-structured answer. Include:
- Clear explanation
- MITRE ATT&CK references if applicable
- Detection/mitigation recommendations if applicable
- Practical examples where helpful"""
        else:
            prompt = f"""Answer the following cybersecurity question using your expert knowledge.

## Question
{request.question}

## Instructions
Provide a comprehensive, well-structured answer. Include:
- Clear explanation
- MITRE ATT&CK references if applicable
- Detection/mitigation recommendations if applicable
- Practical examples where helpful"""

        # Step 3: Generate response from LLM
        answer = await generate(
            prompt=prompt,
            system_prompt=CHAT_SYSTEM_PROMPT,
            temperature=0.7
        )

        logger.info(
            "Chat response generated (%d chars, %d sources)",
            len(answer), len(sources)
        )

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        logger.error("Chat endpoint error: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail=f"LLM service error: {str(e)}"
        )
