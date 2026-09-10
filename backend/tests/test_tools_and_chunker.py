import pytest

from app.agent.tools import (
    calculate_debt_to_ebitda,
    calculate_profit_margin,
    calculate_revenue_growth,
)
from app.documents.chunker import PageText, chunk_document
from app.rag.citations import unique_citations
from app.rag.prompt import build_context
from app.rag.retriever import RetrievedChunk


def test_revenue_growth() -> None:
    assert calculate_revenue_growth(100, 120) == 20


def test_debt_to_ebitda() -> None:
    assert calculate_debt_to_ebitda(84, 26) == 3.23


def test_profit_margin() -> None:
    assert calculate_profit_margin(15, 100) == 15


def test_financial_tools_reject_zero_denominators() -> None:
    with pytest.raises(ValueError):
        calculate_revenue_growth(0, 10)
    with pytest.raises(ValueError):
        calculate_debt_to_ebitda(10, 0)
    with pytest.raises(ValueError):
        calculate_profit_margin(10, 0)


def test_chunking_preserves_page_metadata() -> None:
    pages = [PageText(1, "one two three"), PageText(2, "four five six")]
    chunks = chunk_document(pages, target_words=2, overlap_words=0)
    assert [(chunk.page_number, chunk.content) for chunk in chunks] == [
        (1, "one two"),
        (1, "three"),
        (2, "four five"),
        (2, "six"),
    ]


def test_citations_are_unique_and_keep_retrieval_order() -> None:
    chunks = [
        RetrievedChunk("first", "Acme.pdf", 2, 0.9),
        RetrievedChunk("duplicate page", "Acme.pdf", 2, 0.8),
        RetrievedChunk("second", "Risks.pdf", 4, 0.7),
    ]
    citations = unique_citations(chunks)
    assert [citation.inline() for citation in citations] == [
        "[Acme.pdf, p.2]",
        "[Risks.pdf, p.4]",
    ]


def test_context_budget_stops_before_exceeding_limit() -> None:
    chunks = [
        RetrievedChunk("one two", "Acme.pdf", 1, 0.9),
        RetrievedChunk("three four", "Acme.pdf", 2, 0.8),
    ]
    context, selected = build_context(chunks, max_words=3)
    assert "one two" in context
    assert len(selected) == 1
