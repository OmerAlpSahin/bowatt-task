from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi import HTTPException

from agent.agent import run_agent
import logging

import anthropic

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

async def stream_answer(question: str):
    try:
        async for piece in run_agent(question):
            yield piece
    except anthropic.AuthenticationError:
        logger.error("Anthropic rejected the API key")
        yield "\n\n**Error:** the research service is misconfigured (invalid API key)."
    except anthropic.RateLimitError:
        logger.warning("Anthropic rate limit hit")
        yield "\n\n**Error:** Too many requests"
    except anthropic.APIConnectionError:
        logger.error("Could not reach Anthropic")
        yield "\n\n**Error:** Couldnt reach the AI server. Please try again in a moment"
    except anthropic.APIStatusError as e:
        logger.error("Anthropic API error %s: %s", e.status_code, e.message)
        yield f"\n\n**Error:** the AI service returned an error ({e.status_code}). Please try again."
    except Exception:
        logger.exception("Unexpected error while researching")
        yield "\n\n**Error:** Something went wrong while researching, please try again."

class ResearchRequest(BaseModel):
    request: str


@router.post("/research")
async def research(body: ResearchRequest):
    if not body.request.strip():
        raise HTTPException(status_code=400, detail="Research request must not be empty.")
    return StreamingResponse(stream_answer(body.request), media_type="text/markdown")
