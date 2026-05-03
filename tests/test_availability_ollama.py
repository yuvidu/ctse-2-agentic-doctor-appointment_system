"""Availability + optional Ollama ranking (mocked)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from agents.availability_agent import availability_agent
from schemas.state import GlobalState

from tests.schedule_date_helpers import preferred_date_on_or_after_today


def _schedules() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample_schedules.json"


def test_ollama_reorders_slots_when_flag_on(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AVAILABILITY_USE_OLLAMA", "1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    tz = ZoneInfo("Asia/Colombo")
    day = (datetime.now(tz) + timedelta(days=1)).date().isoformat()
    sched = tmp_path / "two_slots.json"
    sched.write_text(
        json.dumps(
            {
                "doctors": [
                    {
                        "doctor_id": "D001",
                        "name": "Dr. Silva",
                        "specialty": "cardiology",
                        "location": "Clinic A",
                        "slots": [
                            {
                                "start": f"{day}T10:00:00+05:30",
                                "end": f"{day}T10:30:00+05:30",
                            },
                            {
                                "start": f"{day}T14:00:00+05:30",
                                "end": f"{day}T14:30:00+05:30",
                            },
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    state: GlobalState = {
        "user_input": "I prefer something after lunch if possible.",
        "intent": {
            "specialty": "cardiology",
            "preferred_date": day,
            "preferred_time_window": "any",
        },
    }
    with patch(
        "agents.availability_agent.rank_slots_with_ollama",
        return_value=([1, 0], "Afternoon fits the preference better.", '{"x":1}'),
    ):
        out = availability_agent(state, schedules_path=sched)
    assert out["status"] == "availability_ok"
    slots = out["availability"]["available_slots"]
    assert len(slots) == 2
    assert "14:00" in slots[0]["start"]
    rank = out["availability"].get("ollama_ranking") or {}
    assert rank.get("recommended_slot_indices") == [1, 0]
    assert "Afternoon" in (rank.get("rationale") or "")


def test_ollama_skipped_does_not_break_when_flag_off() -> None:
    sched = _schedules()
    date_iso = preferred_date_on_or_after_today(sched, specialty="cardiology", morning_only=True)
    state: GlobalState = {
        "intent": {
            "specialty": "cardiology",
            "preferred_date": date_iso,
            "preferred_time_window": "morning",
        }
    }
    out = availability_agent(state, schedules_path=sched)
    assert out["status"] == "availability_ok"
    assert out["availability"].get("ollama_ranking") is None
