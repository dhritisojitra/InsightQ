"""RAG pipeline orchestrator — ties together retrieval and generation."""

from app.services.vector_store import semantic_search
from app.services.llm_service import generate_rag_answer
from app.config import get_settings
from app.utils.logger import logger


def run_rag_pipeline(doc_id: str, question: str) -> dict:
    """
    Full RAG pipeline:
      1. Semantic search over the document's vector store
      2. Build context from top-K chunks
      3. Generate LLM answer with citations

    Returns:
      {
        "answer": str,
        "citations": [{"filename": str, "page_number": int}]
      }
    """
    settings = get_settings()

    # Step 1: Retrieve relevant chunks
    chunks = semantic_search(doc_id, question, top_k=settings.top_k_results)
    if not chunks:
        return {
            "answer": "I couldn't find relevant content in this document to answer your question.",
            "citations": [],
        }

    logger.info(f"Retrieved {len(chunks)} chunks for doc_id={doc_id}, question='{question[:60]}...'")

    # Step 2: Generate answer using LLM
    answer = generate_rag_answer(question, chunks)

    # Step 3: Deduplicate citations by (filename, page_number)
    seen = set()
    citations = []
    for chunk in chunks:
        key = (chunk["filename"], chunk["page_number"])
        if key not in seen:
            seen.add(key)
            citations.append(
                {
                    "filename": chunk["filename"],
                    "page_number": chunk["page_number"],
                }
            )

    return {
        "answer": answer,
        "citations": citations,
    }
