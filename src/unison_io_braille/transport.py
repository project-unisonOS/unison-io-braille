import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger("unison-io-braille.transport")


def post_event(host: str, port: str, path: str, payload: Dict[str, Any]) -> tuple[bool, int, dict | None]:
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
