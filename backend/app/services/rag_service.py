"""
RAG pipeline:
1. Upload PDF → extract text with PyMuPDF → chunk into ~500-token segments
2. Embed each chunk with Gemini/OpenAI embeddings → store in pgvector
3. On query: embed query → cosine similarity search → top-5 chunks → send to LLM
"""

import hashlib
import logging
import re

import fitz
from sqlalchemy import delete, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.policy_chunk import PolicyChunk
from app.models.policy_document import PolicyDocument
from app.services.ai_service import (
    generate_llm_response,
    get_embedding,
    has_embedding_provider,
    llm_is_configured,
)

logger = logging.getLogger(__name__)

STOPWORDS = frozenset(
    """
    a an the and or for to of in on at with from by is are was were be been being
    this that these those it its as if when what which who how why can could should
    would will do does did has have had into about your our any all
    """.split()
)

QUERY_EXPANSIONS: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"\bltv\b", re.I), ["ltv", "loan to value", "loan-to-value", "lcr", "loan to collateral"]),
    (re.compile(r"\bcommercial\b", re.I), ["commercial"]),
    (re.compile(r"\bgrace\s+period\b", re.I), ["grace period", "grace", "late payment", "overdue", "arrears"]),
    (re.compile(r"\blate\s+payment", re.I), ["late payment", "grace", "penalty", "overdue"]),
    (re.compile(r"\bescalat", re.I), ["escalat", "credit committee", "committee", "approving authority"]),
    (re.compile(r"\bcredit\s+committee\b", re.I), ["credit committee", "committee", "approving authority"]),
    (re.compile(r"\brisk\s+premium\b", re.I), ["risk premium", "margin", "spread", "premium"]),
    (re.compile(r"\bsecurit", re.I), ["securit", "collateral", "non-liquid", "margin"]),
    (re.compile(r"\bcollateral\b", re.I), ["collateral", "security", "mortgage", "charge"]),
    (re.compile(r"\brestructur", re.I), ["restructur", "reschedul", "refinanc"]),
    (re.compile(r"\bmaximum\b|\bminimum\b|\bmax\b|\bmin\b", re.I), []),
    (re.compile(r"risk\s*based\s*pric", re.I), ["risk based pricing", "rbp", "markup framework"]),
    (re.compile(r"\bpricing\b", re.I), ["pricing", "markup", "margin", "spread"]),
    (re.compile(r"\bfol\b|facility\s+offer", re.I), ["fol", "facility offer letter"]),
]

COMMON_POLICY_WORDS = frozenset(
    {
        "risk",
        "based",
        "credit",
        "loan",
        "bank",
        "facility",
        "framework",
        "policy",
        "section",
        "manual",
        "procedure",
        "requirements",
        "including",
    }
)

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
    for pattern in (
        r"§[\d.]+[^\n]*",
        r"\bSection\s+[IVXLC\d]+[^\n]{0,80}",
        r"\b\d+\.\d+(?:\.\d+)?\s+[A-Z][^\n]{3,80}",
    ):
        match = re.search(pattern, chunk)
        if match:
            return match.group(0).strip()
    first_line = chunk.strip().split("\n", 1)[0].strip()
    if 8 < len(first_line) < 120:
        return first_line
    return None


def _query_phrases(query: str) -> list[str]:
    words = [
        w.lower()
        for w in re.findall(r"\w+", query)
        if len(w) > 2 and w.lower() not in STOPWORDS
    ]
    phrases: list[str] = []
    for n in range(min(5, len(words)), 1, -1):
        for i in range(len(words) - n + 1):
            phrases.append(" ".join(words[i : i + n]))
    phrases.sort(key=len, reverse=True)
    unique: list[str] = []
    for p in phrases:
        if p not in unique:
            unique.append(p)
    return unique[:10]


