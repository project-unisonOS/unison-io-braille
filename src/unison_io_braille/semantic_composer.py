from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .interfaces import BrailleCells
from .translator import SimpleTranslator


@dataclass(frozen=True)
class BrailleSegment:
    semantic_id: str
    kind: str
    text: str
    cells: BrailleCells


@dataclass
class BrailleSemanticExpression:
    experience_id: str
    summary: str
    segments: list[BrailleSegment]
    action_ids: list[str]
    required_node_ids: list[str]
    fallback: str
    cursor: int = 0

    def current(self) -> BrailleSegment | None:
        return self.segments[self.cursor] if self.segments else None

    def move(self, offset: int) -> BrailleSegment | None:
        if not self.segments:
            return None
        self.cursor = max(0, min(len(self.segments) - 1, self.cursor + offset))
        return self.current()

    def go_to(self, semantic_id: str) -> BrailleSegment | None:
        for index, segment in enumerate(self.segments):
            if segment.semantic_id == semantic_id:
                self.cursor = index
                return segment
        return None


class BrailleSemanticComposer:
    """Compose tactile navigation from semantic structure, independent of visual focus."""

    def __init__(self, translator: SimpleTranslator | None = None):
        self.translator = translator or SimpleTranslator()

    def compose(self, sem: dict[str, Any]) -> BrailleSemanticExpression:
        if sem.get("schema_version") != "sem.v1" or not sem.get("experience_id") or not sem.get("outcome"):
            raise ValueError("invalid semantic experience")
        segments = [self._segment("outcome", "outcome", str(sem["outcome"]))]
        required_ids = []
        for node in sem.get("nodes", []):
            node_id = str(node.get("node_id", ""))
            if not node_id:
                raise ValueError("semantic node identifier required")
            text = str(node.get("detail") or node.get("summary") or node.get("label") or "")
            segments.append(self._segment(node_id, str(node.get("kind", "entity")), text))
            if node.get("required") is True:
                required_ids.append(node_id)
        action_ids = []
        for action in sem.get("actions", []):
            action_id = str(action.get("action_id", ""))
            consequence = str(action.get("consequence", ""))
            if not action_id or not consequence:
                raise ValueError("semantic action binding required")
            action_ids.append(action_id)
            segments.append(self._segment(action_id, "action", f"{action.get('label', action_id)}. {consequence}"))
        fallback = str(sem.get("recovery") or "The essential outcome remains available as tactile text.")
        return BrailleSemanticExpression(str(sem["experience_id"]), str(sem["outcome"]), segments, action_ids, required_ids, fallback)

    def _segment(self, semantic_id: str, kind: str, text: str) -> BrailleSegment:
        return BrailleSegment(semantic_id, kind, text, self.translator.text_to_cells(text))

