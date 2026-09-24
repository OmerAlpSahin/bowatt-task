from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from fastapi import HTTPException
router = APIRouter(prefix="/api")





class ResearchRequest(BaseModel):
    request: str

async def fake_answer(question: str):
    yield f"# Research: {question}\n\n"
    await asyncio.sleep(0.5)
    yield "This is a **fake** answer to test streaming.\n\n"
    await asyncio.sleep(0.5)
    yield "- Point one\n"
    await asyncio.sleep(0.5)
    yield "- Point two\n"


@router.post("/research")
async def research(body: ResearchRequest):
    if not body.request.strip():
        raise HTTPException(status_code=400, detail="Research request must not be empty.")
    return StreamingResponse(fake_answer(body.request), media_type="text/markdown")
