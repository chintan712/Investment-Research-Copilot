from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    document: str
    page: int

    def inline(self) -> str:
        return f"[{self.document}, p.{self.page}]"


def unique_citations(chunks: list[object]) -> list[Citation]:
    seen: set[tuple[str, int]] = set()
    citations: list[Citation] = []
    for chunk in chunks:
        key = (chunk.document, chunk.page)
        if key not in seen:
            seen.add(key)
            citations.append(Citation(*key))
    return citations
