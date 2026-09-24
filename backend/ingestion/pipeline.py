from ingestion.chunking import chunk_text
from ingestion.embeddings import embed_documents, embed_query
from ingestion.vector_store import add_chunks, search


def ingest_text(source: str, text: str) -> int:
    chunks = chunk_text(text)
    vectors = embed_documents(chunks)
    add_chunks(source,chunks,embeddings=vectors)
    return len(chunks)


def search_documents(question: str, k: int = 5) -> list[dict]:
    return search(embed_query(question),k)
