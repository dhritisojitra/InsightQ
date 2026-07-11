"""Documents router — upload, list, and delete PDF documents."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.models.schemas import DeleteResponse, DocumentListResponse, DocumentMeta, UploadResponse
from app.services.embedding_service import embed_texts  # warm up on import
from app.services.llm_service import (
    generate_document_summary,
    generate_suggested_questions,
)
from app.services.pdf_service import chunk_pages, extract_text_from_pdf, get_page_count
from app.services.vector_store import delete_document_index, index_chunks
from app.utils.logger import logger

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# ── Metadata registry (JSON file-based) ──────────────────────────────────────

def _meta_path(settings) -> Path:
    return Path(settings.upload_dir) / "metadata.json"


def _load_metadata(settings) -> dict:
    p = _meta_path(settings)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def _parse_uploaded_at(val: str) -> datetime:
    dt = datetime.fromisoformat(val)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _save_metadata(settings, data: dict) -> None:
    p = _meta_path(settings)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, generate embeddings, and index in ChromaDB.
    Also generates a document summary and suggested questions using Gemini.
    """
    settings = get_settings()

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    # Validate file size (max 50 MB)
    contents = await file.read()
    file_size_kb = len(contents) / 1024
    if file_size_kb > 50 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 50 MB.",
        )

    # Save to disk
    doc_id = str(uuid.uuid4())
    safe_name = file.filename.replace(" ", "_")
    file_path = Path(settings.upload_dir) / f"{doc_id}_{safe_name}"
    file_path.write_bytes(contents)
    logger.info(f"Saved PDF: {file_path} ({file_size_kb:.1f} KB)")

    # Extract + chunk
    try:
        pages, page_count = extract_text_from_pdf(file_path)
        chunks = chunk_pages(pages, doc_id=doc_id, filename=file.filename)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {e}")

    if not chunks:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Could not extract text from this PDF.")

    # Index in ChromaDB
    try:
        chunk_count = index_chunks(doc_id, chunks)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

    # Generate summary + suggested questions via LLM
    full_text = " ".join(p["text"] for p in pages)
    summary_data = {"summary": "", "key_topics": []}
    suggested_questions: list[str] = []

    try:
        summary_data = generate_document_summary(full_text, file.filename)
        if summary_data.get("summary"):
            suggested_questions = generate_suggested_questions(
                summary_data["summary"], file.filename
            )
    except Exception as e:
        logger.warning(f"LLM summary/questions generation failed: {e}")

    uploaded_at = datetime.now(timezone.utc)

    # Persist metadata
    meta = _load_metadata(settings)
    meta[doc_id] = {
        "doc_id": doc_id,
        "filename": file.filename,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "file_size_kb": round(file_size_kb, 2),
        "uploaded_at": uploaded_at.isoformat(),
        "file_path": str(file_path),
        "summary": summary_data.get("summary", ""),
        "key_topics": summary_data.get("key_topics", []),
        "suggested_questions": suggested_questions,
    }
    _save_metadata(settings, meta)

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        page_count=page_count,
        chunk_count=chunk_count,
        file_size_kb=round(file_size_kb, 2),
        uploaded_at=uploaded_at,
        suggested_questions=suggested_questions,
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents with metadata."""
    settings = get_settings()
    meta = _load_metadata(settings)

    docs = [
        DocumentMeta(
            doc_id=v["doc_id"],
            filename=v["filename"],
            page_count=v["page_count"],
            chunk_count=v["chunk_count"],
            file_size_kb=v["file_size_kb"],
            uploaded_at=_parse_uploaded_at(v["uploaded_at"]),
            summary=v.get("summary"),
            suggested_questions=v.get("suggested_questions", []),
        )
        for v in meta.values()
    ]
    docs.sort(key=lambda d: d.uploaded_at, reverse=True)

    return DocumentListResponse(documents=docs, total=len(docs))


@router.get("/{doc_id}", response_model=DocumentMeta)
async def get_document(doc_id: str):
    """Get metadata for a specific document."""
    settings = get_settings()
    meta = _load_metadata(settings)

    if doc_id not in meta:
        raise HTTPException(status_code=404, detail="Document not found.")

    v = meta[doc_id]
    return DocumentMeta(
        doc_id=v["doc_id"],
        filename=v["filename"],
        page_count=v["page_count"],
        chunk_count=v["chunk_count"],
        file_size_kb=v["file_size_kb"],
        uploaded_at=_parse_uploaded_at(v["uploaded_at"]),
        summary=v.get("summary"),
        suggested_questions=v.get("suggested_questions", []),
    )


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    """Delete a document and its vector index."""
    settings = get_settings()
    meta = _load_metadata(settings)

    if doc_id not in meta:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc_info = meta[doc_id]

    # Remove PDF file
    file_path = Path(doc_info.get("file_path", ""))
    if file_path.exists():
        file_path.unlink()

    # Remove vector index
    delete_document_index(doc_id)

    # Remove chat history
    chat_file = Path(settings.chat_history_dir) / f"{doc_id}.json"
    if chat_file.exists():
        chat_file.unlink()

    # Update registry
    del meta[doc_id]
    _save_metadata(settings, meta)

    logger.info(f"Deleted document doc_id={doc_id}")
    return DeleteResponse(doc_id=doc_id, message="Document deleted successfully.")
