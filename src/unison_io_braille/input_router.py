from typing import Iterable

from .events import braille_input_event
from .interfaces import BrailleEvent
from .transport import post_event
from .settings import ORCH_HOST, ORCH_PORT, DEFAULT_PERSON_ID, ORCH_AUTH_TOKEN


def forward_events(events: Iterable[BrailleEvent]) -> None:
    """Forward BrailleEvents to orchestrator as braille.input envelopes."""
    for evt in events:
        envelope = braille_input_event(evt, person_id=DEFAULT_PERSON_ID)
        post_event(ORCH_HOST, ORCH_PORT, "/event", envelope, token=ORCH_AUTH_TOKEN)
