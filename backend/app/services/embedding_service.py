"""Sentence Transformers embedding service — singleton pattern for fast re-use."""

from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.utils.logger import logger


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model (loaded once on first call)."""
    settings = get_settings()
    model_name = settings.embedding_model
    logger.info(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    logger.info(f"Embedding model loaded: {model_name}")
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Encode a list of text strings into dense embeddings.

    Returns:
        List of float vectors, one per input string.
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,  # cosine similarity via dot product
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Encode a single query string into an embedding vector."""
    return embed_texts([query])[0]
