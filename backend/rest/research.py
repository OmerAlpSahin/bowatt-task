from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi import HTTPException
router = APIRouter(prefix="/api")

from agent.agent import run_agent



class ResearchRequest(BaseModel):
    request: str


@router.post("/research")
async def research(body: ResearchRequest):
    if not body.request.strip():
        raise HTTPException(status_code=400, detail="Research request must not be empty.")
    return StreamingResponse(run_agent(body.request), media_type="text/markdown")
