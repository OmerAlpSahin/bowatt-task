import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


@lru_cache
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_documents(texts: list[str]) -> list[list[float]]:
    vectors = get_model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()              


def embed_query(text: str) -> list[float]:
    return embed_documents([text])[0]