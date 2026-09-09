SYSTEM_PROMPT = """You are an investment research assistant. Answer only from the supplied document context.
Do not invent facts. If the context is insufficient, say so plainly. Distinguish documented facts from interpretation.
Cite factual claims inline as [Document, p.N]. Any calculations must be performed by the supplied backend tools.
"""


def build_context(chunks: list[object], max_words: int) -> tuple[str, list[object]]:
    selected: list[object] = []
    words_used = 0
    sections: list[str] = []
    for chunk in chunks:
        words = chunk.content.split()
        if words_used + len(words) > max_words:
            break
        sections.append(f"[{chunk.document}, p.{chunk.page}]\n{chunk.content}")
        selected.append(chunk)
        words_used += len(words)
    return "\n\n".join(sections), selected
