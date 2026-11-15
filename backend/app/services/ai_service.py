"""
Unified AI service with pluggable providers.

Testing: Gemini (AIza key) for chat + embeddings, or Groq (gsk_ key) for chat only.
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


def gemini_key_usable() -> bool:
    key = (settings.GEMINI_API_KEY or "").strip()
    return key.startswith("AIza")


def llm_is_configured() -> bool:
    """True when the active chat provider can actually answer (not invalid Gemini keys)."""
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return gemini_key_usable()
    if provider == "groq":
        return bool((settings.GROQ_API_KEY or "").strip())
    if provider == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


def has_llm_provider() -> bool:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return bool(settings.GEMINI_API_KEY)
    if provider == "groq":
        return bool(settings.GROQ_API_KEY)
    if provider == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


def has_embedding_provider() -> bool:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return gemini_key_usable()
    if provider == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


async def _gemini_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    model_candidates = [
        settings.GEMINI_MODEL,
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]
    models: list[str] = []
    for m in model_candidates:
        if m and m not in models:
            models.append(m)

    payload_base = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_content}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=90) as client:
        for model in models:
            url = f"{GEMINI_BASE}/models/{model}:generateContent"
            try:
                response = await client.post(
                    url, params={"key": settings.GEMINI_API_KEY}, json=payload_base
                )
                if response.status_code >= 400:
                    errors.append(f"{model}: HTTP {response.status_code}")
                    continue
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    errors.append(f"{model}: no candidates")
                    continue
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    errors.append(f"{model}: empty content")
                    continue
                return parts[0]["text"]
            except httpx.HTTPStatusError as exc:
                errors.append(f"{model}: HTTP {exc.response.status_code}")
            except Exception as exc:
                errors.append(f"{model}: {exc}")

    raise RuntimeError(
        "Gemini chat failed. Use an AI Studio key (AIza…) from https://aistudio.google.com/apikey. "
        f"Details: {'; '.join(errors[:4])}"
    )


async def _anthropic_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    client = _get_claude_client()
    message = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


_groq_client: AsyncOpenAI | None = None


def _get_groq_client() -> AsyncOpenAI:
    global _groq_client
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not configured")
        _groq_client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    return _groq_client


async def _groq_generate(system_prompt: str, user_content: str, max_tokens: int) -> str:
    client = _get_groq_client()
    candidates = [
        settings.GROQ_MODEL,
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
    ]
    models: list[str] = []
    for m in candidates:
        if m and m not in models:
            models.append(m)

    errors: list[str] = []
    for model in models:
        try:
            response = await client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            errors.append(f"{model}: {exc}")

    raise RuntimeError(
        "Groq chat failed. Create a free key at https://console.groq.com/keys "
        f"Details: {'; '.join(errors[:3])}"
    )


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
    if provider == "groq":
        return await _groq_generate(system_prompt, user_content, max_tokens)
    if provider == "anthropic":
        return await _anthropic_generate(system_prompt, user_content, max_tokens)
    if provider == "openai":
        return await _openai_generate(system_prompt, user_content, max_tokens)
    raise RuntimeError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")


async def _gemini_embed(text_input: str) -> list[float]:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    model_candidates = [
        settings.GEMINI_EMBEDDING_MODEL,
        "text-embedding-004",
        "embedding-001",
        "gemini-embedding-001",
    ]
    models: list[str] = []
    for m in model_candidates:
        if m and m not in models:
            models.append(m)

    payload = {
        "content": {"parts": [{"text": text_input[:8000]}]},
    }
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=60) as client:
        for model in models:
            for api_version in ("v1beta", "v1"):
                url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model}:embedContent"
                body = {**payload, "model": f"models/{model}"}
                try:
                    response = await client.post(
                        url, params={"key": settings.GEMINI_API_KEY}, json=body
                    )
                    if response.status_code == 404:
                        errors.append(f"{model}@{api_version}: not found")
                        continue
                    response.raise_for_status()
                    data = response.json()
                    values = data.get("embedding", {}).get("values")
                    if values:
                        return values
                except httpx.HTTPStatusError as exc:
                    errors.append(f"{model}@{api_version}: HTTP {exc.response.status_code}")
                except Exception as exc:
                    errors.append(f"{model}@{api_version}: {exc}")

    hint = (
        "Use a Gemini API key from https://aistudio.google.com/apikey (usually starts with AIza). "
        "Vertex or other Google keys often return 404 on this endpoint."
    )
    raise RuntimeError(f"Gemini embedding failed ({'; '.join(errors[:3])}). {hint}")


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
