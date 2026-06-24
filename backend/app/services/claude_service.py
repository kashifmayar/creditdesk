"""Backward-compatible re-exports — use ai_service for new code."""

from app.services.ai_service import (
    generate_claude_response,
    generate_llm_response,
    get_embedding,
    has_embedding_provider,
    has_llm_provider,
)

__all__ = [
    "generate_claude_response",
    "generate_llm_response",
    "get_embedding",
    "has_embedding_provider",
    "has_llm_provider",
]
