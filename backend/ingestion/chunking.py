def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if not text.strip():
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap                       

    while True:
        end = start + chunk_size
        chunks.append(text[start:end])  
        if end >= len(text):          
            break
        start = start + step                  

    return chunks
