"""
Unified AI service with pluggable providers.

Testing (default): Google Gemini free tier — one API key for chat + embeddings.
Production: set AI_PROVIDER=anthropic and EMBEDDING_PROVIDER=openai in .env.
"""

import logging

import anthropic
import httpx
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

_claude_client: anthropic.AsyncAnthropic | None = None
_openai_client: AsyncOpenAI | None = None


def _get_claude_client() -> anthropic.AsyncAnthropic:
    global _claude_client
    if _claude_client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        _claude_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _claude_client


def _get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def has_llm_provider() -> bool:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if provider == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


def has_embedding_provider() -> bool:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


async def _gemini_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    url = f"{GEMINI_BASE}/models/{settings.GEMINI_MODEL}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_content}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, params={"key": settings.GEMINI_API_KEY}, json=payload)
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise RuntimeError("Gemini returned empty content")
    return parts[0]["text"]


async def _anthropic_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    client = _get_claude_client()
    message = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


async def _openai_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    client = _get_openai_client()
    response = await client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or ""


async def generate_llm_response(
    system_prompt: str,
    user_content: str,
    max_tokens: int = 1000,
) -> str:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return await _gemini_generate(system_prompt, user_content, max_tokens)
    if provider == "anthropic":
        return await _anthropic_generate(system_prompt, user_content, max_tokens)
    if provider == "openai":
        return await _openai_generate(system_prompt, user_content, max_tokens)
    raise RuntimeError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")


async def _gemini_embed(text_input: str) -> list[float]:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    url = f"{GEMINI_BASE}/models/{settings.GEMINI_EMBEDDING_MODEL}:embedContent"
    payload = {
        "model": f"models/{settings.GEMINI_EMBEDDING_MODEL}",
        "content": {"parts": [{"text": text_input}]},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, params={"key": settings.GEMINI_API_KEY}, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["embedding"]["values"]


async def _openai_embed(text_input: str) -> list[float]:
    client = _get_openai_client()
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text_input,
    )
    return response.data[0].embedding


async def get_embedding(text_input: str) -> list[float]:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return await _gemini_embed(text_input)
    if provider == "openai":
        return await _openai_embed(text_input)
    raise RuntimeError(f"Unknown EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")


# Backward-compatible alias
generate_claude_response = generate_llm_response
