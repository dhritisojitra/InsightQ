"""MCQ router — generate multiple-choice questions from a document."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import MCQOption, MCQQuestion, MCQRequest, MCQResponse
from app.services.llm_service import generate_mcqs
from app.services.vector_store import semantic_search
from app.utils.logger import logger

router = APIRouter(prefix="/api/mcq", tags=["MCQ"])


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


@router.post("/{doc_id}", response_model=MCQResponse)
async def generate_mcq(doc_id: str, request: MCQRequest = MCQRequest()):
    """
    Generate multiple-choice questions from a document.
    Retrieves a broad set of chunks to cover the full document for variety.
    """
    doc_info = _get_doc_meta(doc_id)

    # Retrieve a diverse spread of content using broad queries
    broad_queries = [
        "main concepts and definitions",
        "key findings and conclusions",
        "methods and approaches",
        "important facts and data",
    ]

    chunks_seen = {}
    for q in broad_queries:
        for chunk in semantic_search(doc_id, q, top_k=4):
            key = chunk["page_number"]
            if key not in chunks_seen:
                chunks_seen[key] = chunk

    context_chunks = list(chunks_seen.values())[:8]  # max 8 chunks

    if not context_chunks:
        raise HTTPException(
            status_code=422, detail="Could not retrieve content from this document."
        )

    try:
        raw_mcqs = generate_mcqs(context_chunks, request.num_questions, request.difficulty)
    except Exception as e:
        logger.error(f"MCQ generation failed for doc_id={doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"MCQ generation failed: {e}")

    questions = []
    for q_data in raw_mcqs:
        try:
            options = [
                MCQOption(label=o["label"], text=o["text"])
                for o in q_data.get("options", [])
            ]
            questions.append(
                MCQQuestion(
                    question=q_data.get("question", ""),
                    options=options,
                    correct_answer=q_data.get("correct_answer", "A"),
                    explanation=q_data.get("explanation", ""),
                    source_page=q_data.get("source_page"),
                )
            )
        except Exception as e:
            logger.warning(f"Skipping malformed MCQ entry: {e}")
            continue

    return MCQResponse(
        doc_id=doc_id,
        filename=doc_info["filename"],
        questions=questions,
        total=len(questions),
    )
