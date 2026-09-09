from io import BytesIO

import fitz

from app.documents.chunker import PageText


class InvalidPDFError(ValueError):
    pass


def extract_pages(data: bytes) -> list[PageText]:
    try:
        document = fitz.open(stream=BytesIO(data), filetype="pdf")
    except Exception as exc:
        raise InvalidPDFError("The uploaded file is not a readable PDF") from exc
    pages = [PageText(index + 1, page.get_text("text").strip()) for index, page in enumerate(document)]
    if not any(page.text for page in pages):
        raise InvalidPDFError("The PDF does not contain extractable text")
    return pages
