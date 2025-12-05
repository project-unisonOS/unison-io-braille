import logging
from typing import Dict, Any, Optional

import httpx

from .settings import ORCH_AUTH_TOKEN

logger = logging.getLogger("unison-io-braille.transport")


def _headers(token: Optional[str]) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def post_event(host: str, port: str, path: str, payload: Dict[str, Any], token: Optional[str] = None) -> tuple[bool, int, dict | None]:
    """Send an event to orchestrator, including Authorization if provided."""
    auth_token = token or ORCH_AUTH_TOKEN
    try:
        url = f"http://{host}:{port}{path}"
        with httpx.Client(timeout=2.0) as client:
            resp = client.post(url, json=payload, headers=_headers(auth_token))
        parsed = None
        try:
            parsed = resp.json()
        except Exception:
            parsed = None
        return (resp.status_code >= 200 and resp.status_code < 300, resp.status_code, parsed)
    except Exception as exc:  # pragma: no cover
        logger.warning("post_failed %s", exc)
        return (False, 0, None)
