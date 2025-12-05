import logging
import time
from typing import Dict, Any

from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
import uvicorn

from .translator_loader import TableTranslator

logger = logging.getLogger("unison-io-braille.server")

APP_NAME = "unison-io-braille"
app = FastAPI(title=APP_NAME)
_metrics: Dict[str, int] = {}


def _bump(key: str) -> None:
    _metrics[key] = _metrics.get(key, 0) + 1


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
    translator = TableTranslator(table)
    cells = translator.text_to_cells(text)
    return {
        "table": table,
        "rows": cells.rows,
        "cols": cells.cols,
        "cells": [[int(i + 1) for i, v in enumerate(cell.dots) if v] for cell in cells.cells],
        "cursor": cells.cursor_position,
    }


@app.websocket("/braille/output")
async def websocket_output(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"event": "connected", "service": APP_NAME, "ts": time.time()})
        while True:
            try:
                await ws.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        _bump("/braille/output/ws_closed")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
