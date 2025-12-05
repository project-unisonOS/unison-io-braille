from fastapi.testclient import TestClient

from unison_io_braille.server import app


def test_health_ready():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/ready").json().get("ready") is True


def test_translate_endpoint():
    client = TestClient(app)
    resp = client.post("/braille/translate", json={"text": "ab", "table": "ueb_grade1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["cols"] == 2
    assert data["cells"][0] == [1]
