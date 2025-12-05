from fastapi.testclient import TestClient

from unison_io_braille.server import app, ORCH_HOST, ORCH_PORT
from unison_io_braille.events import braille_input_event
from unison_io_braille.interfaces import BrailleEvent


def test_health_ready():
    client = TestClient(app)
    headers = {"X-Test-Bypass": "1"}
    assert client.get("/health", headers=headers).status_code == 200
    assert client.get("/ready", headers=headers).json().get("ready") is True


def test_translate_endpoint():
    client = TestClient(app)
    headers = {"X-Test-Bypass": "1"}
    resp = client.post("/braille/translate", json={"text": "ab", "table": "ueb_grade1"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["cols"] == 2
    assert data["cells"][0] == [1]


def test_input_event_helper():
    evt = BrailleEvent(type="text", keys=(), text="hi", device_id="sim1")
    env = braille_input_event(evt, person_id="user1")
    assert env["event_type"] == "braille.input"
    assert env["person"]["id"] == "user1"
