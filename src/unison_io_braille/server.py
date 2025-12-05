import asyncio
import logging
import os
import time
from typing import Dict, Any, List, Optional

import httpx
from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
import uvicorn

from .translator_loader import TableTranslator
from .events import CapsReport, braille_input_event
from .discovery import enumerate_usb, enumerate_bluetooth
from .simulated_driver import SimulatedBrailleDriver
from .interfaces import BrailleEvent, BrailleCells, DeviceInfo
from .manager import BrailleDeviceDriverRegistry, BrailleDeviceManager
from .middleware import ScopeMiddleware
from .input_router import forward_events
from .transport import post_event
from .settings import APP_NAME, ORCH_HOST, ORCH_PORT, DEFAULT_PERSON_ID, REQUIRED_SCOPE_INPUT

logger = logging.getLogger("unison-io-braille.server")

app = FastAPI(title=APP_NAME)
app.add_middleware(ScopeMiddleware, required_scope=REQUIRED_SCOPE_INPUT)
_metrics: Dict[str, int] = {}
_ws_clients: List[WebSocket] = []
_focus_text: Optional[str] = None
_focus_table: str = "ueb_grade1"
_driver_registry = BrailleDeviceDriverRegistry()
_driver_registry.register("sim", SimulatedBrailleDriver)
_manager = BrailleDeviceManager(_driver_registry)


def _bump(key: str) -> None:
    _metrics[key] = _metrics.get(key, 0) + 1


def http_post_json(host: str, port: str, path: str, payload: dict) -> tuple[bool, int, dict | None]:
    try:
        url = f"http://{host}:{port}{path}"
        with httpx.Client(timeout=2.0) as client:
            resp = client.post(url, json=payload)
        parsed = None
        try:
            parsed = resp.json()
        except Exception:
            parsed = None
        return (resp.status_code >= 200 and resp.status_code < 300, resp.status_code, parsed)
    except Exception as exc:  # pragma: no cover
        logger.warning("post_failed %s", exc)
        return (False, 0, None)


def _cells_payload(text: str, table: str) -> Dict[str, Any]:
    translator = TableTranslator(table)
    cells = translator.text_to_cells(text)
    return {
        "table": table,
        "rows": cells.rows,
        "cols": cells.cols,
        "cells": [[int(i + 1) for i, v in enumerate(cell.dots) if v] for cell in cells.cells],
        "cursor": cells.cursor_position,
    }


async def _broadcast_focus(payload: Dict[str, Any]) -> None:
    clients = list(_ws_clients)
    for ws in clients:
        try:
            await ws.send_json({"event": "focus", "payload": payload})
        except Exception:
            try:
                _ws_clients.remove(ws)
            except ValueError:
                pass


@app.get("/health")
def health() -> Dict[str, str]:
    _bump("/health")
    return {"status": "ok", "service": APP_NAME}


@app.get("/ready")
def ready() -> Dict[str, Any]:
    _bump("/ready")
    return {"ready": True}


@app.get("/metrics")
def metrics() -> str:
    lines = [
        "# HELP unison_io_braille_requests_total Total requests by endpoint",
        "# TYPE unison_io_braille_requests_total counter",
    ]
    for k, v in _metrics.items():
        lines.append(f'unison_io_braille_requests_total{{endpoint="{k}"}} {v}')
    return "\n".join(lines)


@app.post("/braille/translate")
def translate(text: str = Body(..., embed=True), table: str = Body("ueb_grade1", embed=True)) -> Dict[str, Any]:
    _bump("/braille/translate")
    return _cells_payload(text, table)


@app.post("/braille/focus")
async def set_focus(text: str = Body(..., embed=True), table: str = Body("ueb_grade1", embed=True)) -> Dict[str, Any]:
    """Accept focus text from renderer/onboarding and broadcast to subscribers."""
    global _focus_text, _focus_table
    _focus_text = text
    _focus_table = table
    payload = _cells_payload(text, table)
    await _broadcast_focus(payload)
    _bump("/braille/focus")
    return {"ok": True, "payload": payload}


@app.websocket("/braille/output")
async def websocket_output(ws: WebSocket):
    await ws.accept()
    _ws_clients.append(ws)
    try:
        await ws.send_json({"event": "connected", "service": APP_NAME, "ts": time.time()})
        if _focus_text:
            await _broadcast_focus(_cells_payload(_focus_text, _focus_table))
        while True:
            try:
                data = await ws.receive_bytes()
                # Treat incoming bytes as Braille device packets for simulation; forward to orchestrator.
                evt = BrailleEvent(type="text", keys=(), text=data.decode(errors="ignore"))
                forward_events([evt])
            except WebSocketDisconnect:
                break
    finally:
        try:
            _ws_clients.remove(ws)
        except ValueError:
            pass
        _bump("/braille/output/ws_closed")


@app.get("/braille/devices/discover")
async def discover_devices() -> Dict[str, Any]:
    """Enumerate USB and Bluetooth devices; returns cached results."""
    usb = list(enumerate_usb())
    bt = []
    try:
        bt = list(await enumerate_bluetooth())
    except Exception:
        bt = []
    devices = [d.__dict__ for d in usb + bt]
    _bump("/braille/devices/discover")
    # Emit caps.report for first device, best effort
    if usb:
        envelope = CapsReport(person_id=DEFAULT_PERSON_ID, device=usb[0]).to_envelope()
        http_post_json(ORCH_HOST, ORCH_PORT, "/event", envelope)
    return {"devices": devices}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("BRAILLE_PORT", "8090")))
