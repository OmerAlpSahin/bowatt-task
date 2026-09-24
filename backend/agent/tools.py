import asyncio
import os
from functools import lru_cache

from tavily import AsyncTavilyClient

from ingestion.pipeline import search_documents

QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "What to search for, in natural language."},
    },
    "required": ["query"],
}

TOOLS = [
    {
        "name": "search_my_documents",
        "description": (
            "Search the files the user has uploaded. Use this whenever the question could "
            "relate to the user's own documents. Returns the most relevant passages with "
            "their file names."
        ),
        "input_schema": QUERY_SCHEMA,
    },
    {
        "name": "web_search",
        "description": "Search the web for current events,general knowledge or anything "
                       "that the user's document do not cover. Returns titles, URLs and page summaries.",
        "input_schema": QUERY_SCHEMA,
    },
]


@lru_cache
def get_tavily() -> AsyncTavilyClient:
    return AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def search_my_documents(query: str) -> str:
    hits = await asyncio.to_thread(search_documents, query)
    MIN_SCORE = 0.25
    if not hits or hits<MIN_SCORE:
        return "No matching passages found in the uploaded documents."
    return "\n\n".join(f"[{h['source']}] (score {h['score']})\n{h['text']}" for h in hits)


async def web_search(query: str) -> str:
    response = await get_tavily().search(query, max_results=5)
    results = response["results"]
    if not results:
        return "No matching information found in the web search."
    return "\n\n".join(f"[{r['title']}] (url {r['url']})\n{r['content'][:1000]}" for r in results)


async def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run one tool. Returns (result_text, is_error)."""
    try:
        if name == "search_my_documents":
            return await search_my_documents(tool_input["query"]), False
        if name == "web_search":
            return await web_search(tool_input["query"]), False
        return f"Unknown tool: {name}", True
    except Exception as e:
        return f"{name} failed: {e}", True
