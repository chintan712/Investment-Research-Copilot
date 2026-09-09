import pytest

from app.agent.tools import (
    calculate_debt_to_ebitda,
    calculate_profit_margin,
    calculate_revenue_growth,
)
from app.documents.chunker import PageText, chunk_document


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
