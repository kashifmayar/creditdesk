"""
RAG pipeline:
1. Upload PDF → extract text with PyMuPDF → chunk into ~500-token segments
2. Embed each chunk with Gemini/OpenAI embeddings → store in pgvector
3. On query: embed query → cosine similarity search → top-5 chunks → send to LLM
"""

import re

import fitz
from sqlalchemy import delete, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.policy_chunk import PolicyChunk
from app.services.ai_service import generate_llm_response, get_embedding, has_embedding_provider

SYSTEM_PROMPT = """You are a senior credit policy analyst assistant.
You have access to the institution's official credit policy manual.
Answer questions accurately and concisely. Always cite the relevant policy section
(e.g., "§4.2 – Collateral Requirements"). Keep answers under 150 words.
If the answer is not in the provided context, say so clearly.
Format: Answer first, then the section citation."""


def _has_embeddings() -> bool:
    return has_embedding_provider()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    step = max(chunk_size - overlap, 1)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def extract_section_title(chunk: str) -> str | None:
    match = re.search(r"§[\d.]+[^\n]*", chunk)
    return match.group(0).strip() if match else None


async def get_embedding_for_chunk(text_input: str) -> list[float]:
    return await get_embedding(text_input)


async def _keyword_retrieve(query: str, db: AsyncSession, top_k: int = 5) -> str:
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 3]
    if not words:
        result = await db.execute(
            select(PolicyChunk).order_by(PolicyChunk.chunk_index).limit(top_k)
        )
        chunks = result.scalars().all()
        return "\n\n".join(c.content for c in chunks) if chunks else "No policy document available."

    conditions = [PolicyChunk.content.ilike(f"%{w}%") for w in words[:5]]
    result = await db.execute(
        select(PolicyChunk).where(or_(*conditions)).limit(top_k)
    )
    chunks = result.scalars().all()
    if not chunks:
        result = await db.execute(
            select(PolicyChunk).order_by(PolicyChunk.chunk_index).limit(top_k)
        )
        chunks = result.scalars().all()
    return "\n\n".join(c.content for c in chunks)


async def ingest_pdf(file_bytes: bytes, db: AsyncSession) -> dict:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    chunks = chunk_text(full_text)
    if not chunks:
        return {"chunks_ingested": 0, "status": "empty_document"}

    await db.execute(delete(PolicyChunk))

    for i, chunk in enumerate(chunks):
        embedding = None
        if _has_embeddings():
            embedding = await get_embedding_for_chunk(chunk)
        db_chunk = PolicyChunk(
            content=chunk,
            chunk_index=i,
            section_title=extract_section_title(chunk),
            embedding=embedding,
        )
        db.add(db_chunk)

    await db.flush()
    return {"chunks_ingested": len(chunks), "status": "success"}


async def retrieve_context(query: str, db: AsyncSession, top_k: int = 5) -> str:
    if not _has_embeddings():
        return await _keyword_retrieve(query, db, top_k)

    query_embedding = await get_embedding(query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = text(
        """
        SELECT content, section_title
        FROM policy_chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:query_vec AS vector)
        LIMIT :top_k
        """
    )
    result = await db.execute(sql, {"query_vec": embedding_str, "top_k": top_k})
    rows = result.fetchall()

    if not rows:
        fallback = await db.execute(
            select(PolicyChunk).order_by(PolicyChunk.chunk_index).limit(top_k)
        )
        chunks = fallback.scalars().all()
        if not chunks:
            return "No policy document has been uploaded yet."
        return "\n\n".join(c.content for c in chunks)

    parts = []
    for row in rows:
        title = row.section_title or "Policy Section"
        parts.append(f"[{title}]\n{row.content}")
    return "\n\n".join(parts)


async def answer_policy_question(query: str, db: AsyncSession) -> dict:
    context = await retrieve_context(query, db)
    user_content = f"Policy context:\n{context}\n\nQuestion: {query}"

    try:
        answer = await generate_llm_response(SYSTEM_PROMPT, user_content)
    except RuntimeError:
        answer = _demo_answer(query, context)

    return {
        "answer": answer,
        "context_used": context[:500] + ("..." if len(context) > 500 else ""),
    }


def _demo_answer(query: str, context: str) -> str:
    section_match = re.search(r"§[\d.]+[^§\n]*", context)
    section = section_match.group(0).strip() if section_match else "Policy Manual"
    snippet = context[:300].strip()
    return (
        f"Based on the policy manual: {snippet}\n\n"
        f"[{section}]"
    )
