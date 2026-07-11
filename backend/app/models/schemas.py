"""Pydantic schemas for all API request/response models."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ─── Document Schemas ─────────────────────────────────────────────────────────

class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    chunk_count: int
    file_size_kb: float
    uploaded_at: datetime
    summary: Optional[str] = None
    suggested_questions: list[str] = []


class DocumentListResponse(BaseModel):
    documents: list[DocumentMeta]
    total: int


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    chunk_count: int
    file_size_kb: float
    uploaded_at: datetime
    suggested_questions: list[str] = []
    message: str = "Document uploaded and indexed successfully."


class DeleteResponse(BaseModel):
    doc_id: str
    message: str


# ─── Chat Schemas ─────────────────────────────────────────────────────────────

class Citation(BaseModel):
    filename: str
    page_number: int
    chunk_text: str = Field(exclude=True, default="")  # internal use only


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    citations: list[Citation] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    doc_id: str
    question: str


class ChatHistoryResponse(BaseModel):
    doc_id: str
    messages: list[ChatMessage]
    total: int


# ─── Summary Schemas ──────────────────────────────────────────────────────────

class SummaryResponse(BaseModel):
    doc_id: str
    filename: str
    summary: str
    key_topics: list[str] = []
    word_count: int


# ─── MCQ Schemas ──────────────────────────────────────────────────────────────

class MCQOption(BaseModel):
    label: str   # "A", "B", "C", "D"
    text: str


class MCQQuestion(BaseModel):
    question: str
    options: list[MCQOption]
    correct_answer: str  # "A" | "B" | "C" | "D"
    explanation: str
    source_page: Optional[int] = None


class MCQRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium")  # easy | medium | hard


class MCQResponse(BaseModel):
    doc_id: str
    filename: str
    questions: list[MCQQuestion]
    total: int


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, Any]
