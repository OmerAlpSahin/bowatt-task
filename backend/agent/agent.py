import asyncio
import os
from functools import lru_cache

from anthropic import AsyncAnthropic

from agent.tools import TOOLS, run_tool

MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5")
MAX_TURNS = 6

SYSTEM_PROMPT = """You are a research assistant.
- The user may have uploaded documents. You cannot know what they contain without
  searching, so call search_my_documents first for any question that could relate to
  a company, its policies, products or internal information.
- Never say that no documents exist or that you lack information without searching first.
- Use web_search for current events, general knowledge, or when the documents don't cover the question.
- When several searches are independent, request them at the same time.
- Answer in markdown. Cite every fact: [filename] for documents, [page title](url) for web pages.
- If the sources don't contain the answer, say so instead of guessing."""


@lru_cache
def get_client() -> AsyncAnthropic:
    return AsyncAnthropic()


async def run_agent(question: str):
    messages = [{"role": "user", "content": question}]

    for _ in range(MAX_TURNS):
        async with get_client().messages.stream(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
            response = await stream.get_final_message()
        yield "\n\n"

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            return

        for call in tool_calls:
            yield f"_Using {call.name}: \"{call.input.get('query', '')}\"_\n\n"

        results = await asyncio.gather(*[run_tool(call.name,call.input) for call in tool_calls])

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": call.id, "content": text, "is_error": is_error}
            for call, (text, is_error) in zip(tool_calls, results)
        ]})

    yield "\n\n_Stopped: reached the maximum number of research steps._"
