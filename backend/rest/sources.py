from fastapi import APIRouter, UploadFile
from fastapi import HTTPException
from ingestion.pipeline import ingest_text
import asyncio
router = APIRouter(prefix="/api",tags=["sources"])



@router.post("/sources")
async def upload_sources(files: list[UploadFile]):


    accepted = []
    for f in files:
        if not (f.content_type or "").startswith("text/"):
            raise HTTPException(status_code=415, detail=f"{f.filename} is not a text file")
        data = await f.read()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail=f"{f.filename} is not valid UTF-8 text")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail=f"{f.filename} is empty")
        accepted.append((f, text))
        
        
    tasks = [asyncio.to_thread(ingest_text, f.filename, text) for f, text in accepted]
    counts = await asyncio.gather(*tasks)        
        
    uploaded = [
        {"name": f.filename, "size": f.size, "type": f.content_type, "chunks": count}
        for (f, text), count in zip(accepted, counts)
    ]
    return {"uploaded": uploaded}