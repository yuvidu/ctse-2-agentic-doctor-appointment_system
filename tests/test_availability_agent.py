from __future__ import annotations

from pathlib import Path

import pytest

from agents.availability_agent import availability_agent
from schemas.state import GlobalState


@pytest.fixture
def schedules_file() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample_schedules.json"


def test_valid_cardiology_morning(schedules_file: Path) -> None:
    state: GlobalState = {
        "intent": {
            "specialty": "cardiology",
            "preferred_date": "2026-05-02",
            "preferred_time_window": "morning",
        }
    }
    out = availability_agent(state, schedules_path=schedules_file)
    assert out["status"] == "availability_ok"
    assert out.get("availability") is not None
    slots = out["availability"]["available_slots"]
    assert len(slots) >= 1
    assert all(s["doctor_id"] == "D001" for s in slots)
    assert all("10:00" in s["start"] for s in slots)


def test_missing_preferred_date(schedules_file: Path) -> None:
    state: GlobalState = {"intent": {"specialty": "cardiology"}}
    out = availability_agent(state, schedules_path=schedules_file)
    assert out["status"] == "availability_missing_input"
    assert "intent.preferred_date" in (out.get("missing_fields") or [])


def test_invalid_doctor_id_rejected(schedules_file: Path) -> None:
    state: GlobalState = {
        "intent": {
            "doctor_id": "D001;DROP--",
            "preferred_date": "2026-05-02",
        }
    }
    out = availability_agent(state, schedules_path=schedules_file)
    assert out["status"] == "availability_failed"
    errs = out.get("errors") or []
    assert any(e.get("code") == "AVAILABILITY_TOOL_ERROR" for e in errs)


def test_empty_slots_future_day(schedules_file: Path) -> None:
    state: GlobalState = {
        "intent": {
            "specialty": "cardiology",
            "preferred_date": "2099-01-01",
        }
    }
    out = availability_agent(state, schedules_path=schedules_file)
    assert out["status"] == "availability_empty"
    assert out.get("availability", {}).get("total_count") == 0


def test_corrupt_schedules_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    state: GlobalState = {
        "intent": {"specialty": "cardiology", "preferred_date": "2026-05-02"}
    }
    out = availability_agent(state, schedules_path=bad)
    assert out["status"] == "availability_failed"


def test_tool_direct_invalid_window(schedules_file: Path) -> None:
    from tools.availability_tools.schedule_availability import fetch_doctor_availability

    with pytest.raises(ValueError):
        fetch_doctor_availability(
            schedules_path=schedules_file,
            specialty="cardiology",
            preferred_date="2026-05-02",
            preferred_time_window="night",
        )
