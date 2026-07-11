"""Summary router — generate and retrieve document summaries."""

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import SummaryResponse
from app.services.llm_service import generate_document_summary
from app.utils.logger import logger

router = APIRouter(prefix="/api/summary", tags=["Summary"])


def _get_doc_meta(doc_id: str) -> dict:
    settings = get_settings()
    meta_path = Path(settings.upload_dir) / "metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="No documents found.")
    with open(meta_path) as f:
        meta = json.load(f)
    if doc_id not in meta:
        raise HTTPException(status_code=404, detail="Document not found.")
    return meta[doc_id]


def _get_full_text(file_path: str) -> str:
    """Re-extract full text from the stored PDF for summary generation."""
    import fitz
    try:
        doc = fitz.open(file_path)
        texts = [doc[i].get_text("text") for i in range(doc.page_count)]
        doc.close()
        return " ".join(texts)
    except Exception as e:
        logger.error(f"Failed to read PDF for summary: {e}")
        return ""


@router.post("/{doc_id}", response_model=SummaryResponse)
async def generate_summary(doc_id: str):
    """
    Generate (or retrieve cached) summary and key topics for a document.
    If a summary was already generated at upload time, returns the cached version.
    """
    doc_info = _get_doc_meta(doc_id)

    # Return cached summary if already available
    cached_summary = doc_info.get("summary", "")
    if cached_summary:
        full_text = _get_full_text(doc_info["file_path"])
        word_count = len(full_text.split())
        return SummaryResponse(
            doc_id=doc_id,
            filename=doc_info["filename"],
            summary=cached_summary,
            key_topics=doc_info.get("key_topics", []),
            word_count=word_count,
        )

    # Generate fresh summary
    full_text = _get_full_text(doc_info["file_path"])
    if not full_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from this PDF.")

    try:
        result = generate_document_summary(full_text, doc_info["filename"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {e}")

    # Cache the result
    settings = get_settings()
    meta_path = Path(settings.upload_dir) / "metadata.json"
    with open(meta_path) as f:
        meta = json.load(f)
    meta[doc_id]["summary"] = result.get("summary", "")
    meta[doc_id]["key_topics"] = result.get("key_topics", [])
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)

    return SummaryResponse(
        doc_id=doc_id,
        filename=doc_info["filename"],
        summary=result.get("summary", ""),
        key_topics=result.get("key_topics", []),
        word_count=len(full_text.split()),
    )


@router.get("/{doc_id}", response_model=SummaryResponse)
async def get_summary(doc_id: str):
    """Get the cached summary for a document (or trigger generation if missing)."""
    return await generate_summary(doc_id)
