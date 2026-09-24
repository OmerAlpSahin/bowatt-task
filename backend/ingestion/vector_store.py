from functools import lru_cache
from pathlib import Path

import chromadb

CHROMA_PATH = Path(__file__).resolve().parent.parent / "data" / "chroma"
COLLECTION_NAME = "sources"


@lru_cache
def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}},
    )


def add_chunks(source: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    collection = get_collection()
    collection.delete(where={"source": source}) # for edge case where the uploaded version is shorter than the original
    collection.upsert(
        ids=[f"{source}-{n}" for n in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": source,"chunk":n} for n in range(len(chunks))],
    )


def search(query_embedding: list[float], k: int = 5) -> list[dict]:
    result = get_collection().query(query_embeddings=[query_embedding], n_results=k)
    hits = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        hits.append({
            "text": text,
            "source": meta["source"],
            "score": round(1 - distance,3),
        })
    return hits
