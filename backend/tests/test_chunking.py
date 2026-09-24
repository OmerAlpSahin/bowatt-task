import pytest

from ingestion.chunking import chunk_text


def test_splits_with_overlap():
    assert chunk_text("ABCDEFGHIJ", chunk_size=4, overlap=1) == ["ABCD", "DEFG", "GHIJ"]


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []


def test_rejects_overlap_not_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=4, overlap=4)


def test_short_text_gives_one_chunk():
    assert chunk_text("hi") == ["hi"]