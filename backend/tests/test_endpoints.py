from fastapi.testclient import TestClient

import main
from rest import sources

client = TestClient(main.app)


def test_upload_rejects_non_text_file():
    response = client.post("/api/sources", files=[("files", ("photo.png", b"\x89PNG", "image/png"))])

    assert response.status_code == 415
    assert "photo.png" in response.json()["detail"]


def test_upload_rejects_empty_file():
    response = client.post("/api/sources", files=[("files", ("empty.txt", b"   ", "text/plain"))])

    assert response.status_code == 400


def test_upload_rejects_invalid_utf8():
    response = client.post("/api/sources", files=[("files", ("bad.txt", b"\xff\xfe\x00", "text/plain"))])

    assert response.status_code == 400


def test_upload_returns_what_the_frontend_expects(monkeypatch):
    monkeypatch.setattr(sources, "ingest_text", lambda source, text: 3)

    response = client.post("/api/sources", files=[("files", ("notes.txt", b"hello world", "text/plain"))])

    assert response.status_code == 200
    assert response.json() == {
        "uploaded": [{"name": "notes.txt", "size": 11, "type": "text/plain", "chunks": 3}]
    }


def test_research_rejects_empty_question():
    response = client.post("/api/research", json={"request": "   "})

    assert response.status_code == 400