def expand_search_terms(query: str) -> list[str]:
    terms: list[str] = []
    for phrase in _query_phrases(query):
        terms.append(phrase)
    for word in re.findall(r"\w+", query.lower()):
        if len(word) > 2 and word not in STOPWORDS and word not in terms:
            terms.append(word)
    for pattern, extra in QUERY_EXPANSIONS:
        if pattern.search(query):
            for item in extra:
                if item not in terms:
                    terms.append(item)
    if re.search(r"\b(maximum|minimum|max|min)\b", query, re.I):
        for w in ("maximum", "minimum", "percent", "%", "ratio", "margin"):
            if w not in terms:
                terms.append(w)
    return terms[:24]


def _distinctive_terms(terms: list[str]) -> list[str]:
    out: list[str] = []
    for t in terms:
        if " " in t and len(t) > 6:
            out.append(t)
        elif t not in COMMON_POLICY_WORDS and len(t) > 3:
            out.append(t)
    return out or terms[:3]


def _toc_penalty(text: str) -> int:
    low = text.lower()
    penalty = 0
    if "table of contents" in low:
        penalty += 50
    if low.count("credit procedures manual") >= 3:
        penalty += 35
    if re.search(r"\bs\.n\b.*page", low):
        penalty += 30
    page_refs = len(re.findall(r"\bpage\s+\d+\b", low))
    section_refs = len(re.findall(r"\bsection\s+[ivxlc\d]+", low))
    if page_refs >= 4 and section_refs >= 3:
        penalty += 25
    return penalty


def score_chunk_content(content: str, terms: list[str], query: str) -> int:
    low = content.lower()
    q_low = query.lower().strip()
    score = 0
    if len(q_low) > 8 and q_low in low:
        score += 60
    for phrase in _query_phrases(query):
        if len(phrase) > 8 and phrase in low:
            score += 25
    for term in terms:
        if " " in term:
            score += low.count(term) * 8
        elif term in low:
            score += 1 if term in COMMON_POLICY_WORDS else 4
    if re.search(r"\b(maximum|minimum|least|not exceed)\b", query, re.I):
        if re.search(r"\d+\s*%|\d+\.\d+\s*%|%\s|percent", content, re.I):
            score += 8
    if re.search(r"\bcommittee|escalat", query, re.I) and "committee" in low:
        score += 6
    if re.search(r"risk\s*based\s*pric", query, re.I):
        if re.search(r"risk\s*based\s*pric|\brbp\b", low):
            score += 20
        if "fol coverage" in low and "risk based" not in low:
            score -= 12
    score -= _toc_penalty(content)
    return score


