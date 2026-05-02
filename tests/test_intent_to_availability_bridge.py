from __future__ import annotations

from integration.intent_to_availability_state import global_state_from_intent_repo


def test_bridge_complete_maps_specialization_date_time() -> None:
    state = {
        "user_input": "Book cardiology tomorrow morning",
        "intent": {
            "status": "complete",
            "intent": {
                "specialization": "Cardiology",
                "date": "2026-05-02",
                "time_preference": "morning",
            },
        },
    }
    g = global_state_from_intent_repo(state)
    assert g["intent"]["specialty"] == "cardiology"
    assert g["intent"]["preferred_date"] == "2026-05-02"
    assert g["intent"]["preferred_time_window"] == "morning"


def test_bridge_incomplete_maps_missing_fields() -> None:
    state = {
        "user_input": "x",
        "intent": {"status": "incomplete", "missing_fields": ["date", "specialization"]},
    }
    g = global_state_from_intent_repo(state)
    assert "intent.preferred_date" in g["missing_fields"]
    assert "intent.specialty" in g["missing_fields"]
