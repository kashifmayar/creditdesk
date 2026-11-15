from app.services.rag_service import (
    _toc_penalty,
    expand_search_terms,
    score_chunk_content,
    _clean_policy_excerpt,
)

TOC = (
    "Credit Procedures Manual (CPM) RMG Table of Contents Page Section I Introduction "
    "1.1 Scope 1 1.2 Objective 1 Section II Target Markets 2.1 Corporate Borrower 3"
)

LTV = (
    "8.1.3 Margin / Loan to Collateral Ratio (LCR) Maximum exposure for commercial "
    "facilities shall not exceed 70% of forced sale value. Residential mortgage cap is 80%."
)

GRACE = (
    "9.2 Grace Period A grace period of five business days is allowed before penal charges "
    "apply on overdue installments."
)


def test_expand_ltv_terms():
    terms = expand_search_terms("Maximum LTV for commercial loans?")
    assert "ltv" in terms
    assert "loan to collateral" in terms or "lcr" in terms


def test_toc_penalized():
    assert _toc_penalty(TOC) > _toc_penalty(LTV)


def test_ltv_chunk_ranks_above_toc():
    terms = expand_search_terms("Maximum LTV for commercial loans?")
    q = "Maximum LTV for commercial loans?"
    assert score_chunk_content(LTV, terms, q) > score_chunk_content(TOC, terms, q)


def test_clean_excerpt_strips_header_noise():
    raw = "Credit Procedures Manual (CPM) RMG " * 3 + "Maximum LTV is 70%."
    assert "CPM" not in _clean_policy_excerpt(raw) or _clean_policy_excerpt(raw).startswith("Maximum")
