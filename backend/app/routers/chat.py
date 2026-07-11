"""Chat router — RAG Q&A and persistent chat history per document."""

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    Citation,
)
from app.services.rag_service import run_rag_pipeline
from app.utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# ── History helpers ──────────────────────────────────────────────────────────

def _history_path(doc_id: str) -> Path:
    settings = get_settings()
    return Path(settings.chat_history_dir) / f"{doc_id}.json"


def _load_history(doc_id: str) -> list[dict]:
    p = _history_path(doc_id)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return []


def _save_history(doc_id: str, messages: list[dict]) -> None:
    p = _history_path(doc_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(messages, f, indent=2, default=str)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/{doc_id}/ask", response_model=ChatResponse)
async def ask_question(doc_id: str, request: ChatRequest):
    """
    Ask a natural-language question about a document.
    Uses the RAG pipeline: semantic retrieval → Gemini answer → citations.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = run_rag_pipeline(doc_id, question)
    except Exception as e:
        logger.error(f"RAG pipeline error for doc_id={doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")

    answer = result["answer"]
    raw_citations = result["citations"]

    citations = [
        Citation(filename=c["filename"], page_number=c["page_number"])
        for c in raw_citations
    ]

    # Persist to chat history
    history = _load_history(doc_id)
    now = datetime.utcnow().isoformat()

    history.append(
        {
            "role": "user",
            "content": question,
            "citations": [],
            "timestamp": now,
        }
    )
    history.append(
        {
            "role": "assistant",
            "content": answer,
            "citations": [{"filename": c.filename, "page_number": c.page_number} for c in citations],
            "timestamp": now,
        }
    )
    _save_history(doc_id, history)

    return ChatResponse(
        answer=answer,
        citations=citations,
        doc_id=doc_id,
        question=question,
    )


@router.get("/{doc_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(doc_id: str):
    """Retrieve the full chat history for a document."""
    raw = _load_history(doc_id)

    messages = [
        ChatMessage(
            role=m["role"],
            content=m["content"],
            citations=[
                Citation(filename=c["filename"], page_number=c["page_number"])
                for c in m.get("citations", [])
            ],
            timestamp=datetime.fromisoformat(m["timestamp"]),
        )
        for m in raw
    ]

    return ChatHistoryResponse(doc_id=doc_id, messages=messages, total=len(messages))


@router.delete("/{doc_id}/history", status_code=status.HTTP_200_OK)
async def clear_chat_history(doc_id: str):
    """Clear the chat history for a document."""
    p = _history_path(doc_id)
    if p.exists():
        p.unlink()
    logger.info(f"Cleared chat history for doc_id={doc_id}")
    return {"doc_id": doc_id, "message": "Chat history cleared."}
