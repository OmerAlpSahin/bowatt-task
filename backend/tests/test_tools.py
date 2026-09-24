import asyncio

from agent import tools


def fake_hits(query, k=5):
    return [
        {"text": "Relevant passage", "source": "good.txt", "score": 0.8},
        {"text": "Noise passage", "source": "noise.txt", "score": 0.1},
    ]


def test_low_scores_are_filtered_out(monkeypatch):
    monkeypatch.setattr(tools, "search_documents", fake_hits)

    result = asyncio.run(tools.search_my_documents("anything"))

    assert "Relevant passage" in result
    assert "Noise passage" not in result


def only_low_hits(query, k=5):
    return [{"text": "Noise passage", "source": "noise.txt", "score": 0.1}]


def test_only_low_scores_gives_no_match_message(monkeypatch):
    monkeypatch.setattr(tools, "search_documents", only_low_hits)

    result = asyncio.run(tools.search_my_documents("anything"))

    assert result == "No matching passages found in the uploaded documents."


def test_unknown_tool_returns_error():
    result = asyncio.run(tools.run_tool("made_up_tool", {}))

    assert result == ("Unknown tool: made_up_tool", True)


def test_failing_tool_returns_error_instead_of_raising(monkeypatch):
    def broken_search(query, k=5):
        raise RuntimeError("database is down")

    monkeypatch.setattr(tools, "search_documents", broken_search)

    text, is_error = asyncio.run(tools.run_tool("search_my_documents", {"query": "x"}))

    assert is_error is True
    assert "database is down" in text
