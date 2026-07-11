"""PDF text extraction and chunking service using PyMuPDF."""

from pathlib import Path
from dataclasses import dataclass
import fitz  # PyMuPDF

from app.config import get_settings
from app.utils.logger import logger


@dataclass
class TextChunk:
    text: str
    page_number: int
    chunk_index: int
    filename: str
    doc_id: str


def extract_text_from_pdf(file_path: str | Path) -> tuple[list[dict], int]:
    """
    Extract text from a PDF, page by page.

    Returns:
        pages: list of {"page_number": int, "text": str}
        total_pages: int
    """
    path = Path(file_path)
    pages = []

    try:
        doc = fitz.open(str(path))
        total_pages = doc.page_count

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                pages.append({"page_number": page_num + 1, "text": text.strip()})

        doc.close()
        logger.info(f"Extracted {total_pages} pages from {path.name}")
        return pages, total_pages

    except Exception as e:
        logger.error(f"Failed to extract PDF {path}: {e}")
        raise


def chunk_pages(
    pages: list[dict],
    doc_id: str,
    filename: str,
) -> list[TextChunk]:
    """
    Split extracted page text into overlapping chunks with metadata.

    Chunking strategy: word-based with configurable size and overlap.
    Each chunk retains its source page number for citations.
    """
    settings = get_settings()
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        words = page["text"].split()
        page_num = page["page_number"]

        if not words:
            continue

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])

            if len(chunk_text.strip()) > 30:  # skip trivially short chunks
                chunks.append(
                    TextChunk(
                        text=chunk_text,
                        page_number=page_num,
                        chunk_index=chunk_index,
                        filename=filename,
                        doc_id=doc_id,
                    )
                )
                chunk_index += 1

            if end == len(words):
                break
            start = end - overlap  # sliding window

    logger.info(f"Created {len(chunks)} chunks for doc_id={doc_id}")
    return chunks


def get_page_count(file_path: str | Path) -> int:
    """Return the number of pages in a PDF file."""
    try:
        doc = fitz.open(str(file_path))
        count = doc.page_count
        doc.close()
        return count
    except Exception as e:
        logger.error(f"Could not read page count: {e}")
        return 0
