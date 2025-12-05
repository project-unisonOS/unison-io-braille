from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .interfaces import DeviceInfo, BrailleEvent


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CapsReport:
    person_id: str
    device: DeviceInfo

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "schema_version": "2.0",
            "id": "",
            "timestamp": _ts(),
            "source": "unison-io-braille",
            "event_type": "caps.report",
            "payload": {
                "person_id": self.person_id,
                "caps": {
                    "braille_adapter": {
                        "present": True,
                        "transport": self.device.transport,
                        "vid": self.device.vid,
                        "pid": self.device.pid,
                        "name": self.device.name,
                        "capabilities": self.device.capabilities or {},
                    }
                },
            },
        }


def braille_input_event(evt: BrailleEvent, person_id: Optional[str] = None) -> Dict[str, Any]:
    """Map a BrailleEvent to a Unison EventEnvelope-like dict."""
    return {
        "schema_version": "2.0",
        "timestamp": _ts(),
        "source": "unison-io-braille",
        "event_type": "braille.input",
        "intent": {
            "type": "input.command",
            "command": "braille",
            "payload": {"keys": list(evt.keys), "text": evt.text, "event_type": evt.type},
        },
        "person": {"id": person_id} if person_id else None,
        "auth_scope": "braille.input.read",
        "metadata": {"device_id": evt.device_id},
    }
