import pytest

from unison_io_braille import BrailleSemanticComposer


def test_braille_composes_semantic_navigation_without_visual_focus():
    sem = {
        "schema_version": "sem.v1", "experience_id": "bill", "outcome": "Bill increased by 18 dollars",
        "nodes": [{"node_id": "cause", "kind": "trend", "label": "Heating", "summary": "Weekday heating increased", "required": True}],
        "actions": [{"action_id": "review", "label": "Review days", "consequence": "Shows daily usage"}],
        "recovery": "Return to the bill summary",
    }
    expression = BrailleSemanticComposer().compose(sem)
    assert expression.required_node_ids == ["cause"]
    assert expression.action_ids == ["review"]
    assert expression.go_to("cause").text == "Weekday heating increased"
    assert expression.move(1).semantic_id == "review"
    assert expression.fallback == "Return to the bill summary"


def test_braille_composer_fails_with_explicit_fallback_boundary():
    with pytest.raises(ValueError, match="invalid semantic experience"):
        BrailleSemanticComposer().compose({"schema_version": "sem.v1"})