def _clean_policy_excerpt(text: str) -> str:
    text = re.sub(
        r"(Credit Procedures Manual\s*\(CPM\)\s*RMG\s*)+",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _sentences_from_text(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


async def _chunks_have_embeddings(db: AsyncSession) -> bool:
    result = await db.execute(
        select(PolicyChunk.id).where(PolicyChunk.embedding.isnot(None)).limit(1)
    )
    return result.first() is not None


async def get_embedding_for_chunk(text_input: str) -> list[float]:
    return await get_embedding(text_input)


async def _ranked_chunks(
    query: str, db: AsyncSession, top_k: int = 5
) -> list[PolicyChunk]:
    terms = expand_search_terms(query)
    result = await db.execute(select(PolicyChunk))
    all_chunks = result.scalars().all()
    if not all_chunks:
        return []

    if not terms:
        return all_chunks[:top_k]

    scored: list[tuple[int, PolicyChunk]] = []
    for chunk in all_chunks:
        s = score_chunk_content(chunk.content, terms, query)
        if s > 0:
            scored.append((s, chunk))

    scored.sort(key=lambda x: (-x[0], x[1].chunk_index))
    if scored:
        return [c for _, c in scored[:top_k]]

    # Fallback: any term match with relaxed OR filter
    conditions = [PolicyChunk.content.ilike(f"%{t}%") for t in terms[:8]]
    if conditions:
        result = await db.execute(select(PolicyChunk).where(or_(*conditions)))
        relaxed = result.scalars().all()
        rescored = [
            (score_chunk_content(c.content, terms, query), c) for c in relaxed
        ]
        rescored.sort(key=lambda x: (-x[0], x[1].chunk_index))
        if rescored and rescored[0][0] > -30:
            return [c for _, c in rescored[:top_k]]

    skip_front = max(0, min(15, len(all_chunks) // 10))
    return all_chunks[skip_front : skip_front + top_k]


async def _keyword_retrieve(query: str, db: AsyncSession, top_k: int = 5) -> str:
    chunks = await _ranked_chunks(query, db, top_k)
    if not chunks:
        return "No policy document available."

    parts = []
    for c in chunks:
        title = c.section_title or extract_section_title(c.content) or "Policy section"
        parts.append(f"[{title}]\n{c.content}")
    return "\n\n".join(parts)


async def ingest_pdf(
    file_bytes: bytes,
    db: AsyncSession,
    filename: str = "policy.pdf",
) -> dict:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = doc.page_count
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    chunks = chunk_text(full_text)
    if not chunks:
        return {"chunks_ingested": 0, "status": "empty_document", "filename": filename}

    sha = hashlib.sha256(file_bytes).hexdigest()
    await db.execute(update(PolicyDocument).values(is_active=False))
    await db.execute(delete(PolicyChunk))

    embedded_count = 0
    policy_doc = PolicyDocument(
        filename=filename,
        sha256=sha,
        file_data=file_bytes,
        pages=page_count,
        chunk_count=len(chunks),
        embedded_count=0,
        is_active=True,
    )
    db.add(policy_doc)
    await db.flush()

    for i, chunk in enumerate(chunks):
        embedding = None
        if _has_embeddings():
            try:
                embedding = await get_embedding_for_chunk(chunk)
                embedded_count += 1
            except Exception as exc:
                logger.warning("Chunk %s embedding skipped: %s", i, exc)
        db.add(
            PolicyChunk(
                policy_document_id=policy_doc.id,
                content=chunk,
                chunk_index=i,
                section_title=extract_section_title(chunk),
                embedding=embedding,
            )
        )

    policy_doc.embedded_count = embedded_count
    policy_doc.chunk_count = len(chunks)
    await db.flush()
    return {
        "chunks_ingested": len(chunks),
        "status": "success",
        "filename": filename,
        "pages": page_count,
        "sha256": sha,
    }


async def get_policy_status(db: AsyncSession) -> dict:
    result = await db.execute(
        select(PolicyDocument)
        .where(PolicyDocument.is_active.is_(True))
        .order_by(PolicyDocument.ingested_at.desc())
        .limit(1)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        chunk_count = await db.execute(select(PolicyChunk.id).limit(1))
        has_seed = chunk_count.first() is not None
        return {
            "loaded": has_seed,
            "filename": "Sample seeded policy" if has_seed else None,
            "pages": None,
            "chunks_ingested": None,
            "embedded_chunks": 0,
            "ingested_at": None,
            "ai_key_format_ok": llm_is_configured(),
        }
    return {
        "loaded": True,
        "filename": doc.filename,
        "pages": doc.pages,
        "chunks_ingested": doc.chunk_count,
        "embedded_chunks": doc.embedded_count or 0,
        "ingested_at": doc.ingested_at.isoformat() if doc.ingested_at else None,
        "ai_key_format_ok": llm_is_configured(),
    }


async def retrieve_context(query: str, db: AsyncSession, top_k: int = 5) -> str:
    use_vectors = _has_embeddings() and await _chunks_have_embeddings(db)
    if not use_vectors:
        return await _keyword_retrieve(query, db, top_k)

    try:
        query_embedding = await get_embedding(query)
    except Exception as exc:
        logger.warning("Query embedding failed, using keyword search: %s", exc)
        return await _keyword_retrieve(query, db, top_k)

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    try:
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
    except Exception as exc:
        logger.warning("Vector search failed, using keyword search: %s", exc)
        return await _keyword_retrieve(query, db, top_k)

    if not rows:
        return await _keyword_retrieve(query, db, top_k)

    parts = []
    for row in rows:
        title = row.section_title or "Policy Section"
        parts.append(f"[{title}]\n{row.content}")
    return "\n\n".join(parts)


def _trim_context_for_provider(context: str) -> str:
    """Keep Groq free-tier requests within practical token limits (single user)."""
    provider = settings.AI_PROVIDER.lower()
    limit = 12_000 if provider == "groq" else 36_000
    if len(context) <= limit:
        return context
    return context[:limit] + "\n\n[…additional policy text omitted for API limits]"


async def answer_policy_question(query: str, db: AsyncSession) -> dict:
    top_k = 4 if settings.AI_PROVIDER.lower() == "groq" else 8
    context = _trim_context_for_provider(await retrieve_context(query, db, top_k=top_k))
    user_content = f"Policy context:\n{context}\n\nQuestion: {query}"
    answer_mode = "ai"

    try:
        answer = await generate_llm_response(SYSTEM_PROMPT, user_content)
    except Exception as exc:
        logger.warning("LLM generation failed, using local excerpt answer: %s", exc)
        answer_mode = "excerpt"
        answer = _local_answer_from_context(query, context)

    return {
        "answer": answer,
        "context_used": context[:500] + ("..." if len(context) > 500 else ""),
        "answer_mode": answer_mode,
    }


def _local_answer_from_context(query: str, context: str) -> str:
    if not context or context.startswith("No policy"):
        return (
            "I could not find this topic in the loaded policy. "
            "Upload the credit procedure manual (PDF) and try again."
        )

    terms = expand_search_terms(query)
    blocks = [b.strip() for b in re.split(r"\n\n+", context) if b.strip()]
    best_block = blocks[0] if blocks else context
    best_score = -999
    section_label = "Policy manual"

    for block in blocks:
        header_match = re.match(r"\[([^\]]+)\]", block)
        body = block[header_match.end() :].strip() if header_match else block
        s = score_chunk_content(body, terms, query)
        if s > best_score:
            best_score = s
            best_block = body
            if header_match:
                section_label = header_match.group(1).strip()

    distinctive = _distinctive_terms(terms)
    sentences = _sentences_from_text(best_block)
    ranked: list[tuple[int, str]] = []
    for sent in sentences:
        s = score_chunk_content(sent, terms, query)
        if _toc_penalty(sent) > 20:
            continue
        sent_low = sent.lower()
        if distinctive and not any(d in sent_low for d in distinctive):
            if not re.search(r"\d+\s*%|\d+\.\d+", sent):
                continue
        if s > 0 or re.search(r"\d+\s*%|\d+\.\d+", sent):
            ranked.append((s, sent))

    ranked.sort(key=lambda x: -x[0])
    picked = [s for _, s in ranked[:4]]
    if not picked and best_score < 8:
        return (
            f"I couldn't locate a dedicated section on “{query.strip()}” in the indexed manual. "
            "Try a shorter question with exact CPM wording, re-upload the PDF after fixing your "
            "Gemini key (AIza… from AI Studio), or browse the related text below.\n\n"
            f"{_clean_policy_excerpt(best_block[:400])}…"
        )
    if not picked:
        picked = sentences[:3]

    excerpt = _clean_policy_excerpt(" ".join(picked))
    if len(excerpt) > 520:
        excerpt = excerpt[:517] + "…"

    if not excerpt:
        excerpt = _clean_policy_excerpt(best_block[:520])

    if not re.search(r"§|\d+\.\d+", section_label):
        alt = extract_section_title(best_block)
        if alt:
            section_label = alt

    return f"{excerpt}\n\n[{section_label}]"
