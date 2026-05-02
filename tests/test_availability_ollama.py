"""Availability + optional Ollama ranking (mocked)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agents.availability_agent import availability_agent
from schemas.state import GlobalState


def _schedules() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample_schedules.json"


def test_ollama_reorders_slots_when_flag_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AVAILABILITY_USE_OLLAMA", "1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    state: GlobalState = {
        "user_input": "I prefer something after lunch if possible.",
        "intent": {
            "specialty": "cardiology",
            "preferred_date": "2026-05-02",
            "preferred_time_window": "any",
        },
    }
    with patch(
        "agents.availability_agent.rank_slots_with_ollama",
        return_value=([1, 0], "Afternoon fits the preference better.", '{"x":1}'),
    ):
        out = availability_agent(state, schedules_path=_schedules())
    assert out["status"] == "availability_ok"
    slots = out["availability"]["available_slots"]
    assert len(slots) == 2
    assert "14:00" in slots[0]["start"]
    rank = out["availability"].get("ollama_ranking") or {}
    assert rank.get("recommended_slot_indices") == [1, 0]
    assert "Afternoon" in (rank.get("rationale") or "")


def test_ollama_skipped_does_not_break_when_flag_off() -> None:
    state: GlobalState = {
        "intent": {
            "specialty": "cardiology",
            "preferred_date": "2026-05-02",
            "preferred_time_window": "morning",
        }
    }
    out = availability_agent(state, schedules_path=_schedules())
    assert out["status"] == "availability_ok"
    assert out["availability"].get("ollama_ranking") is None
