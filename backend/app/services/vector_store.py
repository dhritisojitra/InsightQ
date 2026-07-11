"""ChromaDB vector store service — persistent storage per document."""

from functools import lru_cache
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.services.pdf_service import TextChunk
from app.services.embedding_service import embed_texts, embed_query
from app.utils.logger import logger


@lru_cache(maxsize=1)
def _get_chroma_client() -> chromadb.PersistentClient:
    """Create and cache the ChromaDB persistent client."""
    settings = get_settings()
    chroma_path = str(Path(settings.chroma_dir).resolve())
    logger.info(f"ChromaDB path: {chroma_path}")
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client


def _collection_name(doc_id: str) -> str:
    """Sanitize doc_id for use as a ChromaDB collection name."""
    return f"doc_{doc_id.replace('-', '_')}"


def index_chunks(doc_id: str, chunks: list[TextChunk]) -> int:
    """
    Embed and store text chunks in ChromaDB for a given document.

    Returns the number of chunks indexed.
    """
    client = _get_chroma_client()
    col_name = _collection_name(doc_id)

    # Delete existing collection if re-indexing
    try:
        client.delete_collection(col_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=col_name,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    ids = [f"{doc_id}_{c.chunk_index}" for c in chunks]
    metadatas = [
        {
            "page_number": c.page_number,
            "chunk_index": c.chunk_index,
            "filename": c.filename,
            "doc_id": c.doc_id,
        }
        for c in chunks
    ]

    # ChromaDB batch add (max 5461 per batch due to sqlite limits)
    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            documents=texts[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    logger.info(f"Indexed {len(chunks)} chunks for doc_id={doc_id}")
    return len(chunks)


def semantic_search(
    doc_id: str,
    query: str,
    top_k: int | None = None,
) -> list[dict]:
    """
    Search the vector store for chunks most relevant to the query.

    Returns list of dicts with keys: text, page_number, filename, score.
    """
    settings = get_settings()
    k = top_k or settings.top_k_results

    client = _get_chroma_client()
    col_name = _collection_name(doc_id)

    try:
        collection = client.get_collection(col_name)
    except Exception:
        logger.warning(f"Collection not found for doc_id={doc_id}")
        return []

    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, distances):
        hits.append(
            {
                "text": doc,
                "page_number": meta.get("page_number", 0),
                "filename": meta.get("filename", ""),
                "score": round(1 - dist, 4),  # cosine similarity
            }
        )

    return hits


def delete_document_index(doc_id: str) -> bool:
    """Delete the ChromaDB collection for a document."""
    client = _get_chroma_client()
    col_name = _collection_name(doc_id)
    try:
        client.delete_collection(col_name)
        logger.info(f"Deleted collection for doc_id={doc_id}")
        return True
    except Exception as e:
        logger.warning(f"Failed to delete collection {col_name}: {e}")
        return False


def collection_exists(doc_id: str) -> bool:
    """Check if a ChromaDB collection exists for a document."""
    client = _get_chroma_client()
    col_name = _collection_name(doc_id)
    try:
        client.get_collection(col_name)
        return True
    except Exception:
        return False
