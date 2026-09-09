from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    page_number: int
    chunk_index: int
    content: str


def _words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def chunk_document(
    pages: list[PageText],
    target_words: int = 650,
    overlap_words: int = 80,
) -> list[DocumentChunk]:
    """Chunk within pages when possible, retaining the source page for citations."""
    if target_words <= 0 or overlap_words < 0 or overlap_words >= target_words:
        raise ValueError("target_words must be positive and overlap_words must be smaller")

    chunks: list[DocumentChunk] = []
    chunk_index = 0
    for page in pages:
        words = _words(page.text)
        if not words:
            continue
        step = target_words - overlap_words
        for start in range(0, len(words), step):
            content = " ".join(words[start : start + target_words]).strip()
            if content:
                chunks.append(DocumentChunk(page.page_number, chunk_index, content))
                chunk_index += 1
            if start + target_words >= len(words):
                break
    return chunks
